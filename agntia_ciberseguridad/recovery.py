"""Bounded encrypted backup/restore for a QUIESCED synthetic single-node lab only."""
import base64
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import sqlite3
import tarfile
import tempfile
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from .errors import reject
from .storage import Database, CURRENT_SCHEMA
from .util import canonical

MAX_BYTES=64*1024*1024
MAX_FILES=2000
AAD=b'agntia-cyber-lab-backup-v1'
RESTORE_MARKER='RESTORE_BLOCKED'

def _key(reference):
    import re
    if not re.fullmatch('[A-Z][A-Z0-9_]{2,100}',reference):raise ValueError('Invalid key reference')
    try:
        key=base64.b64decode(os.environ.get(reference,''),validate=True)
        if len(key)!=32:raise ValueError()
        return key
    except ValueError:reject('backup_key_unavailable','Clave externa de backup no disponible',424)

def backup_lab(service,destination:Path,key_ref:str,*,quiesced:bool=False):
    if not service.settings.lab_mode or not quiesced:reject('lab_only','Backup requiere laboratorio detenido explícitamente',403)
    key=_key(key_ref)
    forbidden={p.token_env for p in service.settings.principals}|{r for p in service.settings.evidence_policies.values() for r in p.key_refs}|{service.settings.delegation_key_env,service.settings.metrics_token_env,service.settings.emergency_token_env}|{p.key_env for p in service.settings.event_sources.values()}
    if key_ref in forbidden:reject('backup_key_scope','Clave de backup debe ser independiente',422)
    destination=Path(destination)
    destination.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    if destination.exists() or destination.is_symlink():raise ValueError('Backup destination must be new')
    files={}; total=0
    with service.db.transaction() as db:
        if db.execute("SELECT 1 FROM jobs WHERE state IN ('running','pending','reconciliation_required') LIMIT 1").fetchone():reject('backup_busy','Resolver trabajos antes del backup de laboratorio',409)
        if db.execute("SELECT 1 FROM cost_reservations WHERE state IN ('started','reconciliation_required') LIMIT 1").fetchone():reject('backup_busy','Conciliar operaciones económicas antes del backup',409)
        for t in db.execute('SELECT id FROM tenants'):
            if not service.db.verify_audit(db,t['id'])['valid']:reject('audit_integrity','Auditoría inválida',409)
        with tempfile.TemporaryDirectory(prefix='cyber-backup-',dir=service.db.root) as temp:
            source_copy=Path(temp)/'db.sqlite3'
            with sqlite3.connect(service.db.path) as source,sqlite3.connect(source_copy) as target:source.backup(target)
            if source_copy.stat().st_size>MAX_BYTES:reject('backup_size','Snapshot excede tamaño de laboratorio',422)
            files['cyber.sqlite3']=source_copy.read_bytes()
            total=len(files['cyber.sqlite3'])
        # Only referenced custody files; no arbitrary root directory copy or secrets.
        from .evidence.vault import Vault
        vault=Vault(service)
        for row in db.execute('SELECT body FROM evidence'):
            meta=json.loads(row['body'])
            if meta['state']=='purged':continue
            for variant in ('original','redacted'):
                path=vault._file(meta,variant)
                if path.is_symlink() or not path.is_file() or path.stat().st_size>5*1024*1024:reject('backup_file','Evidencia no recuperable',409)
                if any(parent.is_symlink() for parent in (path.parent,path.parent.parent)):
                    reject('backup_path','Directorio de custodia no permitido',422)
                name=path.relative_to(service.db.root).as_posix()
                total+=path.stat().st_size
                if total>MAX_BYTES or len(files)>=MAX_FILES-2:reject('backup_size','Backup excede límite de laboratorio',422)
                files[name]=path.read_bytes()
        # Local target locations and credential environment references are sensitive: encrypted too.
        files['server-config.json']=canonical(service.settings.model_dump(mode='json')).encode()
        total=sum(len(v) for v in files.values())
        if len(files)>MAX_FILES or total>MAX_BYTES:reject('backup_size','Backup excede límite de laboratorio',422)
        manifest={'schema_version':1,'database_schema':CURRENT_SCHEMA,'files':{n:hashlib.sha256(v).hexdigest() for n,v in files.items()},
            'scope':'database_and_referenced_evidence_only','excluded':['snapshot_source_trees','remediation_candidates','external_secrets','external_approvals_after_backup'],
            'quiesced_lab_only':True,'privacy_reconciliation_required':True}
        files['manifest.json']=canonical(manifest).encode()
        buffer=io.BytesIO()
        with tarfile.open(fileobj=buffer,mode='w') as archive:
            for name,data in sorted(files.items()):
                info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o600;archive.addfile(info,io.BytesIO(data))
        nonce=os.urandom(12);encrypted=nonce+AESGCM(key).encrypt(nonce,buffer.getvalue(),AAD)
        with destination.open('xb') as handle:handle.write(encrypted);handle.flush();os.fsync(handle.fileno())
        destination.chmod(0o600)
    return {'backup_sha256':hashlib.sha256(encrypted).hexdigest(),'files':len(files),'plaintext_bytes':total,
        'encrypted_bytes':len(encrypted),'scope':manifest['scope'],'external_keys_included':False}

def restore_lab(source:Path,destination:Path,key_ref:str):
    destination=Path(destination)
    if destination.exists() or destination.is_symlink():raise ValueError('Restore directory must be new')
    source=Path(source)
    if source.is_symlink() or source.stat().st_size>MAX_BYTES*2:reject('backup_size','Archivo de backup inválido',422)
    try:
        blob=source.read_bytes();raw=AESGCM(_key(key_ref)).decrypt(blob[:12],blob[12:],AAD)
    except Exception:reject('backup_integrity','Backup o clave inválidos',409)
    if len(raw)>MAX_BYTES*2:reject('backup_size','Contenido de backup excesivo',422)
    files={};total=0
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:') as archive:
        for member in archive:
            name=PurePosixPath(member.name)
            if (not member.isfile() or name.is_absolute() or '..' in name.parts or str(name)!=member.name
                    or member.name in files or len(files)>=MAX_FILES+1 or member.size<0 or member.size>MAX_BYTES):
                reject('backup_path','Miembro de backup no permitido',422)
            total+=member.size
            if total>MAX_BYTES+1024*1024:reject('backup_size','Contenido excesivo',422)
            handle=archive.extractfile(member)
            if handle is None:reject('backup_file','Miembro no disponible',422)
            files[member.name]=handle.read()
    try:
        manifest=json.loads(files.pop('manifest.json'))
        if manifest['database_schema']!=CURRENT_SCHEMA or set(files)!=set(manifest['files']):raise ValueError()
        for name,data in files.items():
            if hashlib.sha256(data).hexdigest()!=manifest['files'][name]:raise ValueError()
    except (KeyError,ValueError,TypeError):reject('backup_integrity','Manifiesto no válido',409)
    # Allow only our named bundle members, never tar extraction commands.
    import re
    if any(n not in ('cyber.sqlite3','server-config.json') and not re.fullmatch(r'evidence/[A-Za-z0-9][A-Za-z0-9_-]{0,63}/[a-f0-9]{32}-(original|redacted)\.enc',n) for n in files):
        reject('backup_path','Objeto fuera del bundle de laboratorio',422)
    destination.mkdir(mode=0o700,parents=False)
    try:
        (destination/RESTORE_MARKER).write_text('Isolated restore: reconcile current privacy restrictions, revoked identities, grants, pending effects and external approvals before enabling any request. Snapshot trees are not restored.\n')
        for name,data in files.items():
            path=destination/name;path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
            with path.open('xb') as handle:handle.write(data)
            path.chmod(0o600)
        db=Database(destination)
        with db.connection(readonly=True) as c:
            if c.execute('SELECT max(version) FROM schema_migrations').fetchone()[0]!=CURRENT_SCHEMA:reject('backup_integrity','Versión SQLite no corresponde',409)
            if c.execute('PRAGMA integrity_check').fetchone()[0]!='ok':reject('backup_integrity','SQLite no válido',409)
            for t in c.execute('SELECT id FROM tenants'):
                if not db.verify_audit(c,t['id'])['valid']:reject('audit_integrity','Auditoría restaurada inválida',409)
        return {'restored':True,'new_work_enabled':False,'privacy_reconciliation_required':True,'external_keys_included':False,
            'snapshot_scanning_available':False,'scope':manifest['scope'],'files':len(files)}
    except Exception:
        # Partial restore stays blocked and is never advertised as ready.
        (destination/RESTORE_MARKER).write_text('Restore failed; do not enable.\n')
        raise
