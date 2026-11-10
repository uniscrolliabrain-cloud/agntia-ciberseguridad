"""Closed profiles and bounded outcomes; no shell/argv/environment from a model."""
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import re

class Tool(str, Enum):
    gitleaks='gitleaks'
    osv='osv'
    semgrep='semgrep'
    trivy='trivy'

@dataclass(frozen=True)
class ToolImage:
    tool: Tool
    version: str
    image: str
    policy_hash: str

    def __post_init__(self):
        if not re.fullmatch(r'(?:[a-zA-Z0-9._/:-]+@)?sha256:[a-f0-9]{64}',self.image):
            raise ValueError('Immutable image ID/digest required')
        versions={Tool.gitleaks:'8.30.1',Tool.osv:'2.7.1',Tool.semgrep:'1.185.0',Tool.trivy:'0.76.2'}
        if self.tool not in versions or self.version != versions[self.tool] or not re.fullmatch(r'[a-f0-9]{64}',self.policy_hash):
            raise ValueError('Unsupported tool contract')

@dataclass(frozen=True)
class RunLimits:
    timeout_seconds: float=60
    max_output_bytes: int=2*1024*1024
    memory_mb: int=256
    cpus: float=1
    pids: int=32

    def __post_init__(self):
        for value,low,high in ((self.timeout_seconds,.05,300),(self.max_output_bytes,1024,8*1024*1024),(self.memory_mb,32,1024),(self.cpus,.1,2),(self.pids,4,64)):
            if isinstance(value,bool) or not isinstance(value,(int,float)) or not low<=value<=high:raise ValueError('Invalid runner limits')
        for value in (self.max_output_bytes,self.memory_mb,self.pids):
            if type(value) is not int:raise ValueError('Integer runner limit required')

@dataclass(frozen=True)
class RunResult:
    tool: Tool
    version: str
    status: str
    exit_code: int|None
    output: bytes=field(default=b'',repr=False)
    output_sha256: str|None=None
    duration_seconds: float=0
    cleanup_verified: bool=False
    error_code: str|None=None
    policy_hash: str|None=None
    image: str|None=None
