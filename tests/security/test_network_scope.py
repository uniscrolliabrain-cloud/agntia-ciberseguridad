from pathlib import Path
import unittest

from agntia_ciberseguridad.errors import DomainError
from agntia_ciberseguridad.network_policy import local_target,pin_target,validate_redirect
from tests.support import Fixture


class NetworkScopeTests(unittest.TestCase):
    def setUp(self):self.f=Fixture();self.target=self.f.settings.targets['webA']
    def tearDown(self):self.f.close()

    def test_pin_all_dns_answers_and_no_metadata(self):
        pinned=pin_target(self.target,self.f.settings,lambda h,p:['192.0.2.10','192.0.2.11'])
        self.assertEqual(pinned.address,'192.0.2.10');self.assertEqual(pinned.host,'approved.example.invalid')
        for addresses in (['192.0.2.10','169.254.169.254'],['0.0.0.0'],['::ffff:169.254.169.254'],[],['127.0.0.1']):
            with self.assertRaises(DomainError):pin_target(self.target,self.f.settings,lambda h,p:addresses)

    def test_metadata_denied_even_with_broad_allowlist(self):
        target=self.target.model_copy(update={'allowed_networks':['0.0.0.0/0','::/0']})
        for address in ('169.254.169.254','169.254.170.2','100.100.100.200','fd00:ec2::254','224.0.0.1','::'):
            with self.assertRaises(DomainError):pin_target(target,self.f.settings,lambda h,p:[address])

    def test_url_credentials_redirect_and_path_cannot_expand(self):
        for url in ('https://user:password@approved.example.invalid/app','http://approved.example.invalid/app','https://approved.example.invalid:8443/app','https://approved.example.invalid/app?token=hidden','https://approved.example.invalid/app#token','https://approved.example.invalid/app/%252e%252e/private'):
            with self.assertRaises(DomainError):pin_target(self.target.model_copy(update={'location':url}),self.f.settings,lambda h,p:['192.0.2.10'])
        calls=[]
        for redirect in ('https://other.example.invalid/app','/admin','/%2e%2e/admin','//169.254.169.254/latest'):
            with self.assertRaises(DomainError):validate_redirect(self.target,self.target.location,redirect,self.f.settings,lambda h,p:(calls.append(h) or ['192.0.2.10']))
        self.assertEqual(calls,[])
        self.assertEqual(validate_redirect(self.target,self.target.location,'/app/report',self.f.settings,lambda h,p:['192.0.2.10']).address,'192.0.2.10')

    def test_insecure_loopback_requires_both_lab_flags(self):
        target=self.target.model_copy(update={'location':'http://localhost:8010/app','allowed_ports':[8010],'allowed_networks':['127.0.0.0/8'],'allow_insecure_lab':True,'allow_loopback_lab':True})
        self.assertEqual(pin_target(target,self.f.settings,lambda h,p:['127.0.0.1']).address,'127.0.0.1')
        with self.assertRaises(DomainError):pin_target(target,self.f.settings.model_copy(update={'lab_mode':False}),lambda h,p:['127.0.0.1'])

    def test_local_path_and_symlink_escape_denied(self):
        self.assertEqual(local_target(self.f.settings.targets['repoA'],self.f.settings),self.f.repo)
        outside=self.f.root/'outside';outside.mkdir();link=self.f.workspace/'escaped';link.symlink_to(outside,target_is_directory=True)
        with self.assertRaises(DomainError):local_target(self.f.settings.targets['repoA'].model_copy(update={'location':str(link)}),self.f.settings)
        with self.assertRaises(DomainError):local_target(self.f.settings.targets['repoA'].model_copy(update={'location':'../outside'}),self.f.settings)
