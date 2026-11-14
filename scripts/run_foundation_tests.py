"""Execute the real unittest suite and write sanitized checkpoint evidence."""
import argparse
from datetime import datetime,timezone
import hashlib
import io
import json
import logging
from pathlib import Path
import platform
import time
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    stream=io.StringIO();handler=logging.StreamHandler(stream)
    logger=logging.getLogger('agntia.security');logger.addHandler(handler)
    start=time.perf_counter()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.discover(str(ROOT/'tests')))
    elapsed=time.perf_counter()-start
    logger.removeHandler(handler)
    args.output.mkdir(parents=True,exist_ok=True)
    log=args.output/'tests.txt';log.write_text(stream.getvalue())
    report={'at':datetime.now(timezone.utc).isoformat(),'command':'python scripts/run_foundation_tests.py --output '+str(args.output),
        'python':platform.python_version(),'executed':result.testsRun,'passed':result.testsRun-len(result.errors)-len(result.failures)-len(result.skipped),
        'failed':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'elapsed_seconds':round(elapsed,6),
        'status':'PASS' if result.wasSuccessful() else 'FAIL','security_scanners_executed':0,'docker_tests_executed':0,
        'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest(),
        'scope':'Real SQLite, pure network preflight with injected DNS, ASGI API. No security scan or external target.'}
    (args.output/'tests.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
    raise SystemExit(not result.wasSuccessful())
if __name__=='__main__':main()
