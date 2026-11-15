from .base import ToolAdapter


class GarakAdapter(ToolAdapter):
    name = "garak"
    binary = "garak"
    capability = "ai.evaluate"

    def probe(self, sandbox, model: str):
        return self.run(sandbox, ["--model_type", "test", "--model_name", model, "--probes", "promptinject"])
