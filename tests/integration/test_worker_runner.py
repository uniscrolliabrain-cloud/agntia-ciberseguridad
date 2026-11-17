"""Worker loop shutdown: bounded grace, cancellation and real SIGTERM/SIGINT."""
import asyncio
import json
import signal
import subprocess
import sys
import unittest
from types import SimpleNamespace
from tests.integration.test_jobs import Setup

from agntia_ciberseguridad.jobs.runner import ShutdownWatch, serve
from agntia_ciberseguridad.jobs.worker import Worker
from agntia_ciberseguridad.runners.base import Tool

class FakeWorker:
    def __init__(self,delay,*,fail=False):
        self.delay=delay;self.fail=fail;self.calls=0;self.cancelled=0
    async def run_once(self):
        self.calls+=1
        try:await asyncio.sleep(self.delay)
        except asyncio.CancelledError:
            self.cancelled+=1
            raise
        if self.fail:raise RuntimeError('synthetic iteration failure')
        return {'id':'job-%02d'%self.calls,'state':'completed'}

class ServeTests(unittest.IsolatedAsyncioTestCase):
    async def test_stop_before_first_iteration_claims_nothing(self):
        stop=asyncio.Event();stop.set();worker=FakeWorker(0)
        self.assertEqual(await serve(worker,stop=stop),[])
        self.assertEqual(worker.calls,0)

    async def test_stop_during_attempt_finishes_it_within_grace(self):
        stop=asyncio.Event();worker=FakeWorker(0.05)
        task=asyncio.create_task(serve(worker,stop=stop,shutdown_grace=1))
        await asyncio.sleep(0.01);stop.set()
        results=await asyncio.wait_for(task,timeout=2)
        self.assertEqual([r['state'] for r in results],['completed'])
        self.assertEqual(worker.cancelled,0)

    async def test_stop_after_grace_cancels_the_attempt_instead_of_waiting(self):
        stop=asyncio.Event();worker=FakeWorker(30)
        task=asyncio.create_task(serve(worker,stop=stop,shutdown_grace=0.05))
        await asyncio.sleep(0.01);stop.set()
        results=await asyncio.wait_for(task,timeout=2)
        self.assertEqual(results,[])
        self.assertEqual(worker.cancelled,1)

    async def test_iteration_failure_propagates_and_stops_claiming(self):
        worker=FakeWorker(0,fail=True)
        with self.assertRaises(RuntimeError):await serve(worker,max_iterations=3)
        self.assertEqual(worker.calls,1)

    async def test_sigterm_and_sigint_set_the_stop_event_and_restore_handlers(self):
        original={name:signal.getsignal(name) for name in (signal.SIGTERM,signal.SIGINT)}
        stop=asyncio.Event()
        with ShutdownWatch(stop) as watch:
            signal.raise_signal(signal.SIGTERM)
            await asyncio.wait_for(stop.wait(),timeout=2)
            stop.clear()
            signal.raise_signal(signal.SIGINT)
            await asyncio.wait_for(stop.wait(),timeout=2)
        self.assertEqual(watch.received,[signal.SIGTERM,signal.SIGINT])
        for name,handler in original.items():self.assertIs(signal.getsignal(name),handler)

CHILD=r'''
import asyncio,json,signal
from agntia_ciberseguridad.jobs.runner import ShutdownWatch,serve
class W:
    def __init__(self):self.cancelled=0
    async def run_once(self):
        print('attempt',flush=True)
        try:await asyncio.sleep(30)
        except asyncio.CancelledError:
            self.cancelled+=1;print('cancelled',flush=True);raise
async def main():
    stop=asyncio.Event();worker=W()
    with ShutdownWatch(stop) as watch:results=await serve(worker,stop=stop,shutdown_grace=0.05,interval=0)
    print(json.dumps({'results':results,'cancelled':worker.cancelled,'signals':watch.received}),flush=True)
asyncio.run(main())
'''

class ProcessSignalTests(unittest.TestCase):
    def test_real_sigterm_stops_a_worker_process_without_killing_it_abruptly(self):
        process=subprocess.Popen([sys.executable,'-c',CHILD],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            self.assertEqual(process.stdout.readline().strip(),'attempt')
            process.send_signal(signal.SIGTERM)
            stdout,stderr=process.communicate(timeout=15)
        finally:
            if process.poll() is None:process.kill()
        self.assertEqual(process.returncode,0,stderr)
        self.assertIn('cancelled',stdout)
        report=json.loads(stdout.splitlines()[-1])
        self.assertEqual(report['results'],[])
        self.assertEqual(report['cancelled'],1)
        self.assertEqual(report['signals'],[signal.SIGTERM])

class StopAfterClaimTests(Setup,unittest.TestCase):
    def test_shutdown_cancellation_is_persisted_as_reconciliation_required(self):
        receipt=self.submit()
        async def scan(*args,**kwargs):await asyncio.sleep(30)
        scanner=SimpleNamespace(runner=SimpleNamespace(images={Tool.gitleaks:SimpleNamespace(policy_hash='a'*64)}),scan=scan)
        worker=Worker(self.store,scanner,'workerA',lease_seconds=4)
        async def scenario():
            stop=asyncio.Event()
            task=asyncio.create_task(serve(worker,stop=stop,shutdown_grace=0.05))
            await asyncio.sleep(0.05);stop.set()
            return await asyncio.wait_for(task,timeout=5)
        self.assertEqual(asyncio.run(scenario()),[])
        state=self.store.get(self.actor,'tenantA',receipt['id'])
        self.assertEqual(state['state'],'reconciliation_required')
        self.assertEqual(state['error_code'],'worker_cancelled')
        with self.f.service.db.connection(readonly=True) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM job_results').fetchone()[0],0)

if __name__=='__main__':unittest.main()
