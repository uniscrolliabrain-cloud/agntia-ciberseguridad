"""Finite non-blocking span handoff; export failure never changes business permissions."""
import queue
import threading
import time
try:
    from opentelemetry.sdk.trace import SpanProcessor
except ImportError:
    class SpanProcessor:pass

class BoundedSpanProcessor(SpanProcessor):
    def __init__(self,exporter,metrics,*,capacity=128,batch_size=32,start=True):
        if not 1<=capacity<=1024 or not 1<=batch_size<=capacity:raise ValueError('Invalid export bounds')
        self.exporter=exporter;self.metrics=metrics;self.queue=queue.Queue(capacity);self.batch_size=batch_size
        self.stop=threading.Event();self.thread=None
        if start:
            self.thread=threading.Thread(target=self._run,name='agntia-telemetry',daemon=True);self.thread.start()
    def on_start(self,span,parent_context=None):pass
    def _on_ending(self,span):pass
    def on_end(self,span):
        try:self.queue.put_nowait(span)
        except queue.Full:
            with self.metrics.lock:self.metrics.dropped+=1
    def drain_once(self):
        batch=[]
        for _ in range(self.batch_size):
            try:batch.append(self.queue.get_nowait())
            except queue.Empty:break
        if not batch:return
        try:
            result=self.exporter.export(batch)
            if getattr(result,'name',None)!='SUCCESS':
                with self.metrics.lock:self.metrics.dropped+=len(batch);self.metrics.export_failures+=1
        except Exception:
            with self.metrics.lock:self.metrics.dropped+=len(batch);self.metrics.export_failures+=1
        finally:
            for _ in batch:self.queue.task_done()
    def _run(self):
        while not self.stop.wait(.05):self.drain_once()
    def force_flush(self,timeout_millis=500):
        deadline=time.monotonic()+min(max(timeout_millis,0),1000)/1000
        while self.queue.unfinished_tasks and time.monotonic()<deadline:time.sleep(.005)
        return self.queue.unfinished_tasks==0
    def shutdown(self):
        if self.thread:self.force_flush(500)
        self.stop.set()
        if self.thread:self.thread.join(timeout=.5)
        if self.thread is None or not self.thread.is_alive():
            try:self.exporter.shutdown()
            except Exception:pass
        # No unbounded join/network call in the API shutdown path.
