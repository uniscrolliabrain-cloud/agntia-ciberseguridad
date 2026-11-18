"""Worker loop with graceful SIGTERM/SIGINT and no blind re-execution.

The loop claims at most one job per iteration. A shutdown request while a job is in
flight is honoured in two steps: bounded grace so an attempt can finish and persist its
result, then cancellation, which the Worker already records as `reconciliation_required`
with `cleanup_verified=False`. Nothing here retries a job whose external effect is unknown.
"""
import asyncio
import signal

TERMINATION_SIGNALS=(signal.SIGTERM,signal.SIGINT)

class ShutdownWatch:
    """Map SIGTERM/SIGINT to one stop event without losing the previous handlers."""

    def __init__(self,stop,*,signals=TERMINATION_SIGNALS,loop=None):
        if not isinstance(signals,tuple) or not signals:raise ValueError('At least one signal is required')
        self.stop=stop;self.signals=signals;self.loop=loop;self.received=[];self._previous={}

    def __enter__(self):
        self.loop=self.loop or asyncio.get_running_loop()
        for name in self.signals:
            self._previous[name]=signal.getsignal(name)
            signal.signal(name,self._handle)
        return self

    def _handle(self,signum,frame):
        # Signal handlers run in the main thread; the loop may already be scheduled.
        self.received.append(signum)
        self.loop.call_soon_threadsafe(self.stop.set)

    def __exit__(self,*exc_info):
        for name,previous in self._previous.items():signal.signal(name,previous)
        self._previous={}
        return False

async def serve(worker,*,stop=None,interval=1.0,max_iterations=None,shutdown_grace=5.0,on_result=None):
    """Run one bounded iteration at a time and return the persisted job states."""
    if not interval>=0 or not shutdown_grace>=0:raise ValueError('Invalid worker cadence')
    stop=stop or asyncio.Event();iterations=0;results=[]
    while not stop.is_set() and (max_iterations is None or iterations<max_iterations):
        iterations+=1
        attempt=asyncio.create_task(worker.run_once())
        stopper=asyncio.create_task(stop.wait())
        done,_=await asyncio.wait({attempt,stopper},return_when=asyncio.FIRST_COMPLETED)
        interrupted=attempt not in done
        stopper.cancel()
        await asyncio.gather(stopper,return_exceptions=True)
        if interrupted:
            try:result=await asyncio.wait_for(asyncio.shield(attempt),timeout=shutdown_grace)
            except asyncio.TimeoutError:
                attempt.cancel()
                try:await attempt
                except asyncio.CancelledError:pass
                result=None
        else:result=await attempt
        if result is not None:
            results.append(result)
            if on_result is not None:on_result(result)
        if stop.is_set():break
        if interval:
            try:await asyncio.wait_for(stop.wait(),timeout=interval)
            except asyncio.TimeoutError:pass
    return results
