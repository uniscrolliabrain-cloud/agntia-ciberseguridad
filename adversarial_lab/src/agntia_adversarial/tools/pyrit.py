from .base import ToolAdapter


class PyritAdapter(ToolAdapter):
    name = "pyrit"
    binary = "pyrit"
    capability = "ai.evaluate"

    def evaluate(self, sandbox, scenario: str):
        return self.run(sandbox, ["--scenario", scenario, "--offline"])
