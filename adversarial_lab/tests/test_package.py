import unittest

from support import config

from agntia_adversarial import __version__
from agntia_adversarial.cli import main
from agntia_adversarial.config import LabConfig


class PackageTests(unittest.TestCase):
    def test_version_is_exposed(self):
        self.assertEqual(__version__, "0.1.0")

    def test_config_defaults_deny_network(self):
        self.assertFalse(LabConfig.from_env().allow_network)
        self.assertFalse(LabConfig.from_env().allow_subprocess_providers)

    def test_config_rejects_network(self):
        with self.assertRaises(ValueError):
            LabConfig(data_dir=config.__globals__["Path"]("."), allow_network=True).validate()

    def test_cli_doctor_reports_blocked_tools(self):
        self.assertEqual(main(["doctor"]), 0)


if __name__ == "__main__":
    unittest.main()
