from .base import ToolAdapter


class SyftAdapter(ToolAdapter):
    name = "syft"
    binary = "syft"
    capability = "sbom"

    def sbom(self, sandbox, path: str):
        return self.run(sandbox, [f"dir:{path}", "-o", "cyclonedx-json"])
