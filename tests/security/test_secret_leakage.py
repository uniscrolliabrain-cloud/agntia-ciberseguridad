"""A secret value must never reach operational logs, even when callers pass it by mistake."""
import os
import unittest
from tests.security.test_observability_controls import NewSetup
from agntia_ciberseguridad.util import canonical

class SecretLeakageTests(NewSetup, unittest.TestCase):
    def test_env_secret_is_discarded_by_closed_log_schema(self):
        sentinel='AGNTIA_LEAK_CANARY_'+'Z'*40
        os.environ['CYBER_LEAK_CANARY']=sentinel
        try:
            self.logs.record('tenantA',event='request.rejected',component='api',level='error',code='auth',
                correlation_id='0'*8+'-0000-0000-0000-'+'0'*12,
                authorization='Bearer '+sentinel,payload={'secret':sentinel},exception=sentinel)
        finally:
            os.environ.pop('CYBER_LEAK_CANARY',None)
        rows=self.logs.search(self.owner,'tenantA')
        self.assertTrue(rows)
        self.assertNotIn(sentinel,canonical(rows))
        self.assertNotIn('authorization',canonical(rows).lower())
