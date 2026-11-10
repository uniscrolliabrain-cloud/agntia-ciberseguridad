"""Encrypted originals and minimized views, explicit custody/retention, no plaintext fallback."""
import base64
from datetime import datetime,timedelta
import hashlib
import json
import os
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from ..auth import require_human
from ..errors import reject,not_found,DomainError
from ..util import canonical,digest,now,uid,utcnow
from .redaction import redact

MAX_BYTES=2*1024*1024

class Vault:
    def __init__(self,service,*,clock=utcnow):
        self.service=service;self.db=service.db;self.clock=clock
        self.root=service.settings.data_dir.resolve()/'evidence'
        self.root.mkdir(parents=True,exist_ok=True,mode=0o700)

    def _policy(self,tenant):
        policy=self.service.settings.evidence_policies.get(tenant)
        if not policy:reject('evidence_unconfigured','Custodia y clave no configuradas',424)
        return policy

    def _key(self,tenant,reference):
        policy=self._policy(tenant)
        if reference not in policy.key_refs:reject('evidence_key_unavailable','Referencia de clave no disponible',424)
        try:
            key=base64.b64decode(os.getenv(reference,''),validate=True)
            if len(key)!=32:raise ValueError()
            return key
        except (ValueError,TypeError):reject('evidence_key_unavailable','Clave de custodia no disponible',424)

    @staticmethod
    def _row(db,tenant,evidence_id):
        row=db.execute('SELECT body FROM evidence WHERE tenant_id=? AND id=?',(tenant,evidence_id)).fetchone()
        if not row:not_found()
        return json.loads(row['body'])

    @staticmethod
    def public(meta):
        keys=('id','tenant_id','source_job_id','media_type','classification','created_at','expires_at','legal_hold',
              'revision','state','redaction_status','redacted_sha256','redacted_bytes','custodian_ref','legal_basis_ref')
        return {key:meta[key] for key in keys}

    def _file(self,meta,variant):
        return self.root/meta['tenant_id']/(meta['id']+'-'+variant+'.enc')

    @staticmethod
    def _aad(meta,variant):
        return canonical({'schema_version':1,'tenant_id':meta['tenant_id'],'id':meta['id'],
                          'variant':variant,'envelope':meta['envelope']}).encode()

    def put(self,actor,tenant,content,media_type,correlation,*,source_job_id=None):
        with self.service.telemetry.span('evidence.write',component='evidence',correlation_id=correlation):
            return self._put(actor,tenant,content,media_type,correlation,source_job_id=source_job_id)

    def _put(self,actor,tenant,content,media_type,correlation,*,source_job_id=None):
        self.service.authorize(actor,tenant,'evidence.create')
        if not isinstance(content,bytes) or not content or len(content)>MAX_BYTES:reject('evidence_size','Tamaño de evidencia inválido',422)
        if media_type not in ('text/plain','application/json','application/pdf'):reject('evidence_type','Tipo no soportado',422)
        if media_type=='application/pdf' and not content.startswith(b'%PDF-'):reject('evidence_type','Firma de archivo no corresponde',422)
        policy=self._policy(tenant);key_ref=policy.key_refs[0];key=self._key(tenant,key_ref)
        try:view,redaction_status=redact(content,media_type)
        except (ValueError,UnicodeError):reject('evidence_invalid','Contenido no admitido',422)
        if len(view)>MAX_BYTES*2:reject('evidence_size','Vista redactada excede el límite',422)
        evidence_id=uid();instant=self.clock()
        meta={'schema_version':1,'id':evidence_id,'tenant_id':tenant,'source_job_id':source_job_id,
              'media_type':media_type,'classification':'confidential','created_by':actor.actor_id,
              'created_at':instant.isoformat(),'expires_at':(instant+timedelta(days=policy.retention_days)).isoformat(),
              'legal_hold':False,'revision':0,'state':'quarantined' if media_type=='application/pdf' else 'unreviewed',
              'redaction_status':redaction_status,'redacted_sha256':hashlib.sha256(view).hexdigest(),
              'redacted_bytes':len(view),'custodian_ref':policy.custodian_ref,'legal_basis_ref':policy.legal_basis_ref,
              'key_ref':key_ref,'original_sha256':hashlib.sha256(content).hexdigest(),'original_bytes':len(content)}
        meta['envelope']={'media_type':media_type,'original_sha256':meta['original_sha256'],
                          'redacted_sha256':meta['redacted_sha256'],'key_ref':key_ref,'policy_hash':digest(policy.model_dump(mode='json'))}
        folder=self.root/tenant;folder.mkdir(mode=0o700,exist_ok=True)
        written=[]
        try:
            for variant,payload in (('original',content),('redacted',view)):
                nonce=os.urandom(12);encrypted=nonce+AESGCM(key).encrypt(nonce,payload,self._aad(meta,variant))
                file=self._file(meta,variant)
                with file.open('xb') as target:target.write(encrypted);target.flush();os.fsync(target.fileno())
                file.chmod(0o400);written.append(file)
            with self.db.transaction() as db:
                self.service.auth.authorize(actor,tenant,'evidence.create')
                if source_job_id:
                    if not db.execute('SELECT 1 FROM jobs WHERE tenant_id=? AND id=?',(tenant,source_job_id)).fetchone():not_found()
                db.execute('INSERT INTO evidence VALUES(?,?,?,?,?)',(tenant,evidence_id,source_job_id,canonical(meta),0))
                self.db.audit(db,tenant,actor.actor_id,'evidence.created',evidence_id,correlation,
                              {'evidence_id':evidence_id,'redacted_sha256':meta['redacted_sha256'],'state':meta['state']})
            return self.public(meta)
        except Exception:
            for file in written:file.unlink(missing_ok=True)
            raise

    def metadata(self,actor,tenant,evidence_id):
        self.service.authorize(actor,tenant,'evidence.read')
        with self.db.connection(readonly=True) as db:return self.public(self._row(db,tenant,evidence_id))

    def read(self,actor,tenant,evidence_id,correlation,*,original=False,reason=None):
        with self.service.telemetry.span('evidence.read',component='evidence',correlation_id=correlation):
            return self._read(actor,tenant,evidence_id,correlation,original=original,reason=reason)

    def _read(self,actor,tenant,evidence_id,correlation,*,original=False,reason=None):
        if original:
            require_human(self.service,actor,tenant,'evidence.original')
            if not isinstance(reason,str) or not 5<=len(reason)<=500:reject('evidence_purpose','Motivo de acceso requerido',422)
        else:self.service.authorize(actor,tenant,'evidence.read')
        with self.db.connection(readonly=True) as db:meta=self._row(db,tenant,evidence_id)
        if meta['state'] in ('deleted','purge_pending'):reject('evidence_unavailable','Evidencia no disponible',410)
        if not meta['legal_hold'] and datetime.fromisoformat(meta['expires_at'])<=self.clock():reject('evidence_expired','Evidencia fuera de retención',410)
        with self.db.transaction() as db:
            self.db.audit(db,tenant,actor.actor_id,'evidence.read_requested',evidence_id,correlation,{'evidence_id':evidence_id,'variant':'original' if original else 'redacted'})
        variant='original' if original else 'redacted';key=self._key(tenant,meta['key_ref']);file=self._file(meta,variant)
        try:
            if file.is_symlink() or file.stat().st_size>MAX_BYTES*2+64:raise ValueError()
            encrypted=file.read_bytes()
            plain=AESGCM(key).decrypt(encrypted[:12],encrypted[12:],self._aad(meta,variant))
            if len(plain)!=meta[variant+'_bytes'] or hashlib.sha256(plain).hexdigest()!=meta[variant+'_sha256']:raise ValueError()
        except Exception:reject('evidence_integrity','No se pudo verificar la evidencia',409)
        with self.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'evidence.original' if original else 'evidence.read')
            current=self._row(db,tenant,evidence_id)
            if current['state'] in ('deleted','purge_pending'):reject('evidence_unavailable','Evidencia no disponible',410)
            self.db.audit(db,tenant,actor.actor_id,'evidence.accessed',evidence_id,correlation,
                          {'evidence_id':evidence_id,'variant':variant,'purpose_hash':digest(reason) if original else None})
        return plain

    def manage(self,actor,tenant,evidence_id,expected_revision,action,correlation,*,enabled=False,reason=''):
        require_human(self.service,actor,tenant,'evidence.review' if action=='review' else 'evidence.manage')
        if action not in ('review','hold','purge') or not 5<=len(reason)<=500:reject('validation','Acción o motivo inválidos',422)
        with self.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'evidence.review' if action=='review' else 'evidence.manage')
            meta=self._row(db,tenant,evidence_id)
            if meta['revision']!=expected_revision:reject('conflict','Revisión de evidencia modificada',409)
            if meta['state'] in ('deleted','purge_pending'):reject('conflict','Estado de evidencia no admite cambio',409)
            if action=='review':
                if actor.actor_id==meta['created_by']:reject('separation_of_duties','Otro humano debe revisar',403)
                if meta['state']=='quarantined':reject('quarantine','Revisión de malware no disponible para este PDF',424)
                meta.update(state='reviewed',reviewed_by=actor.actor_id,reviewed_at=now())
            elif action=='hold':meta['legal_hold']=bool(enabled)
            else:
                if meta['legal_hold'] or datetime.fromisoformat(meta['expires_at'])>self.clock():reject('retention','Retención o legal hold impide purga',409)
                meta['state']='purge_pending'
            meta['revision']+=1
            db.execute('UPDATE evidence SET body=?,revision=? WHERE tenant_id=? AND id=?',(canonical(meta),meta['revision'],tenant,evidence_id))
            self.db.audit(db,tenant,actor.actor_id,'evidence.'+action,evidence_id,correlation,{'evidence_id':evidence_id,'revision':meta['revision'],'reason_hash':digest(reason)})
        if action=='purge':
            for variant in ('original','redacted'):self._file(meta,variant).unlink(missing_ok=True)
            with self.db.transaction() as db:
                self.service.auth.authorize(actor,tenant,'evidence.manage')
                current=self._row(db,tenant,evidence_id)
                if current['state']!='purge_pending':reject('conflict','Purga requiere conciliación',409)
                current['state']='deleted';current['revision']+=1
                db.execute('UPDATE evidence SET body=?,revision=? WHERE tenant_id=? AND id=?',(canonical(current),current['revision'],tenant,evidence_id))
                self.db.audit(db,tenant,actor.actor_id,'evidence.purged',evidence_id,correlation,{'evidence_id':evidence_id})
                meta=current
        return self.public(meta)
