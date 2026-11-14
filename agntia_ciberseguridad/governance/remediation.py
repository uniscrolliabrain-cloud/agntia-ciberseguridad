"""Two original lab-only rules. Build a private candidate, never modify/merge/deploy client source."""
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
from typing import Literal
from pydantic import Field,StrictInt
from .store import Cases
from ..auth import require_human
from ..contracts import Model,ResourceId,Hash,OpaqueId,AuditPreview
from ..evidence.redaction import text
from ..errors import reject
from ..snapshots import SnapshotStore
from ..safety import ReleaseGates
from ..runners.base import Tool
from ..adapters import gitleaks,semgrep
from ..util import canonical,digest

RULES={'remove_synthetic_canary':('canary.txt','gitleaks','agntia-canary'),'remove_fixture_eval':('fixture_eval.py','semgrep','agntia.python.dynamic-eval')}
class RemediationPlan(Model):
    snapshot_id: ResourceId
    finding_id: Hash
    expected_finding_revision: StrictInt=Field(ge=0)
    rule: Literal['remove_synthetic_canary','remove_fixture_eval']
    source_license_ref: OpaqueId

class Remediation:
    def __init__(self,service):self.service=service;self.cases=Cases(service);self.snapshots=SnapshotStore(service)
    def _lab(self,db,tenant,resource_id):
        asset=self.service._asset(db,tenant,resource_id)
        if not self.service.settings.lab_mode or asset['target_ref'] not in self.service.settings.remediation_fixture_refs:reject('remediation_lab_only','Solo fixtures registrados por servidor',424)
        return asset
    @staticmethod
    def replacement(rule,original):
        if rule=='remove_synthetic_canary':
            if not re.fullmatch(rb'AGNTIA_TEST_SECRET_[A-Za-z0-9]{16,100}\n?',original):reject('fixture_contract','La regla solo cubre una canary sintética aislada',422)
            return b'Synthetic nonfunctional credential fixture removed\n'
        if original!=b'def run(value):\n    return eval(value)\n':reject('fixture_contract','Solo plantilla eval sintética exacta',422)
        return b'def run(value):\n    return value\n'
    def plan(self,actor,tenant,body,correlation):
        self.service.authorize(actor,tenant,'governance.propose');manifest,contents=self.snapshots.verify(actor,tenant,body.snapshot_id)
        if manifest['coverage']!='captured_local_files':reject('remediation_coverage','No preparar cambios sobre captura parcial',422)
        with self.service.db.connection(readonly=True) as db:
            self._lab(db,tenant,manifest['asset_id'])
            row=db.execute('SELECT body FROM finding_current WHERE tenant_id=? AND id=?',(tenant,body.finding_id)).fetchone()
            if not row:reject('not_found','Finding no disponible',404)
            finding=json.loads(row[0]);path,tool,rule_id=RULES[body.rule]
            if finding['asset_id']!=manifest['asset_id'] or finding['last_snapshot_id']!=manifest['id'] or finding.get('revision',0)!=body.expected_finding_revision or finding['path']!=path or finding['tool']!=tool or finding['rule_id']!=rule_id:reject('remediation_scope','Finding/origen no corresponde a regla',409)
            observation=db.execute('SELECT body FROM finding_observations WHERE tenant_id=? AND finding_id=? ORDER BY rowid DESC LIMIT 1',(tenant,body.finding_id)).fetchone()
            expected_policy=json.loads(observation[0])['policy_hash']
        original=(contents/path).read_bytes()
        if len(original)>4096:reject('fixture_contract','Fixture excede tamaño previsto',422)
        replacement=self.replacement(body.rule,original)
        patch=''.join(difflib.unified_diff(original.decode().splitlines(True),replacement.decode().splitlines(True),fromfile='a/'+path,tofile='b/'+path))
        fields={**body.model_dump(mode='json'),'resource_id':manifest['asset_id'],'grant_id':manifest['grant_id'],'grant_revision':manifest['grant_revision'],
            'source_manifest_hash':manifest['manifest_hash'],'source_content_hash':manifest['content_hash'],'source_finding_hash':digest(finding),'target_path':path,
            'before_sha256':hashlib.sha256(original).hexdigest(),'after_sha256':hashlib.sha256(replacement).hexdigest(),'tool':tool,'expected_tool_policy_hash':expected_policy,
            'diff_redacted':text(patch),'path_change_allowlist':[path],'candidate_artifact':'private_directory_not_git_branch','merge_enabled':False,'deploy_enabled':False,
            'rollback':'discard_private_candidate_original_unchanged','source_license_status':'declared_reference_not_legal_verification'}
        return self.cases.create(actor,tenant,'remediation',fields,correlation)
    def _origin(self,actor,tenant,record):
        fields=record['fields'];authorization=AuditPreview(asset_id=fields['resource_id'],grant_id=fields['grant_id'],profile='static_read')
        self.service.validate_authorization(actor,tenant,authorization)
        with self.service.db.connection(readonly=True) as db:
            self._lab(db,tenant,fields['resource_id']);finding=db.execute('SELECT body FROM finding_current WHERE tenant_id=? AND id=?',(tenant,fields['finding_id'])).fetchone()
            if not finding or digest(json.loads(finding[0]))!=fields['source_finding_hash']:reject('remediation_conflict','Finding modificado',409)
        latest=self.snapshots.acquire(actor,tenant,authorization,'remediation-origin-check')
        if latest['content_hash']!=fields['source_content_hash']:reject('remediation_conflict','Origen cambió; preparar otra propuesta',409)
        return authorization
    def _folder(self,tenant,record_id):return self.service.settings.data_dir.resolve()/'remediations'/tenant/record_id/'candidate'
    @staticmethod
    def tree(root):
        files=[]
        if not root.is_dir() or root.is_symlink():reject('candidate_integrity','Candidato no recuperable',409)
        for path in sorted(root.rglob('*')):
            if path.is_symlink() or (not path.is_dir() and not path.is_file()):reject('candidate_integrity','Tipo no permitido',409)
            if path.is_file():files.append({'path':path.relative_to(root).as_posix(),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        return files
    def _state(self,actor,tenant,record_id,state,correlation,**updates):
        with self.service.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'governance.review')
            record=self.cases.row(db,tenant,record_id,'remediation');record['state']=state;record['revision']+=1;record['fields'].update(updates);self.cases.save(db,tenant,record)
            self.service.db.audit(db,tenant,actor.actor_id,'remediation.state',record_id,correlation,{'state':state,'source_manifest_hash':record['fields']['source_manifest_hash']})
        return record
    def materialize(self,actor,tenant,record_id,correlation):
        require_human(self.service,actor,tenant,'governance.review')
        record=self.cases.get(actor,tenant,record_id,correlation);self.cases.current_review(record)
        if record['kind']!='remediation':reject('remediation_scope','Tipo no permitido',422)
        if record['state']=='candidate_ready':
            if digest(self.tree(self._folder(tenant,record_id)))!=record['fields']['candidate_hash']:reject('candidate_integrity','Candidato alterado',409)
            return record
        if record['state']!='reviewed':reject('conflict','Estado no materializable',409)
        try:self._origin(actor,tenant,record)
        except Exception:
            self._state(actor,tenant,record_id,'stale_origin',correlation);raise
        with self.service.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'governance.review');current=self.cases.row(db,tenant,record_id,'remediation')
            if current['revision']!=record['revision'] or current['state']!='reviewed':reject('conflict','Propuesta modificada',409)
            current['state']='building_candidate';current['revision']+=1;self.cases.save(db,tenant,current)
        manifest,contents=self.snapshots.verify(actor,tenant,record['fields']['snapshot_id'])
        folder=self._folder(tenant,record_id);folder.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        temporary=Path(tempfile.mkdtemp(prefix='.candidate-',dir=folder.parent))
        try:
            shutil.copytree(contents,temporary,dirs_exist_ok=True);temporary.chmod(0o700)
            target=temporary/record['fields']['target_path'];original=target.read_bytes()
            if hashlib.sha256(original).hexdigest()!=record['fields']['before_sha256']:reject('candidate_integrity','Base alterada',409)
            target.chmod(0o600);target.write_bytes(self.replacement(record['fields']['rule'],original));target.chmod(0o444)
            files=self.tree(temporary);expected={f['path']:f['sha256'] for f in manifest['files']}
            if {f['path'] for f in files}!=set(expected) or any(f['sha256']!=(record['fields']['after_sha256'] if f['path']==record['fields']['target_path'] else expected[f['path']]) for f in files):reject('candidate_scope','Cambios fuera de allowlist',409)
            self.snapshots.verify(actor,tenant,manifest['id'])
            for path in temporary.rglob('*'):path.chmod(0o555 if path.is_dir() else 0o444)
            temporary.chmod(0o555);temporary.rename(folder)
        except Exception:
            for path in temporary.rglob('*'):
                if path.is_dir():path.chmod(0o700)
            temporary.chmod(0o700);shutil.rmtree(temporary,ignore_errors=True);self._state(actor,tenant,record_id,'reconciliation_required',correlation);raise
        return self._state(actor,tenant,record_id,'candidate_ready',correlation,candidate_hash=digest(files),candidate_manifest=files)
    async def retest(self,actor,tenant,record_id,runner,correlation,*,gates=None):
        (gates or ReleaseGates()).require_customer_execution();require_human(self.service,actor,tenant,'governance.review')
        record=self.cases.get(actor,tenant,record_id,correlation);self.cases.current_review(record)
        if record['kind']!='remediation' or record['state']!='candidate_ready':reject('conflict','Candidato no listo',409)
        authorization=self._origin(actor,tenant,record);folder=self._folder(tenant,record_id)
        if digest(self.tree(folder))!=record['fields']['candidate_hash']:reject('candidate_integrity','Candidato alterado',409)
        tool=Tool(record['fields']['tool'])
        if tool not in runner.images or runner.images[tool].policy_hash!=record['fields']['expected_tool_policy_hash']:reject('retest_policy','Política de scanner distinta',409)
        with self.service.db.transaction() as db:
            current=self.cases.row(db,tenant,record_id,'remediation')
            if current['revision']!=record['revision'] or current['state']!='candidate_ready':reject('conflict','Retest ya iniciado',409)
            current['state']='retesting';current['revision']+=1;self.cases.save(db,tenant,current)
        def cancelled():
            try:self.service.validate_authorization(actor,tenant,authorization);self.cases.current_review(record);return False
            except Exception:return True
        run=await runner.run(tool,folder,cancelled=cancelled)
        if cancelled():return self._state(actor,tenant,record_id,'reconciliation_required',correlation)
        if digest(self.tree(folder))!=record['fields']['candidate_hash']:reject('candidate_integrity','Candidato cambió durante retest',409)
        result=(gitleaks if tool==Tool.gitleaks else semgrep).parse(run,record_id,manifest_paths={f['path'] for f in record['fields']['candidate_manifest']})
        result.pop('snapshot_id',None);result.update(candidate_id=record_id,source_snapshot_id=record['fields']['snapshot_id'],candidate_hash=record['fields']['candidate_hash'])
        state='retest_passed_fixture' if result['status']=='no_findings' else 'retest_failed'
        return self._state(actor,tenant,record_id,state,correlation,retest=result,source_finding_changed=False,verified_fixed=False)
