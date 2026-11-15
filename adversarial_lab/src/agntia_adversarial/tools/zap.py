from .base import ToolAdapter


class ZapAdapter(ToolAdapter):
    name = "zap"
    binary = "zap.sh"
    capability = "api.passive"

    def baseline(self, sandbox, target_url: str):
        return self.run(sandbox, ["-cmd", "-quickurl", target_url, "-quickout", "zap.json"])
