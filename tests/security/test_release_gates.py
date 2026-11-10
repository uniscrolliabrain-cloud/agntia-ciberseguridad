import json
from pathlib import Path
import unittest
from agntia_ciberseguridad.errors import DomainError
from agntia_ciberseguridad.safety import ReleaseGates

class SafetyGateTests(unittest.TestCase):
    def test_missing_review_or_sandbox_never_activates_customer_execution(self):
        for gates in (ReleaseGates(),ReleaseGates(True,False,True),ReleaseGates(False,True,True),ReleaseGates(True,True,False)):
            with self.assertRaises(DomainError) as error:gates.require_customer_execution()
            self.assertEqual(error.exception.code,'release_gate_blocked')
        ReleaseGates(True,True,True).require_customer_execution()

    def test_every_boundary_has_benign_adversarial_cases_and_owner(self):
        catalog=json.loads((Path(__file__).parent/'scenario_catalog.json').read_text())
        self.assertGreaterEqual(len(catalog['boundaries']),8)
        for boundary in catalog['boundaries']:
            self.assertTrue(boundary['benign']);self.assertTrue(boundary['adversarial']);self.assertTrue(boundary['owner'])
        self.assertFalse(catalog['independent_review_verified'])
