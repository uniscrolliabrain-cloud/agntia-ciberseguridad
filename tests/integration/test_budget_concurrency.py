from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import unittest
from pydantic import ValidationError
from tests.support import Fixture
from agntia_ciberseguridad.billing.rates import Rate, BudgetPolicy, CAPS
from agntia_ciberseguridad.billing.reservations import Ledger, ReservationRequest, Settlement
from agntia_ciberseguridad.events.outbox import Outbox, Ack, SyntheticConsumer
from agntia_ciberseguridad.errors import DomainError

class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.f=Fixture(); self.actor=self.f.service.auth.authenticate(self.f.headers('reviewerA')['Authorization'])
        self.rate=Rate(version='fixture-v1',provider_ref='synthetic',source_ref='fixture-price',reviewed_by_ref='human-review',valid_until='2099-12-31',unit_price_minor='1000',hard_limit_verified=True,commercial_use_review_ref='fixture-not-a-service')
        self.f.settings.budget_policies={'tenantA':BudgetPolicy(plan='Lite',allocation_review_ref='fixture-shared-cost',rates={'fixture':self.rate})}
        self.clock=[datetime(2026,11,11,tzinfo=timezone.utc)]
        self.ledger=Ledger(self.f.service,clock=lambda:self.clock[0])
    def tearDown(self):self.f.service.telemetry.close();self.f.close()
    def reserve(self,key='fixture-key-001',units=1):return self.ledger.reserve(self.actor,'tenantA',ReservationRequest(rate_ref='fixture',units=units,operation_key=key),'synthetic')
    def test_atomic_distinct_reservations_cannot_overspend_and_restart_replay(self):
        def reserve(i):
            try:return self.reserve('fixture-key-'+str(i),2)['id']
            except DomainError as e:return e.code
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(reserve,range(2)))
        self.assertEqual(results.count('budget_exhausted'),1)
        self.assertEqual(self.ledger.summary(self.actor,'tenantA')['reserved_cents'],2000)
        with ThreadPoolExecutor(max_workers=2) as pool:same=list(pool.map(lambda _:self.reserve(),range(2)))
        self.assertEqual(same[0]['id'],same[1]['id']);self.assertEqual(sum(not r['replayed'] for r in same),1)
        self.assertTrue(Ledger(self.f.service,clock=lambda:self.clock[0]).reserve(self.actor,'tenantA',ReservationRequest(rate_ref='fixture',units=1,operation_key='fixture-key-001'),'restart')['replayed'])
        with self.assertRaises(DomainError) as e:self.reserve(units=2)
        self.assertEqual(e.exception.code,'idempotency_conflict')
    def test_unknown_keeps_money_cancel_only_before_start_and_late_invoice_freezes(self):
        r=self.reserve();r=self.ledger.transition(self.actor,'tenantA',r['id'],0,'start','fixture')
        with self.assertRaises(DomainError):self.ledger.transition(self.actor,'tenantA',r['id'],1,'cancel','fixture')
        r=self.ledger.transition(self.actor,'tenantA',r['id'],1,'uncertain','fixture')
        self.assertEqual(self.ledger.summary(self.actor,'tenantA')['reserved_cents'],1000)
        body=Settlement(expected_revision=2,actual_cents=3500,invoice_ref='late-invoice')
        settled=self.ledger.settle(self.actor,'tenantA',r['id'],body,'fixture')
        self.assertEqual(settled['state'],'overrun');self.assertEqual(self.ledger.settle(self.actor,'tenantA',r['id'],body,'replay'),settled)
        summary=self.ledger.summary(self.actor,'tenantA');self.assertEqual(summary['spent_cents'],3500);self.assertEqual(summary['overrun_cents'],500)
        self.assertEqual(summary['status'],'frozen');self.assertFalse(summary['security_controls_degraded'])
        with self.assertRaises(DomainError):self.reserve('fixture-after-freeze')
    def test_unused_release_and_invoice_after_release_record_liability(self):
        r=self.reserve();self.ledger.transition(self.actor,'tenantA',r['id'],0,'cancel','fixture')
        self.assertEqual(self.ledger.summary(self.actor,'tenantA')['reserved_cents'],0)
        self.ledger.settle(self.actor,'tenantA',r['id'],Settlement(expected_revision=1,actual_cents=100,invoice_ref='late-small'),'fixture')
        self.assertEqual(self.ledger.summary(self.actor,'tenantA')['spent_cents'],100)
    def test_tax_fx_minimum_rounding_source_limits_and_finite_input(self):
        rate=self.rate.model_copy(update={'currency':'USD','unit_price_minor':'0.1','minimum_minor':'10','fx_to_eur':'0.93','tax_basis_points':2100})
        self.assertEqual(rate.worst_case(1),12)
        self.f.settings.budget_policies['tenantA'].rates['fixture']=self.rate.model_copy(update={'hard_limit_verified':False})
        with self.assertRaises(DomainError) as e:self.reserve()
        self.assertEqual(e.exception.code,'unbounded_cost')
        for bad in ['NaN','Infinity','-1','1e99']:
            with self.assertRaises(ValidationError):Rate(**{**self.rate.model_dump(),'unit_price_minor':bad})
        with self.assertRaises(ValidationError):ReservationRequest(rate_ref='fixture',units=True,operation_key='fixture-key')
    def test_server_policy_changed_month_boundary_and_cross_tenant(self):
        r=self.reserve();self.clock[0]=datetime(2026,12,1,tzinfo=timezone.utc)
        with self.assertRaises(DomainError):self.ledger.transition(self.actor,'tenantA',r['id'],0,'start','fixture')
        self.assertEqual(self.ledger.summary(self.actor,'tenantA')['reserved_cents'],0)
        # A November liability stays in November.
        self.ledger.settle(self.actor,'tenantA',r['id'],Settlement(expected_revision=0,actual_cents=800,invoice_ref='november'),'fixture')
        self.assertEqual(self.ledger.summary(self.actor,'tenantA')['spent_cents'],0)
        self.reserve('december-key');self.f.settings.budget_policies['tenantA'].fixed_commitment_cents=100
        self.assertEqual(self.ledger.summary(self.actor,'tenantA')['status'],'policy_changed')
        with self.assertRaises(DomainError):self.reserve('changed-policy-key')
        foreign=self.f.service.auth.authenticate(self.f.headers('reviewerB')['Authorization'])
        with self.assertRaises(DomainError) as e:self.ledger.summary(foreign,'tenantA')
        self.assertEqual(e.exception.status,404)
        with self.assertRaises(DomainError):self.ledger.reserve(self.f.service.auth.authenticate(self.f.headers('viewerA')['Authorization']),'tenantA',ReservationRequest(rate_ref='fixture',units=1,operation_key='viewer-key'),'fixture')
    def test_cap_config_matches_plans_and_fixed_commitments(self):
        import json
        plans=json.loads((Path(__file__).resolve().parents[2]/'config/plans.json').read_text())['plans']
        self.assertEqual(CAPS,{p:v['monthly_cap_eur']*100 for p,v in plans.items()})
        self.f.settings.budget_policies['tenantA'].fixed_commitment_cents=2500
        with self.assertRaises(DomainError) as e:self.reserve()
        self.assertEqual(e.exception.code,'budget_exhausted')
    def test_transaction_rollback_preserves_balance_audit_outbox(self):
        from unittest.mock import patch
        with patch.object(self.f.service.db,'audit',side_effect=RuntimeError('synthetic-audit-failure')):
            with self.assertRaises(RuntimeError):self.reserve()
        self.assertEqual(self.ledger.summary(self.actor,'tenantA')['reserved_cents'],0)
        with self.f.service.db.connection(readonly=True) as db:self.assertEqual(db.execute('SELECT count(*) FROM integration_outbox').fetchone()[0],0)
    def test_transactional_outbox_durable_consumer_replay_and_ack_scope(self):
        self.reserve();outbox=Outbox(self.f.service);item=outbox.poll(self.actor,'tenantA','synthetic-consumer')['events'][0]
        consumer=SyntheticConsumer(self.f.root/'consumer.sqlite3');self.assertTrue(consumer.consume(item))
        self.assertFalse(SyntheticConsumer(self.f.root/'consumer.sqlite3').consume(item))
        self.assertEqual(len(outbox.poll(self.actor,'tenantA','synthetic-consumer')['events']),1)
        ack=Ack(consumer_id='synthetic-consumer',content_hash=item['content_hash'])
        self.assertFalse(outbox.ack(self.actor,'tenantA',item['envelope']['id'],ack,'fixture')['duplicate'])
        self.assertTrue(outbox.ack(self.actor,'tenantA',item['envelope']['id'],ack,'fixture')['duplicate'])
        self.assertEqual(outbox.poll(self.actor,'tenantA','synthetic-consumer')['events'],[])
        self.assertEqual(len(outbox.poll(self.actor,'tenantA','another-consumer')['events']),1)
        with self.assertRaises(DomainError):outbox.ack(self.actor,'tenantA',item['envelope']['id'],ack.model_copy(update={'content_hash':'0'*64}),'fixture')
        with self.f.service.db.connection(readonly=True) as db:self.assertTrue(self.f.service.db.verify_audit(db,'tenantA')['valid'])
