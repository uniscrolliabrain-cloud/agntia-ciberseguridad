"""Run the encrypted lab recovery verification with ephemeral keys; no customer data."""
import json
import sys
import unittest
from tests.integration.test_recovery_lab import RecoveryTests
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RecoveryTests))
print(json.dumps({'synthetic_only':True,'cases':result.testsRun,'success':result.wasSuccessful(),'scope':'Database and referenced ciphertext; source snapshots excluded; restored API blocked','production_restore':'NOT_VERIFIED'}))
sys.exit(not result.wasSuccessful())
