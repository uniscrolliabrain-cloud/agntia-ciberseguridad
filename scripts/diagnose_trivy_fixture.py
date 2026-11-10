"""CI-only diagnostics, fixed synthetic data, no customer context or arbitrary arguments."""
import asyncio
import json
from pathlib import Path
import shutil
import tempfile
from agntia_ciberseguridad.runners.base import Tool,ToolImage
from agntia_ciberseguridad.runners.container import ContainerRunner

async def main():
    root=Path(__file__).resolve().parents[1]
    images=[ToolImage(Tool(x['tool']),x['version'],x['image'],x['policy_hash']) for x in json.loads((root/'state/scanner-build/images.json').read_text())]
    runner=ContainerRunner(images,docker=shutil.which('docker'))
    with tempfile.TemporaryDirectory() as temporary:
        folder=Path(temporary);folder.chmod(0o755)
        (folder/'Dockerfile').write_text('FROM alpine:3.20\nUSER root\n')
        command=runner.command(Tool.trivy,folder,'agntia-trivy-synthetic-diagnostic')
        process=await asyncio.create_subprocess_exec(*command,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.STDOUT)
        try:
            data,_=await asyncio.wait_for(process.communicate(),15)
            print(json.dumps({'synthetic_only':True,'exit':process.returncode,'bounded_diagnostic':data[:12000].decode(errors='replace')}))
        finally:
            if process.returncode is None:process.kill();await process.wait()
            await runner._cleanup('agntia-trivy-synthetic-diagnostic')
asyncio.run(main())
