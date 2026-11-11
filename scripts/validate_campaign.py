"""Validate a planned campaign and its DAG; never executes security tests."""
from collections import Counter
import json
from pathlib import Path, PurePosixPath

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'docs/campaigns/2026-11-10-seven-days'

def check(ok,message):
    if not ok:raise SystemExit(message)

def acyclic(graph):
    visited=set();active=set()
    def visit(node):
        check(node not in active,'Dependency cycle at '+node)
        if node in visited:return
        active.add(node)
        for parent in graph[node]:
            check(parent in graph,'Missing dependency: '+parent)
            visit(parent)
        active.remove(node);visited.add(node)
    for node in graph:visit(node)

def main():
    plan=json.loads((FOLDER/'campaign.json').read_text(encoding="utf-8"))
    phases=plan['phases'];check(len(phases)==plan['phase_count']==42,'Expected42 phases')
    check({p['day'] for p in phases}==set(range(1,8)),'Expected7 days')
    counts=Counter(p['day'] for p in phases);check(all(v==6 for v in counts.values()),'Expected6 phases/day')
    phase_map={p['id']:p for p in phases};check(len(phase_map)==42,'Duplicate phaseID')
    task_graph={};test_ids=set();tasks=[]
    for p in phases:
        check(p['priority'] in ('M0','M1'),'Invalid priority')
        check(len(p['tasks'])==7 and len(p['test_cases'])==2,'Expected7 tasks/2 scenarios per phase')
        for field in ('objective','business_contract','rollback','planned_files','required_evidence'):
            check(bool(p[field]),'Missing phase field '+field)
        for f in p['planned_files']:
            path=PurePosixPath(f)
            check(not path.is_absolute() and '..' not in path.parts,'Unsafe planned file path')
        for d in p['depends_on']:
            check(d in phase_map,'Missing phase dependency '+d)
            check(phase_map[d]['day']<=p['day'],'Dependency scheduled after consumer')
            if p['priority']=='M0':check(phase_map[d]['priority']=='M0','M0 unexpectedly requires deferredM1 '+d)
        for i,t in enumerate(p['tasks'],1):
            check(t['id']==p['id']+'T'+str(i),'Task numbering mismatch')
            check(t['id'] not in task_graph,'Duplicate taskID')
            check(len(t['action'].strip())>=30,'Task action too vague')
            task_graph[t['id']]=t['depends_on'];tasks.append(t)
        for t in p['test_cases']:
            check(t['id'] not in test_ids and bool(t['scenario']),'Invalid test scenario')
            test_ids.add(t['id'])
    acyclic({p['id']:p['depends_on'] for p in phases});acyclic(task_graph)
    check(len(tasks)==plan['task_count']==294,'Expected294 tasks')
    check(len(test_ids)==plan['test_case_count']==84,'Expected84 scenarios')
    for day in range(1,8):
        content=(FOLDER/f'{day:02d}-dia-{day}.md').read_text(encoding="utf-8")
        for p in phases:
            if p['day']==day:
                for t in p['tasks']:check(t['id'] in content,'Task missing from day documentation')
    print(json.dumps({'status':'PASS','scope':'campaign structure, contracts, IDs and dependency graph only','days':7,'phases':42,'tasks':294,'planned_gate_scenarios':84,'phase_states':dict(Counter(p['status'] for p in phases)),'security_tests_executed_by_this_validator':0},ensure_ascii=False))

if __name__=='__main__':main()
