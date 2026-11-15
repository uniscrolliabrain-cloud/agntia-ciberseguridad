from .base import ToolAdapter


class SchemathesisAdapter(ToolAdapter):
    name = "schemathesis"
    binary = "schemathesis"
    capability = "api.passive"

    def check(self, sandbox, schema_path: str):
        return self.run(sandbox, ["run", schema_path, "--max-examples", "20"])
