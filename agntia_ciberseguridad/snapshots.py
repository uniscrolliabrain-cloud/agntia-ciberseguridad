"""POSIX descriptor-relative copy of an approved local tree; never run Git/hooks."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import tempfile

from .artifact_limits import ArtifactLimits
from .contracts import ResourceId
from .errors import DomainError, reject, not_found
from .network_policy import local_target
from .util import canonical, digest, now, uid


def _safe_name(name, limits):
    if (name in ('', '.', '..') or '/' in name or '\\' in name or ':' in name
            or any(ord(c) < 32 or ord(c) == 127 for c in name)
            or len(name.encode('utf-8')) > limits.max_path_bytes):
        reject('artifact_path', 'Nombre de recurso no admitido', 422)


def _signature(info):
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


class SnapshotStore:
    """Service-owned storage. Local admins remain trusted; per-job mounts are read-only."""
    def __init__(self, service, limits=None):
        self.service = service
        self.limits = limits or ArtifactLimits()
        self.root = service.settings.data_dir.resolve() / 'snapshots'
        self.root.mkdir(mode=0o700, parents=True, exist_ok=True)

    def acquire(self, actor, tenant, body, correlation, cancelled=lambda: False):
        asset, grant, target = self.service.validate_authorization(actor, tenant, body)
        if target.kind.value not in ('repository', 'directory') or body.profile.value != 'static_read':
            reject('unsupported', 'Solo adquisición de directorio local estático', 424)
        if os.name != 'posix' or not hasattr(os, 'O_NOFOLLOW'):
            reject('unsupported', 'Adquisición segura requiere ejecutor POSIX', 424)
        source = local_target(target, self.service.settings)
        # Re-open from / without following any component, including roots changed after resolve().
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        current = os.open('/', flags)
        temp = None
        try:
            for component in source.parts[1:]:
                child = os.open(component, flags, dir_fd=current)
                os.close(current); current = child
            bucket = self.root / tenant
            bucket.mkdir(mode=0o700, exist_ok=True)
            temp = Path(tempfile.mkdtemp(prefix='.acquiring-', dir=bucket))
            contents = temp / 'content'; contents.mkdir(mode=0o700)
            files, exclusions = [], []
            total = 0
            entries_seen = 0
            checks = 0
            def check_cancel():
                nonlocal checks
                if cancelled(): reject('cancelled', 'Adquisición cancelada', 409)
                checks += 1
                if checks % 128 == 0:self.service.validate_authorization(actor, tenant, body)
            def walk(fd, destination, prefix='', depth=0):
                nonlocal total, entries_seen
                check_cancel()
                if depth > self.limits.max_depth:reject('artifact_limit', 'Profundidad excedida', 422)
                before = os.fstat(fd)
                names = []
                with os.scandir(fd) as entries:
                    for entry in entries:
                        if len(names) >= self.limits.max_files:reject('artifact_limit', 'Demasiadas entradas', 422)
                        names.append(entry.name)
                for name in sorted(names):
                    check_cancel(); _safe_name(name, self.limits)
                    entries_seen += 1
                    if entries_seen > self.limits.max_files:reject('artifact_limit', 'Demasiadas entradas totales', 422)
                    relative = prefix + name
                    if len(relative.encode()) > self.limits.max_path_bytes:reject('artifact_limit', 'Ruta demasiado larga', 422)
                    if name == '.git':
                        exclusions.append({'path':relative, 'reason':'git_metadata_not_read'})
                        continue
                    info = os.stat(name, dir_fd=fd, follow_symlinks=False)
                    if stat.S_ISLNK(info.st_mode) or not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):
                        reject('artifact_type', 'Enlaces o archivos especiales no admitidos', 422)
                    if stat.S_ISDIR(info.st_mode):
                        child = os.open(name, flags, dir_fd=fd)
                        try:
                            if _signature(os.fstat(child)) != _signature(info):reject('artifact_changed', 'Origen modificado', 409)
                            dest = destination / name; dest.mkdir(mode=0o700)
                            walk(child, dest, relative+'/', depth+1)
                            dest.chmod(0o555)
                        finally:os.close(child)
                        continue
                    if len(files) + len(exclusions) >= self.limits.max_files or info.st_size > self.limits.max_file_bytes or total + info.st_size > self.limits.max_total_bytes:
                        reject('artifact_limit', 'Límites de contenido excedidos', 422)
                    if info.st_nlink != 1:reject('artifact_type', 'Hardlinks no admitidos', 422)
                    infile = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
                    checksum = hashlib.sha256(); size = 0; beginning = b''
                    try:
                        opened = os.fstat(infile)
                        if not stat.S_ISREG(opened.st_mode) or _signature(opened) != _signature(info) or opened.st_nlink != 1:
                            reject('artifact_changed', 'Origen modificado', 409)
                        with (destination/name).open('xb') as out:
                            while True:
                                check_cancel(); chunk = os.read(infile, 65536)
                                if not chunk:break
                                size += len(chunk)
                                if size > self.limits.max_file_bytes or total + size > self.limits.max_total_bytes:
                                    reject('artifact_limit', 'Límites de contenido excedidos', 422)
                                if len(beginning) < 256:beginning += chunk[:256-len(beginning)]
                                checksum.update(chunk); out.write(chunk)
                            out.flush(); os.fsync(out.fileno())
                        if size != info.st_size or _signature(os.fstat(infile)) != _signature(info):
                            reject('artifact_changed', 'Origen modificado durante lectura', 409)
                    finally:os.close(infile)
                    total += size
                    reason = ('external_submodule_not_acquired' if name == '.gitmodules' else
                              'lfs_pointer_not_materialized' if beginning.startswith(b'version https://git-lfs.github.com/spec/v1') else None)
                    if reason:exclusions.append({'path':relative,'reason':reason})
                    files.append({'path':relative,'bytes':size,'sha256':checksum.hexdigest(),'binary':b'\0' in beginning})
                    (destination/name).chmod(0o444)
                if _signature(os.fstat(fd)) != _signature(before):reject('artifact_changed', 'Directorio modificado durante adquisición', 409)
            walk(current, contents)
            self.service.validate_authorization(actor, tenant, body)
            manifest = {'schema_version':1,'id':uid(),'tenant_id':tenant,'asset_id':asset['id'],
                        'grant_id':grant['id'],'grant_revision':grant['revision'],'created_by':actor.actor_id,
                        'created_at':now(),'correlation_id':correlation,'source_kind':'local_directory',
                        'git_commit':None,'configuration_hash':asset['configuration_hash'],'files':files,
                        'total_bytes':total,'exclusions':exclusions,'content_hash':digest(files),
                        'coverage':'partial' if exclusions else 'captured_local_files',
                        'limitations':['No Git history, remote clone, archive extraction, LFS download or submodule checkout.',
                                       'File collection only; language analysis and vulnerability coverage belong to scanners.']}
            manifest['manifest_hash'] = digest(manifest)
            with (temp/'manifest.json').open('x') as output:
                output.write(canonical(manifest));output.flush();os.fsync(output.fileno())
            (temp/'manifest.json').chmod(0o400);contents.chmod(0o555)
            with self.service.db.transaction() as db:
                self.service.auth.authorize(actor, tenant, 'audits.preview')
                current_grant = self.service._grant(db, tenant, grant['id'])
                if current_grant['revision'] != grant['revision'] or current_grant['state'] != 'approved':
                    reject('conflict', 'Autorización modificada', 409)
                destination = bucket / manifest['id']
                temp.rename(destination);temp = destination
                db.execute('INSERT INTO snapshots VALUES(?,?,?,?,?,?,?)',
                           (tenant,manifest['id'],asset['id'],grant['id'],manifest['manifest_hash'],manifest['content_hash'],canonical(manifest)))
                self.service.db.audit(db,tenant,actor.actor_id,'snapshot.acquired' ,manifest['id'],correlation,
                                      {'snapshot_id':manifest['id'],'manifest_hash':manifest['manifest_hash'],'content_hash':manifest['content_hash']})
            temp = None
            return manifest
        except DomainError:raise
        except OSError:
            reject('artifact_unavailable', 'No se pudo adquirir el recurso de forma segura', 422)
        finally:
            os.close(current)
            if temp is not None:self._remove_own(temp)

    @staticmethod
    def _remove_own(path):
        # Only random service-owned temporary trees, never source paths.
        for base, dirs, files in os.walk(path):
            Path(base).chmod(0o700)
        shutil.rmtree(path)

    def verify(self, actor, tenant, snapshot_id):
        from pydantic import TypeAdapter
        TypeAdapter(ResourceId).validate_python(snapshot_id)
        self.service.authorize(actor,tenant,'assets.read')
        with self.service.db.connection(readonly=True) as db:
            record=db.execute('SELECT manifest_hash,content_hash,body FROM snapshots WHERE tenant_id=? AND id=?',(tenant,snapshot_id)).fetchone()
            if not record:not_found()
        folder = self.root/tenant/snapshot_id
        if not folder.is_dir():reject('snapshot_integrity','Snapshot registrado sin contenido recuperable',409)
        try:
            manifest=json.loads((folder/'manifest.json').read_text())
            claimed=manifest.pop('manifest_hash')
            if manifest['tenant_id'] != tenant or manifest['id'] != snapshot_id or digest(manifest) != claimed or claimed != record['manifest_hash'] or manifest['content_hash'] != record['content_hash']:
                raise ValueError()
            contents=folder/'content'
            actual=[]
            for base,dirs,files in os.walk(contents,followlinks=False):
                if any((Path(base)/d).is_symlink() for d in dirs):raise ValueError()
                for name in files:
                    path=Path(base)/name
                    if path.is_symlink() or not path.is_file():raise ValueError()
                    relative=path.relative_to(contents).as_posix()
                    actual.append((relative,path.stat().st_size,hashlib.sha256(path.read_bytes()).hexdigest()))
            expected=sorted((f['path'],f['bytes'],f['sha256']) for f in manifest['files'])
            if sorted(actual) != expected or manifest['content_hash'] != digest(manifest['files']):raise ValueError()
            manifest['manifest_hash']=claimed
            if canonical(manifest) != record['body']:raise ValueError()
            return manifest, contents
        except (OSError,ValueError,KeyError,TypeError):
            reject('snapshot_integrity', 'Snapshot ausente o alterado', 409)
