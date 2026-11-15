"""AD-01: invariantes del baseline verificado.

Estos tests fijan hechos medidos sobre `main@dd18f2a`, no aspiraciones. Si alguno falla, o el
baseline cambió de forma deliberada (actualizar el reporte AD-01) o se introdujo una regresión.
"""

import json
import unittest
from pathlib import Path

from agntia_ciberseguridad.storage import CURRENT_SCHEMA, MIGRATIONS

ROOT = Path(__file__).resolve().parents[2]


class BaselineInventoryTests(unittest.TestCase):
    def test_schema_is_migration_eight(self) -> None:
        self.assertEqual([version for version, _ in MIGRATIONS], list(range(1, 9)))
        self.assertEqual(CURRENT_SCHEMA, 8)

    def test_release_status_does_not_claim_production(self) -> None:
        status = json.loads((ROOT / "docs/release/status.json").read_text(encoding="utf-8"))
        self.assertFalse(status["production_enabled"])
        self.assertEqual(status["classification"], "SYNTHETIC_DEMO_NOT_PRODUCTION")
        self.assertEqual(status["owner_acceptance"], "PENDING")
        self.assertEqual(status["independent_review"], "PENDING")
        self.assertEqual(len(status["phases"]), 42)
        self.assertEqual(status["phase_counts"], {"PASS": 2, "PARTIAL": 40})
        self.assertEqual(status["task_counts"], {"PASS": 80, "PARTIAL": 214})

    def test_every_api_route_is_tenant_scoped(self) -> None:
        from tests.support import Fixture

        fixture = Fixture()
        paths = [route.path for route in fixture.app.routes if route.path.startswith("/v1")]
        self.assertGreaterEqual(len(set(paths)), 80)
        for path in paths:
            self.assertTrue(path.startswith("/v1/tenants/{tenant}/"), path)

    def test_no_publication_or_deployment_route(self) -> None:
        from tests.support import Fixture

        fixture = Fixture()
        paths = [route.path for route in fixture.app.routes if route.path.startswith("/v1")]
        forbidden = [path for path in paths if "publish" in path or "deploy" in path]
        self.assertEqual(forbidden, [])

    def test_build_runtime_avoids_removed_node_transform_mode(self) -> None:
        source = (ROOT / "typescript/build-runtime.mjs").read_text(encoding="utf-8")
        normalized = source.replace(" ", "").replace("\n", "")
        self.assertNotIn("mode:'transform'", normalized)
        self.assertIn("stripTypeScriptTypes", source)


class AutodocArtifactsTests(unittest.TestCase):
    def test_program_and_handoff_documents_exist(self) -> None:
        for relative in (
            "AGENTS.md",
            "docs/autodoc/PROGRAMA-15-CAMPANAS-ULTRAGRANULARES.md",
            "docs/engineering/AUTODOCUMENTACION-EVIDENCIAS-Y-PUBLICACIONES-TECNICAS.md",
        ):
            self.assertTrue((ROOT / relative).is_file(), relative)


if __name__ == "__main__":
    unittest.main()
