"""Bounded-label Prometheus exposition; no tenant/user/URL labels or security score."""
import math
import threading

OPERATIONS={'read','write','health','metrics','other'}
TOOLS={'gitleaks','osv','semgrep','trivy','other'}
STATES={'pending','running','completed','partial','failed','cancelled','blocked','reconciliation_required','other'}
BUCKETS=(.005,.01,.025,.05,.1,.25,.5,1,2,5,10)

class Metrics:
    def __init__(self):
        self.lock=threading.Lock();self.requests={};self.latency={};self.jobs={};self.coverage={};self.dropped=0;self.export_failures=0
        self.last_scan=0
    def request(self,operation,status,seconds):
        operation=operation if operation in OPERATIONS else 'other'
        status=str(status//100)+'xx' if type(status)is int and status//100 in (2,4,5) else 'other'
        seconds=float(seconds)
        if not math.isfinite(seconds) or seconds<0:seconds=0
        with self.lock:
            key=(operation,status);self.requests[key]=self.requests.get(key,0)+1
            hist=self.latency.setdefault(operation,{'count':0,'sum':0,'buckets':[0]*len(BUCKETS)})
            hist['count']+=1;hist['sum']+=seconds
            for i,bound in enumerate(BUCKETS):hist['buckets'][i]+=int(seconds<=bound)
    def job(self,tool,state):
        tool=tool if tool in TOOLS else 'other';state=state if state in STATES else 'other'
        with self.lock:
            key=(tool,state);self.jobs[key]=self.jobs.get(key,0)+1
    def scan(self,result_status):
        import time
        coverage='incomplete' if result_status in ('error','partial','stale') else 'declared_scope_complete' if result_status in ('findings','no_findings') else 'unknown'
        with self.lock:
            self.coverage[coverage]=self.coverage.get(coverage,0)+1;self.last_scan=time.time()
    def export(self):
        with self.lock:
            lines=['# HELP agntia_http_requests_total Completed API requests, not scans.','# TYPE agntia_http_requests_total counter']
            for (op,status),value in sorted(self.requests.items()):lines.append(f'agntia_http_requests_total{{operation="{op}",status="{status}"}} {value}')
            lines+=['# HELP agntia_http_duration_seconds In-process API latency.','# TYPE agntia_http_duration_seconds histogram']
            for op,hist in sorted(self.latency.items()):
                for bound,value in zip(BUCKETS,hist['buckets']):lines.append(f'agntia_http_duration_seconds_bucket{{operation="{op}",le="{bound}"}} {value}')
                lines.append(f'agntia_http_duration_seconds_bucket{{operation="{op}",le="+Inf"}} {hist["count"]}')
                lines.append(f'agntia_http_duration_seconds_count{{operation="{op}"}} {hist["count"]}')
                lines.append(f'agntia_http_duration_seconds_sum{{operation="{op}"}} {hist["sum"]}')
            lines+=['# TYPE agntia_job_transitions_total counter']
            for (tool,state),value in sorted(self.jobs.items()):lines.append(f'agntia_job_transitions_total{{tool="{tool}",state="{state}"}} {value}')
            lines+=['# HELP agntia_scan_coverage_total Completion of declared scope, never percentage secure.','# TYPE agntia_scan_coverage_total counter']
            for coverage,value in sorted(self.coverage.items()):lines.append(f'agntia_scan_coverage_total{{coverage="{coverage}"}} {value}')
            lines+=['# TYPE agntia_telemetry_dropped_total counter',f'agntia_telemetry_dropped_total {self.dropped}',
                    '# TYPE agntia_telemetry_export_failures_total counter',f'agntia_telemetry_export_failures_total {self.export_failures}',
                    '# TYPE agntia_last_scan_timestamp_seconds gauge',f'agntia_last_scan_timestamp_seconds {self.last_scan}']
            return '\n'.join(lines)+'\n'
    def series_count(self):return sum(not line.startswith('#') and bool(line) for line in self.export().splitlines())
