"""Finite server-side limits, never chosen by untrusted repository content."""
from dataclasses import dataclass

@dataclass(frozen=True)
class ArtifactLimits:
    max_files: int = 2000
    max_file_bytes: int = 2 * 1024 * 1024
    max_total_bytes: int = 20 * 1024 * 1024
    max_depth: int = 20
    max_path_bytes: int = 512

    def __post_init__(self):
        bounds = {'max_files':100_000,'max_file_bytes':100_000_000,'max_total_bytes':1_000_000_000,'max_depth':64,'max_path_bytes':4096}
        for name, maximum in bounds.items():
            value = getattr(self, name)
            if type(value) is not int or not 1 <= value <= maximum:
                raise ValueError('Invalid artifact limits')
