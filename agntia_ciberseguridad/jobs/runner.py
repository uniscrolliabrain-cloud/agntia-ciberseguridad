"""Worker loop with graceful SIGTERM/SIGINT, bounded failure tolerance and no blind re-execution.

The loop claims at most one job per iteration. A shutdown request while a job is in
flight is honoured in two steps: bounded grace so an attempt can finish and persist its
result, then cancellation, which the Worker already records as `reconciliation_required`
with `cleanup_verified=False`. Nothing here retries a job whose external effect is unknown.

A transient failure (a locked database, a restarting dependency) must not kill the loop:
consecutive failures are tolerated up to `max_consecutive_failures` and reported through
`on_error`. A lost lease is not transient -- this loop no longer owns the job -- so it is
re-raised immediately instead of being retried.
"""
import asyncio
import signal

from ..errors import DomainError

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

async def _attempt(worker,stop,shutdown_grace):
    """Run one iteration; a stop request gets bounded grace before cancellation."""
    attempt=asyncio.create_task(worker.run_once())
    stopper=asyncio.create_task(stop.wait())
    try:
        done,_=await asyncio.wait({attempt,stopper},return_when=asyncio.FIRST_COMPLETED)
        interrupted=attempt not in done
        stopper.cancel()
        await asyncio.gather(stopper,return_exceptions=True)
        if not interrupted:return await attempt
        try:return await asyncio.wait_for(asyncio.shield(attempt),timeout=shutdown_grace)
        except asyncio.TimeoutError:
            attempt.cancel()
            try:await attempt
            except asyncio.CancelledError:pass
            return None
    finally:
        # Whatever happened, no task may outlive the iteration that created it.
        for task in (attempt,stopper):
            if not task.done():task.cancel()
        await asyncio.gather(attempt,stopper,return_exceptions=True)

async def serve(worker,*,stop=None,interval=1.0,max_iterations=None,shutdown_grace=5.0,max_consecutive_failures=3,on_result=None,on_error=None):
    """Run one bounded iteration at a time and return the persisted job states."""
    if not interval>=0 or not shutdown_grace>=0:raise ValueError('Invalid worker cadence')
    if max_consecutive_failures is not None and max_consecutive_failures<1:raise ValueError('Invalid failure tolerance')
    stop=stop or asyncio.Event();iterations=0;results=[];failures=0
    while not stop.is_set() and (max_iterations is None or iterations<max_iterations):
        iterations+=1
        try:result=await _attempt(worker,stop,shutdown_grace)
        except DomainError as error:
            if error.code=='stale_lease':raise
            failures+=1
            if on_error is not None:on_error(error)
            if max_consecutive_failures is not None and failures>=max_consecutive_failures:raise
            result=None
        except Exception as error:
            failures+=1
            if on_error is not None:on_error(error)
            if max_consecutive_failures is not None and failures>=max_consecutive_failures:raise
            result=None
        else:
            failures=0
        if result is not None:
            results.append(result)
            if on_result is not None:on_result(result)
        if stop.is_set():break
        if interval:
            try:await asyncio.wait_for(stop.wait(),timeout=interval)
            except asyncio.TimeoutError:pass
    return results
