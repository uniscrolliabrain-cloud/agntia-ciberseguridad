"""Internal business boundary. No HTTP execution route and release gates deny by default."""
from .adapters import gitleaks,osv,semgrep,trivy
from .contracts import Profile
from .errors import DomainError,reject
from .offline_database import verify_cache
from .runners.base import Tool
from .safety import ReleaseGates
from .snapshots import SnapshotStore
from .util import digest,utcnow

class StaticScanner:
    def __init__(self,service,runner,*,gates=None):
        self.service=service
        self.runner=runner
        self.snapshots=SnapshotStore(service)
        self.gates=gates or ReleaseGates()

    async def scan(self,actor,tenant,authorization,snapshot_id,tool,correlation,*,cache=None,database=None,execution_key=None):
        self.gates.require_customer_execution()
        if authorization.profile!=Profile.static_read:reject('unsupported','Solo análisis estático',424)
        asset,grant,_=self.service.validate_authorization(actor,tenant,authorization)
        manifest,contents=self.snapshots.verify(actor,tenant,snapshot_id)
        if manifest['asset_id']!=asset['id'] or manifest['grant_id']!=grant['id'] or manifest['grant_revision']!=grant['revision']:
            reject('snapshot_scope','Snapshot fuera de la autorización vigente',403)
        if tool not in (Tool.gitleaks,Tool.osv,Tool.semgrep,Tool.trivy):reject('unsupported','Scanner no permitido',424)
        if tool==Tool.osv:
            try:verify_cache(cache,database,utcnow())
            except (ValueError,TypeError,OSError):reject('offline_database','Caché offline ausente o no verificable',424)
        def revoked():
            try:self.service.validate_authorization(actor,tenant,authorization);return False
            except DomainError:return True
        with self.service.telemetry.span('scanner.run',component='runner',tool=tool.value,correlation_id=correlation):
            run=await self.runner.run(tool,contents,cache=cache,cancelled=revoked,**({"execution_key":execution_key} if execution_key else {}))
        self.service.validate_authorization(actor,tenant,authorization)
        self.snapshots.verify(actor,tenant,snapshot_id)
        paths={file['path'] for file in manifest['files']}
        if tool==Tool.osv:
            try:verify_cache(cache,database,utcnow())
            except (ValueError,TypeError,OSError):reject('offline_database','Caché modificada durante el trabajo',409)
            result=osv.parse(run,snapshot_id,database=database,manifest_paths=paths)
        else:result={Tool.gitleaks:gitleaks,Tool.semgrep:semgrep,Tool.trivy:trivy}[tool].parse(run,snapshot_id,manifest_paths=paths)
        result['snapshot_coverage']=manifest['coverage']
        result['snapshot_exclusions']=manifest['exclusions']
        # No source bytes, stdout/stderr, credential values or report titles enter audit.
        with self.service.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'audits.preview')
            current=self.service._grant(db,tenant,grant['id'])
            if current['revision']!=grant['revision'] or current['state']!='approved':reject('conflict','Autorización modificada',409)
            self.service.db.audit(db,tenant,actor.actor_id,'scanner.completed',snapshot_id,correlation,
                                  {'snapshot_id':snapshot_id,'tool':tool.value,'status':result['status'],
                                   'result_hash':digest(result),'policy_hash':run.policy_hash,'cleanup_verified':run.cleanup_verified})
        return result
