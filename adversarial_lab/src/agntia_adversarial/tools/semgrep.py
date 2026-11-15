from .base import ToolAdapter


class SemgrepAdapter(ToolAdapter):
    name = "semgrep"
    binary = "semgrep"
    capability = "repo.static"

    def scan(self, sandbox, path: str, config: str = "auto"):
        return self.run(sandbox, ["--json", "--config", config, path])
