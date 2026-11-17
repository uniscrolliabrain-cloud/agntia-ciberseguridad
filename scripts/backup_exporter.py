"""Prometheus textfile exporter for the lab backup ledger.

The API never performs a backup, so it must not invent a backup series either. A separate
process reads the ledger and writes the only backup signal the alert rules may trust. The
write is atomic: a crash mid-write cannot leave a truncated file that a scrape could read
as a fresh success. When nothing is known, the series says zero and the stale rule fires,
because "no news" is not "restored last night".
"""
import argparse
import os
from pathlib import Path
import sys
import tempfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.backup_ledger import summarize


def render(summary):
    last_success=0.0 if summary['last_success'] is None else float(summary['last_success'])
    last_attempt=0.0 if summary['last_attempt'] is None else float(summary['last_attempt'])
    lines=['# HELP agntia_backup_last_success_timestamp_seconds Last verified encrypted lab backup; 0 when none is known.',
           '# TYPE agntia_backup_last_success_timestamp_seconds gauge',
           f'agntia_backup_last_success_timestamp_seconds {last_success!r}',
           '# HELP agntia_backup_last_attempt_timestamp_seconds Last recorded attempt, successful or not.',
           '# TYPE agntia_backup_last_attempt_timestamp_seconds gauge',
           f'agntia_backup_last_attempt_timestamp_seconds {last_attempt!r}',
           '# HELP agntia_backup_consecutive_failures Attempts since the last verified success.',
           '# TYPE agntia_backup_consecutive_failures gauge',
           f"agntia_backup_consecutive_failures {summary['consecutive_failures']!r}",
           '# HELP agntia_backup_ledger_corrupt_total Lines the exporter could not verify; unknown, not healthy.',
           '# TYPE agntia_backup_ledger_corrupt_total gauge',
           f"agntia_backup_ledger_corrupt_total {summary['corrupt']!r}"]
    return '\n'.join(lines)+'\n'


def write(ledger,destination,clock=None):
    destination=Path(destination)
    if not destination.parent.is_dir():raise ValueError('Textfile directory does not exist: '+str(destination.parent))
    payload=render(summarize(ledger,clock=clock))
    handle,path=tempfile.mkstemp(dir=destination.parent,prefix='.agntia-backup-',suffix='.tmp')
    try:
        with os.fdopen(handle,'w',encoding='utf-8') as stream:
            stream.write(payload);stream.flush();os.fsync(stream.fileno())
        os.chmod(path,0o644);os.replace(path,destination)
    except BaseException:
        if os.path.exists(path):os.unlink(path)
        raise
    return payload


def main(argv=None):
    parser=argparse.ArgumentParser(description='Export the lab backup ledger as a Prometheus textfile.')
    parser.add_argument('--ledger',required=True);parser.add_argument('--destination',required=True)
    options=parser.parse_args(argv)
    try:write(options.ledger,options.destination)
    except (ValueError,OSError) as error:raise SystemExit(str(error))
    print(str(options.destination))


if __name__=='__main__':main()
