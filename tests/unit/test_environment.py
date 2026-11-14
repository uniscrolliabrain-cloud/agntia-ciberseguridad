"""Inventory must preserve an existing checkout, including unrelated edits."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

class EnvironmentTests(unittest.TestCase):
    def test_inventory_preserves_unrelated_edits_and_reports_unavailable_docker(self):
        source=Path(__file__).resolve().parents[2]/'scripts/verify_environment.py'
        spec=importlib.util.spec_from_file_location('verify_environment',source)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            subprocess.run(['git','init','-q',str(root)],check=True)
            tracked=root/'unrelated.txt';tracked.write_text('Original\n')
            subprocess.run(['git','-C',str(root),'add','unrelated.txt'],check=True)
            subprocess.run(['git','-C',str(root),'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','fixture'],check=True)
            tracked.write_text('Unrelated owner change\n')
            untouched=root/'untracked-owner.txt';untouched.write_text('Keep me\n')
            original_command=module.command
            def command(argv,**kwargs):
                if argv[0]=='docker':return {'exit_code':1,'error_class':'permission_denied','output':''}
                return original_command(argv,**kwargs)
            with patch.object(module,'ROOT',root),patch.object(module,'command',command):inventory=module.collect()
            self.assertEqual(tracked.read_text(),'Unrelated owner change\n')
            self.assertEqual(untouched.read_text(),'Keep me\n')
            self.assertIn('unrelated.txt',inventory['git_status'])
            self.assertEqual(inventory['docker_local_socket']['error_class'],'permission_denied')
            self.assertEqual(inventory['security_scans_executed'],0)
