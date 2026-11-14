"""Durable admission before optional metered work; unknown outcomes retain their funds."""
import json
from pydantic import Field, StrictInt
from ..auth import require_human
from ..contracts import Model, OpaqueId
from ..errors import reject, not_found
from ..util import canonical, digest, now, uid, utcnow
from .rates import CAPS

class ReservationRequest(Model):
    rate_ref: OpaqueId
    units: StrictInt = Field(ge=1, le=1000000)
    operation_key: str = Field(pattern=r'^[A-Za-z0-9_-]{8,100}$')

class Settlement(Model):
    expected_revision: StrictInt = Field(ge=0)
    actual_cents: StrictInt = Field(ge=0, le=100000000)
    invoice_ref: OpaqueId

class Ledger:
    def __init__(self, service, *, clock=utcnow):
        self.service=service; self.db=service.db; self.clock=clock
    def _policy(self, tenant):
        policy=self.service.settings.budget_policies.get(tenant)
        if not policy: reject('budget_unconfigured','Presupuesto no configurado',424)
        return policy
    def _account(self, db, tenant, period):
        policy=self._policy(tenant); ph=digest(policy.model_dump(mode='json'))
        row=db.execute('SELECT * FROM budget_accounts WHERE tenant_id=? AND period=?',(tenant,period)).fetchone()
        if row and row['policy_hash']!=ph: reject('budget_policy_changed','Conciliar política del periodo antes de continuar',409)
        if not row:
            db.execute('INSERT INTO budget_accounts(tenant_id,period,policy_hash,cap_cents,fixed_cents,margin_cents) VALUES(?,?,?,?,?,?)',
                (tenant,period,ph,CAPS[policy.plan],policy.fixed_commitment_cents,policy.reserve_margin_cents))
            row=db.execute('SELECT * FROM budget_accounts WHERE tenant_id=? AND period=?',(tenant,period)).fetchone()
        return row
    @staticmethod
    def _reserved(db, tenant, period):
        return db.execute("SELECT coalesce(sum(amount_cents),0) FROM cost_reservations WHERE tenant_id=? AND period=? AND state IN ('reserved','started','reconciliation_required')",(tenant,period)).fetchone()[0]
    @staticmethod
    def _row(db,tenant,rid):
        row=db.execute('SELECT * FROM cost_reservations WHERE tenant_id=? AND id=?',(tenant,rid)).fetchone()
        if not row: not_found()
        return dict(row)
    @staticmethod
    def public(row):
        return {k:row[k] for k in ('id','period','amount_cents','actual_cents','state','revision')}
    def summary(self,actor,tenant):
        self.service.authorize(actor,tenant,'budget.read')
        policy=self.service.settings.budget_policies.get(tenant)
        if not policy: return {'tenant_id':tenant,'status':'not_configured','currency':'EUR','security_controls_degraded':False}
        period=self.clock().strftime('%Y-%m')
        with self.db.connection(readonly=True) as db:
            row=db.execute('SELECT * FROM budget_accounts WHERE tenant_id=? AND period=?',(tenant,period)).fetchone()
            reserved=self._reserved(db,tenant,period)
        cap=row['cap_cents'] if row else CAPS[policy.plan]
        fixed=row['fixed_cents'] if row else policy.fixed_commitment_cents
        margin=row['margin_cents'] if row else policy.reserve_margin_cents
        spent=row['spent_cents'] if row else 0
        available=cap-fixed-margin-spent-reserved
        changed=bool(row and row['policy_hash']!=digest(policy.model_dump(mode='json')))
        status='policy_changed' if changed else 'frozen' if row and row['frozen'] else 'exhausted' if available<=0 else 'warning' if available*5<cap else 'available'
        return {'tenant_id':tenant,'period':period,'currency':'EUR','cap_cents':cap,'fixed_commitment_cents':fixed,
            'reserve_margin_cents':margin,'spent_cents':spent,'reserved_cents':reserved,'available_cents':max(0,available),
            'overrun_cents':max(0,-available),'status':status,'security_controls_degraded':False,
            'unit':'one tenant/workspace, UTC calendar month','provider_billing_connected':False}
    def reserve(self,actor,tenant,body,correlation):
        require_human(self.service,actor,tenant,'budget.manage')
        # This campaign provides a metering primitive, not permission to call a provider.
        policy=self._policy(tenant); rate=policy.rates.get(body.rate_ref)
        if not rate: reject('rate_unavailable','Tarifa no aprobada',424)
        if rate.valid_until < self.clock().date().isoformat(): reject('rate_stale','Tarifa caducada',424)
        if not rate.hard_limit_verified and rate.uncertainty_margin_cents<=0:
            reject('unbounded_cost','Sin límite fiable ni margen revisado',424)
        amount=rate.worst_case(body.units); period=self.clock().strftime('%Y-%m')
        request_hash=digest({'request':body.model_dump(),'rate_hash':rate.content_hash,'binding_id':actor.binding_id})
        with self.db.transaction() as db:
            require_human(self.service,actor,tenant,'budget.manage')
            old=db.execute('SELECT * FROM cost_reservations WHERE tenant_id=? AND operation_key=?',(tenant,body.operation_key)).fetchone()
            if old:
                if old['request_hash']!=request_hash: reject('idempotency_conflict','Clave ligada a otra propuesta',409)
                return {**self.public(dict(old)),'replayed':True}
            account=self._account(db,tenant,period)
            if account['frozen']: reject('budget_frozen','Presupuesto bloqueado para conciliación',409)
            if account['fixed_cents']+account['margin_cents']+account['spent_cents']+self._reserved(db,tenant,period)+amount>account['cap_cents']:
                reject('budget_exhausted','Saldo insuficiente; sin ampliación automática',429)
            if db.execute('SELECT count(*) FROM cost_reservations WHERE tenant_id=?',(tenant,)).fetchone()[0]>=10000:
                reject('budget_capacity','Conciliar archivo del ledger antes de admitir',429)
            rid=uid(); payload={'rate':rate.model_dump(mode='json'),'rate_hash':rate.content_hash,'units':body.units,'created_at':now()}
            db.execute('INSERT INTO cost_reservations(tenant_id,period,id,operation_key,request_hash,amount_cents,state,body) VALUES(?,?,?,?,?,?,?,?)',
                (tenant,period,rid,body.operation_key,request_hash,amount,'reserved',canonical(payload)))
            self.db.audit(db,tenant,actor.actor_id,'budget.reserved',rid,correlation,{'amount_cents':amount,'rate_hash':rate.content_hash})
            return {**self.public(self._row(db,tenant,rid)),'replayed':False}
    def transition(self,actor,tenant,rid,revision,action,correlation):
        require_human(self.service,actor,tenant,'budget.manage')
        if action not in ('start','cancel','uncertain'): reject('validation','Acción de reserva inválida',422)
        with self.db.transaction() as db:
            require_human(self.service,actor,tenant,'budget.manage'); row=self._row(db,tenant,rid)
            if row['revision']!=revision: reject('conflict','Revisión modificada',409)
            permitted={'start':{'reserved'},'cancel':{'reserved'},'uncertain':{'started'}}
            if row['state'] not in permitted[action]: reject('conflict','Estado no admite la transición',409)
            state={'start':'started','cancel':'released','uncertain':'reconciliation_required'}[action]
            if action=='start':
                account=self._account(db,tenant,row['period'])
                rate=json.loads(row['body'])['rate']
                if account['frozen'] or row['period']!=self.clock().strftime('%Y-%m') or rate['valid_until']<self.clock().date().isoformat():
                    reject('budget_frozen','Reserva no ejecutable; revisar periodo/tarifa',409)
            db.execute('UPDATE cost_reservations SET state=?,revision=revision+1 WHERE tenant_id=? AND id=?',(state,tenant,rid))
            self.db.audit(db,tenant,actor.actor_id,'budget.'+state,rid,correlation,{'revision':revision+1})
            return self.public(self._row(db,tenant,rid))
    def settle(self,actor,tenant,rid,body,correlation):
        require_human(self.service,actor,tenant,'budget.manage')
        with self.db.transaction() as db:
            require_human(self.service,actor,tenant,'budget.manage'); row=self._row(db,tenant,rid); payload=json.loads(row['body'])
            receipt=digest(body.model_dump())
            if row['state'] in ('settled','overrun'):
                if payload.get('settlement_hash')!=receipt: reject('idempotency_conflict','Conciliación distinta',409)
                return self.public(row)
            if row['revision']!=body.expected_revision: reject('conflict','Revisión modificada',409)
            # A late invoice is a liability even if an unused reservation was released.
            account=db.execute('SELECT * FROM budget_accounts WHERE tenant_id=? AND period=?',(tenant,row['period'])).fetchone()
            reserved=self._reserved(db,tenant,row['period'])-(row['amount_cents'] if row['state'] in ('reserved','started','reconciliation_required') else 0)
            total=account['fixed_cents']+account['margin_cents']+account['spent_cents']+body.actual_cents+reserved
            overrun=body.actual_cents>row['amount_cents'] or total>account['cap_cents']
            payload.update(settlement_hash=receipt,invoice_ref=body.invoice_ref,settled_at=now())
            state='overrun' if overrun else 'settled'
            db.execute('UPDATE budget_accounts SET spent_cents=spent_cents+?,frozen=max(frozen,?) WHERE tenant_id=? AND period=?',(body.actual_cents,int(overrun),tenant,row['period']))
            db.execute('UPDATE cost_reservations SET state=?,actual_cents=?,revision=revision+1,body=? WHERE tenant_id=? AND id=?',(state,body.actual_cents,canonical(payload),tenant,rid))
            self.db.audit(db,tenant,actor.actor_id,'budget.'+state,rid,correlation,{'actual_cents':body.actual_cents,'invoice_hash':digest(body.invoice_ref)})
            return self.public(self._row(db,tenant,rid))
