"""Read-time restrictions propagate to report artifacts and typed projections."""
from datetime import datetime
import json
from ..errors import reject,not_found
from ..util import digest

def ensure_readable(db,tenant,evidence_id,instant,visited=None):
    visited=set() if visited is None else visited
    if evidence_id in visited or len(visited)>=32:reject('privacy_dependency','Dependencias no verificables',409)
    visited.add(evidence_id)
    restricted=db.execute('SELECT restricted FROM evidence_privacy WHERE tenant_id=? AND evidence_id=?',(tenant,evidence_id)).fetchone()
    if restricted and restricted[0]:reject('privacy_restricted','Lectura restringida por solicitud revisada',423)
    row=db.execute('SELECT body FROM evidence WHERE tenant_id=? AND id=?',(tenant,evidence_id)).fetchone()
    if not row:not_found()
    meta=json.loads(row[0])
    if meta['state'] in ('deleted','purge_pending'):reject('evidence_unavailable','Fuente no disponible',410)
    if not meta['legal_hold'] and datetime.fromisoformat(meta['expires_at'])<=instant:reject('evidence_expired','Fuente fuera de retención',410)
    if 'derived_source_ids' in meta:
        if digest(meta['derived_source_ids'])!=meta['envelope'].get('derived_sources_hash'):reject('privacy_dependency','Linaje de evidencia alterado',409)
        for source_id in meta['derived_source_ids']:ensure_readable(db,tenant,source_id,instant,visited.copy())
        return
    report=db.execute('SELECT 1 FROM reports WHERE tenant_id=? AND evidence_id=?',(tenant,evidence_id)).fetchone()
    if report:
        scope=db.execute('SELECT sources FROM report_source_scopes WHERE tenant_id=? AND evidence_id=?',(tenant,evidence_id)).fetchone()
        if not scope:reject('privacy_reconciliation_required','Informe anterior requiere reconciliar fuentes',424)
        for source_id in json.loads(scope[0]):ensure_readable(db,tenant,source_id,instant,visited.copy())
