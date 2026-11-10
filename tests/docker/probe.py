#!/usr/local/bin/python
"""Synthetic sandbox probes only; no targets outside the isolated test container."""
import errno
import json
import os
from pathlib import Path
import socket
import time

mode=Path('/input/mode.txt').read_text().strip()
if mode=='timeout':time.sleep(5)
elif mode=='output':print('x'*200000)
elif mode=='pids':
    children=[]
    try:
        for _ in range(100):
            try:pid=os.fork()
            except OSError as error:
                if error.errno!=errno.EAGAIN:raise
                break
            if pid==0:time.sleep(.2);os._exit(0)
            children.append(pid)
    finally:
        for pid in children:os.waitpid(pid,0)
    print(json.dumps({'children':len(children),'pids_limit_applied':len(children)<100}))
else:
    def cannot_write(path):
        try:Path(path).write_text('forbidden');return False
        except OSError:return True
    sock=socket.socket();sock.settimeout(.2)
    try:sock.connect(('192.0.2.1',80));network_blocked=False
    except OSError:network_blocked=True
    finally:sock.close()
    status=Path('/proc/self/status').read_text()
    limits=Path('/sys/fs/cgroup')
    memory=(limits/'memory.max').read_text().strip()
    pids=(limits/'pids.max').read_text().strip()
    cpu=(limits/'cpu.max').read_text().split()
    print(json.dumps({'memory_limit_present':memory.isdigit() and int(memory)<=256*1024*1024,
          'pid_limit_present':pids.isdigit() and int(pids)<=32,
          'cpu_limit_present':cpu[0]!='max' and int(cpu[0])/int(cpu[1])<=1,
          'no_new_privileges':'NoNewPrivs:\t1' in status,
          'capabilities_dropped':'CapEff:\t0000000000000000' in status,
          'uid':os.getuid(),'root_readonly':cannot_write('/forbidden'),
          'input_readonly':cannot_write('/input/forbidden'),'socket_absent':not Path('/var/run/docker.sock').exists(),
          'network_blocked':network_blocked,'host_secret_absent':'AGNTIA_HOST_SECRET' not in os.environ,
          'proxy_absent':not any(k.lower().endswith('proxy') for k in os.environ)}))
