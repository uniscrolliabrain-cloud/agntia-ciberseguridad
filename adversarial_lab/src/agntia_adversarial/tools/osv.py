from .base import ToolAdapter


class OsvAdapter(ToolAdapter):
    name = "osv"
    binary = "osv-scanner"
    capability = "repo.static"

    def scan(self, sandbox, path: str):
        return self.run(sandbox, ["--format", "json", "-r", path])
