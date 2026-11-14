"""Reproducible synthetic cross-component journeys. No external scanner/customer call."""
import json
import sys
import unittest
from tests.e2e.test_pilot_journeys import PilotJourneys
suite=unittest.defaultTestLoader.loadTestsFromTestCase(PilotJourneys)
result=unittest.TextTestRunner(verbosity=2).run(suite)
print(json.dumps({'synthetic_only':True,'test_cases':result.testsRun,'passed':result.testsRun-len(result.failures)-len(result.errors)-len(result.skipped),'scan_input':'fixture normalized results, real scanner contracts run separately in Docker CI','production_gate':'NOT_ACCEPTED'}))
sys.exit(not result.wasSuccessful())
