import json
import unittest
from unittest.mock import patch

from agntia_ciberseguridad.config import Settings
from agntia_ciberseguridad.contracts import AssetCreate, AuditPreview, GrantCreate
from tests.support import Fixture


class ContractTests(unittest.TestCase):
    def test_closed_fields_and_schema_roundtrip(self):
        value=AssetCreate(target_ref='repoA',kind='repository',display_name='Fixture')
        self.assertEqual(AssetCreate.model_validate_json(value.model_dump_json()),value)
        self.assertFalse(AssetCreate.model_json_schema()['additionalProperties'])
        for field in ('tenant_id','actor_id','context','shell','base_url'):
            with self.assertRaises(ValueError):AssetCreate(**{**value.model_dump(),field:'forbidden'})

    def test_money_is_strict_integer_and_nonfinite_rejected(self):
        data={'asset_id':'a'*32,'grant_id':'b'*32,'profile':'static_read'}
        for amount in (1.1,1.0,'1',True,float('nan'),float('inf'),-1):
            with self.assertRaises(ValueError):AuditPreview(**data,maximum_cost_cents=amount)
        self.assertEqual(AuditPreview(**data,maximum_cost_cents=0).maximum_cost_cents,0)

    def test_grant_requires_timezone_and_bounded_window(self):
        fixture=Fixture()
        try:
            good=fixture.grant_body('a'*32)
            self.assertEqual(GrantCreate.model_validate(good).profile.value,'static_read')
            for change in ({'starts_at':'2026-01-01T00:00:00'}, {'expires_at':good['starts_at']}, {'expires_at':'2099-01-01T00:00:00Z'}):
                with self.assertRaises(ValueError):GrantCreate.model_validate({**good,**change})
        finally:fixture.close()

    def test_no_implicit_configuration_and_ambiguous_principal_denied(self):
        with patch.dict('os.environ',{'AGNTIA_CYBER_CONFIG_FILE':''}):
            with self.assertRaisesRegex(ValueError,'must reference'):Settings.from_env()
        fixture=Fixture()
        try:
            values=fixture.settings.model_dump(mode='json');values['principals'].append(values['principals'][0])
            with self.assertRaises(ValueError):Settings.model_validate(values)
            values=fixture.settings.model_dump(mode='json');values['targets']['repoA']['tenant_id']='foreign'
            with self.assertRaises(ValueError):Settings.model_validate(values)
        finally:fixture.close()
