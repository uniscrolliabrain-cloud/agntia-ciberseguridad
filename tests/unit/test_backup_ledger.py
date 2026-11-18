"""Backup ledger and textfile exporter: append-only, fail-closed, atomic, secret-free."""
from pathlib import Path
import os
import stat
import tempfile
import unittest

import scripts.backup_exporter as backup_exporter
import scripts.backup_ledger as backup_ledger

DIGEST='a'*64

class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory();self.root=Path(self.directory.name)
        self.path=self.root/'ledger.jsonl'
    def tearDown(self):self.directory.cleanup()

    def test_success_requires_a_digest_and_reasons_are_bounded(self):
        with self.assertRaises(ValueError):backup_ledger.record(self.path,'success')
        with self.assertRaises(ValueError):backup_ledger.record(self.path,'failure',digest=DIGEST)
        with self.assertRaises(ValueError):backup_ledger.record(self.path,'failure',reason='Backup Key Missing')
        with self.assertRaises(ValueError):backup_ledger.record(self.path,'failure',reason='x'*41)
        with self.assertRaises(ValueError):backup_ledger.record(self.path,'maybe',reason='timeout')
        with self.assertRaises(ValueError):backup_ledger.record(self.path,'success',digest='A'*64)
        self.assertFalse(self.path.exists())

    def test_append_only_private_file_keeps_every_attempt(self):
        backup_ledger.record(self.path,'failure',reason='backup_key_unavailable',clock=lambda:1000.0)
        backup_ledger.record(self.path,'success',digest=DIGEST,clock=lambda:2000.0)
        lines=self.path.read_text().splitlines()
        self.assertEqual(len(lines),2)
        self.assertEqual(stat.S_IMODE(self.path.stat().st_mode),0o600)
        summary=backup_ledger.summarize(self.path,clock=lambda:2100.0)
        self.assertEqual((summary['records'],summary['corrupt']),(2,0))
        self.assertEqual(summary['last_success'],2000.0)
        self.assertEqual(summary['consecutive_failures'],0)
        self.assertEqual(summary['age_seconds'],100.0)

    def test_absence_and_corruption_are_unknown_not_success(self):
        empty=backup_ledger.summarize(self.path,clock=lambda:1000.0)
        self.assertEqual((empty['last_success'],empty['records'],empty['corrupt'],empty['age_seconds']), (None,0,0,None))
        self.path.write_text('{"schema_version":1,"outcome":"success","timestamp":900}\nnot json\n')
        summary=backup_ledger.summarize(self.path,clock=lambda:1000.0)
        self.assertIsNone(summary['last_success'])
        self.assertEqual((summary['records'],summary['valid_records'],summary['corrupt']),(2,0,2))

    def test_consecutive_failures_since_the_last_success(self):
        backup_ledger.record(self.path,'success',digest=DIGEST,clock=lambda:1000.0)
        backup_ledger.record(self.path,'failure',reason='backup_busy',clock=lambda:2000.0)
        backup_ledger.record(self.path,'failure',reason='backup_integrity',clock=lambda:3000.0)
        summary=backup_ledger.summarize(self.path,clock=lambda:3000.0)
        self.assertEqual(summary['consecutive_failures'],2)
        self.assertEqual(summary['last_success'],1000.0)
        self.assertEqual(summary['last_attempt'],3000.0)

class ExporterTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory();self.root=Path(self.directory.name)
        self.path=self.root/'ledger.jsonl';self.target=self.root/'agntia-backup.prom'
    def tearDown(self):self.directory.cleanup()

    def test_unknown_backup_exports_zero_which_the_rule_reads_as_stale(self):
        payload=backup_exporter.write(self.path,self.target,clock=lambda:1000.0)
        values=self.samples(payload)
        self.assertEqual(values['agntia_backup_last_success_timestamp_seconds'],0.0)
        self.assertEqual(values['agntia_backup_last_attempt_timestamp_seconds'],0.0)
        self.assertEqual(values['agntia_backup_consecutive_failures'],0.0)
        self.assertEqual(values['agntia_backup_ledger_corrupt_total'],0.0)
        self.assertEqual(len(values),4,'the exporter must expose one bounded backup series per fact')

    def test_atomic_write_leaves_no_temporary_file_behind(self):
        backup_ledger.record(self.path,'success',digest=DIGEST,clock=lambda:500.0)
        backup_exporter.write(self.path,self.target,clock=lambda:600.0)
        self.assertEqual([path.name for path in self.root.iterdir()].count(self.target.name),1)
        self.assertFalse([path for path in self.root.iterdir() if path.name.startswith('.agntia-backup-')])
        self.assertEqual(self.samples(self.target.read_text())['agntia_backup_last_success_timestamp_seconds'],500.0)

    def test_missing_textfile_directory_is_an_error_not_a_silent_stale_file(self):
        with self.assertRaises(ValueError):backup_exporter.write(self.path,self.root/'absent'/'agntia-backup.prom')
        self.assertFalse(self.target.exists())

    @staticmethod
    def samples(text):
        return {line.split(' ')[0]:float(line.split(' ')[1]) for line in text.splitlines() if line and not line.startswith('#')}

if __name__=='__main__':unittest.main()
