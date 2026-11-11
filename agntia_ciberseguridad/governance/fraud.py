"""Offline signal analysis only; message-supplied links/channels are never trusted verification."""
from email.utils import parseaddr,getaddresses
import hashlib
import unicodedata
from urllib.parse import urlsplit
from typing import Literal
from pydantic import Field,field_validator,StrictInt
from .store import Cases
from ..auth import require_human
from ..contracts import Model,OpaqueId,ResourceId,Hash
from ..evidence.vault import Vault
from ..errors import reject
from ..util import digest

class FraudObservation(Model):
    sender: str=Field(min_length=3,max_length=320)
    reply_to: str|None=Field(default=None,max_length=320)
    claimed_url: str|None=Field(default=None,max_length=2048)
    new_payment_destination_claimed: bool=False
    authentication_results_claim: Literal['not_provided','pass','fail']='not_provided'
    evidence_ref: OpaqueId
    @field_validator('sender','reply_to','claimed_url')
    @classmethod
    def no_controls(cls,value):
        if value and any(ord(c)<32 or ord(c)==127 for c in value):raise ValueError('Control characters rejected')
        return value
class FraudVerification(Model):
    expected_revision: StrictInt=Field(ge=0)
    record_hash: Hash
    channel_ref: OpaqueId
    evidence_id: ResourceId
    decision: Literal['human_attested_verified','cannot_verify','suspicion_unresolved']

class Fraud:
    def __init__(self,service):self.service=service;self.cases=Cases(service)
    @staticmethod
    def domain(value):
        scripts={unicodedata.name(c,'').split(' ')[0] for c in value if c.isalpha()}
        try:
            ascii_domain=value.encode('idna').decode().lower().rstrip('.')
            if not ascii_domain or len(ascii_domain)>253 or any(not x or len(x)>63 or x.startswith('-') or x.endswith('-') or not all(c.isalnum() or c=='-' for c in x) for x in ascii_domain.split('.')):raise ValueError()
        except UnicodeError:raise ValueError('Invalid domain') from None
        return ascii_domain,len(scripts)>1,ascii_domain!=value.lower().rstrip('.')
    @classmethod
    def email_domain(cls,value):
        addresses=getaddresses([value])
        if len(addresses)!=1:raise ValueError('One sender required')
        _,address=addresses[0]
        if address.count('@')!=1:raise ValueError('Invalid address')
        return cls.domain(address.rsplit('@',1)[1])
    def observe(self,actor,tenant,body,correlation):
        self.service.authorize(actor,tenant,'governance.propose')
        try:
            sender,mixed,idna=self.email_domain(body.sender);reply=self.email_domain(body.reply_to)[0] if body.reply_to else None
            target=None
            if body.claimed_url:
                url=urlsplit(body.claimed_url)
                if url.scheme not in ('http','https') or not url.hostname or url.username or url.password:raise ValueError()
                target,target_mixed,target_idna=self.domain(url.hostname);mixed=mixed or target_mixed;idna=idna or target_idna
        except ValueError:reject('fraud_input','Identificador no normalizable',422)
        signals=[]
        if reply and sender!=reply:signals.append('sender_reply_domain_mismatch')
        if target and target!=sender:signals.append('link_sender_domain_mismatch')
        if mixed:signals.append('mixed_script_signal')
        if idna:signals.append('idna_normalized_signal')
        if body.new_payment_destination_claimed:signals.append('sensitive_change_requires_registered_channel')
        fields={'sender_domain':sender,'reply_domain':reply,'link_domain':target,'input_hash':digest(body.model_dump(mode='json')),'evidence_ref':body.evidence_ref,
                'signals':signals,'claimed_authentication':body.authentication_results_claim,'authenticated_spf_dkim_dmarc':'unknown','reputation':'not_queried','deepfake':'not_evaluated',
                'verdict':'not_determined','network_visited':False,'payment_or_blocking_action':False,'verification':None}
        return self.cases.create(actor,tenant,'fraud',fields,correlation)
    def verify(self,actor,tenant,record_id,body,correlation):
        require_human(self.service,actor,tenant,'governance.review')
        channel=self.service.settings.verification_channels.get(body.channel_ref)
        if not channel or channel.tenant_id!=tenant or not channel.enabled:reject('verification_channel','Canal no registrado previamente',403)
        meta=Vault(self.service).metadata(actor,tenant,body.evidence_id)
        if meta['state']!='reviewed':reject('evidence_unreviewed','Se requiere justificante revisado',422)
        Vault(self.service).read(actor,tenant,body.evidence_id,correlation)
        with self.service.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'governance.review');record=self.cases.row(db,tenant,record_id,'fraud')
            if record['revision']!=body.expected_revision or record['record_hash']!=body.record_hash:reject('conflict','Caso modificado',409)
            if record['created_by']==actor.actor_id:reject('separation_of_duties','Otro humano verifica',403)
            record['fields']['verification']={'decision':body.decision,'by':actor.actor_id,'channel_ref':body.channel_ref,'directory_ref':channel.directory_ref,'evidence_id':body.evidence_id,'authenticity':'human_attested_not_provider_verified'}
            record['revision']+=1;record['state']='human_verification_recorded';self.cases.save(db,tenant,record)
            self.service.db.audit(db,tenant,actor.actor_id,'fraud.verified',record_id,correlation,{'decision':body.decision,'channel_ref':body.channel_ref,'input_hash':record['fields']['input_hash']})
        return record
