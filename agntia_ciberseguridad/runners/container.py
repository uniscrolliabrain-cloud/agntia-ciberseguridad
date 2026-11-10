"""Dedicated trusted launcher. Must not be hosted in the public API process.

The launcher talks to a LOCAL daemon; the untrusted scanner has no socket/network.
No generic public run endpoint and no fallback to host binaries.
"""
import asyncio
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import time
from uuid import uuid4

from .base import RunLimits, RunResult, Tool, ToolImage
from ..errors import reject


class ContainerRunner:
    def __init__(self, images, *, docker='/usr/bin/docker', limits=None):
        self.images={image.tool:image for image in images}
        if len(self.images)!=len(images):raise ValueError('Duplicate tool image')
        self.docker=str(Path(docker).resolve())
        if not Path(self.docker).is_file() or not os.path.isabs(docker):raise ValueError('Approved Docker executable required')
        self.limits=limits or RunLimits()

    def command(self, tool, input_path, name, cache=None):
        if tool not in self.images:reject('unsupported','Herramienta no habilitada',424)
        image=self.images[tool]
        source=Path(input_path)
        if not source.is_absolute() or source.is_symlink() or not source.is_dir() or ',' in str(source) or any(ord(c)<32 for c in str(source)):
            reject('runner_input','Snapshot local inválido',422)
        argv=[self.docker,'--host=unix:///var/run/docker.sock','run','--name',name,
              '--pull=never','--read-only','--network=none','--user=65532:65532','--cap-drop=ALL',
              '--security-opt=no-new-privileges:true','--pids-limit='+str(self.limits.pids),
              '--memory='+str(self.limits.memory_mb)+'m','--memory-swap='+str(self.limits.memory_mb)+'m',
              '--cpus='+str(self.limits.cpus),'--ulimit=nofile=128:128','--ulimit=core=0:0',
              '--log-driver=none','--workdir=/input','--entrypoint=/scanner',
              '--mount=type=bind,src='+str(source.resolve())+',dst=/input,readonly,bind-propagation=rprivate',
              '--tmpfs=/tmp:rw,noexec,nosuid,nodev,size=16m,mode=1777',
              '--tmpfs=/out:rw,noexec,nosuid,nodev,size=8m,mode=1777',
              '--env=HOME=/tmp','--env=TMPDIR=/tmp','--env=PATH=/','--env=GOMAXPROCS=2']
        if tool==Tool.osv:
            if cache is None or not Path(cache).is_absolute() or not Path(cache).is_dir() or Path(cache).is_symlink() or ',' in str(cache):
                reject('offline_database','Base offline aprobada requerida',424)
            argv += ['--mount=type=bind,src='+str(Path(cache).resolve())+',dst=/db,readonly,bind-propagation=rprivate',
                     '--env=OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY=/db']
        argv.append(image.image)
        if tool==Tool.gitleaks:
            argv += ['dir','/input','--no-banner','--redact=100','--log-level=error',
                     '--config=/policy/gitleaks.toml','--gitleaks-ignore-path=/policy/empty.ignore',
                     '--ignore-gitleaks-allow','--report-format=json','--report-path=/dev/stdout','--exit-code=10',
                     '--max-archive-depth=0','--max-decode-depth=0']
        else:
            argv += ['scan','source','--offline','--format=json','--all-packages',
                     '--no-ignore','--no-call-analysis','--no-resolve','--config=/policy/osv.toml','-r','/input']
        return argv

    async def _process(self, argv, *, cap, timeout):
        # Docker proxy defaults may inject API-host proxy/secrets into newly created containers.
        # DOCKER_CONFIG points at a private empty directory for this offline launcher invocation.
        import tempfile
        with tempfile.TemporaryDirectory(prefix='agntia-docker-client-') as config:
            env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','DOCKER_CONFIG':config}
            proc=await asyncio.create_subprocess_exec(*argv,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE,env=env)
            collected=bytearray();seen=0;overflow=False
            async def drain(stream, keep):
                nonlocal seen,overflow
                while True:
                    chunk=await stream.read(16384)
                    if not chunk:return
                    seen+=len(chunk)
                    if seen>cap:
                        overflow=True
                        if proc.returncode is None:
                            try:proc.kill()
                            except ProcessLookupError:pass
                    elif keep:collected.extend(chunk)
                    # Keep draining/discarding after the cap. Stopping a reader can
                    # deadlock Process.wait() on a full pipe even after killing the CLI.
            completion=asyncio.gather(drain(proc.stdout,True),drain(proc.stderr,False),proc.wait())
            try:
                await asyncio.wait_for(asyncio.shield(completion),timeout)
                if overflow:raise OverflowError()
                return proc.returncode,bytes(collected)
            finally:
                if proc.returncode is None:
                    try:proc.kill()
                    except ProcessLookupError:pass
                try:
                    await asyncio.wait_for(asyncio.shield(completion),2)
                except TimeoutError:
                    completion.cancel()

    async def _cleanup(self,name):
        prefix=[self.docker,'--host=unix:///var/run/docker.sock']
        try:
            code,_=await self._process([*prefix,'rm','--force',name],cap=4096,timeout=10)
            # A stopped/deleted container is checked by exact name; never kill global processes.
            check,data=await self._process([*prefix,'ps','--all','--filter','name=^/'+name+'$','--format','{{.Names}}'],cap=4096,timeout=10)
            return check==0 and not data.strip()
        except Exception:return False

    async def run(self, tool, input_path, *, cache=None, cancelled=lambda:False):
        name='agntia-scan-'+uuid4().hex
        command=self.command(tool,input_path,name,cache)
        image=self.images[tool];start=time.perf_counter();output=b'';code=None;status='error';error='runner_unavailable'
        task=None
        try:
            if cancelled():error='cancelled'
            else:
                task=asyncio.create_task(self._process(command,cap=self.limits.max_output_bytes,timeout=self.limits.timeout_seconds))
                while not task.done():
                    if cancelled():
                        task.cancel();error='cancelled';break
                    await asyncio.sleep(.02)
                if error!='cancelled':
                    code,output=await task
                    known=(0,10) if tool==Tool.gitleaks else (0,1)
                    if code in known:status='completed';error=None
                    else:error='scanner_exit'
        except TimeoutError:error='timeout'
        except OverflowError:error='output_limit'
        except asyncio.CancelledError:
            error='cancelled'
            raise
        except (OSError,ValueError):error='runner_unavailable'
        finally:
            if task and not task.done():
                task.cancel()
                try:await task
                except (asyncio.CancelledError,Exception):pass
            cleaned=await asyncio.shield(self._cleanup(name))
        if not cleaned:status='error';error='cleanup_unverified';output=b''
        return RunResult(tool,image.version,status,code,output,hashlib.sha256(output).hexdigest(),
                         time.perf_counter()-start,cleaned,error,image.policy_hash,image.image)
