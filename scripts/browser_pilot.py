"""Real browser review/denial/download/tenant switch. Synthetic normalized scan fixture."""
import hashlib
import json
import os
from pathlib import Path
import socket
import threading
import time
import uvicorn
from playwright.sync_api import sync_playwright
from tests.security.support_custody import CustodySetup
from agntia_ciberseguridad.billing.rates import BudgetPolicy
from agntia_ciberseguridad.findings.store import FindingStore
from agntia_ciberseguridad.reviews import ReviewProposal


def main():
    pilot=CustodySetup();pilot.setUp();fixture=pilot.f
    fixture.settings.budget_policies={'tenantA':BudgetPolicy(plan='Lite',fixed_commitment_cents=3000,allocation_review_ref='synthetic-browser-shared-cost')}
    receipt=pilot.submit();row=pilot.store.claim('synthetic-browser')
    pilot.store.complete(row,'synthetic-browser',row['fence'],pilot.result([{'rule_id':'synthetic-ui','path':'file.py','start_line':1,'severity':'high'}]))
    document=pilot.reviewed_document(receipt['id'])
    screens=Path(os.getenv('AGNTIA_BROWSER_EVIDENCE','/tmp/agntia-browser40'));screens.mkdir(parents=True,exist_ok=True)
    server=None;thread=None
    try:
        with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
        server=uvicorn.Server(uvicorn.Config(fixture.app,host='127.0.0.1',port=port,log_level='error',access_log=False))
        thread=threading.Thread(target=server.run,daemon=True);thread.start()
        for _ in range(100):
            if server.started:break
            time.sleep(.02)
        else:raise RuntimeError('Synthetic server not ready')
        with sync_playwright() as playwright:
            args={'headless':True}
            if os.getenv('AGNTIA_CHROMIUM_PATH'):args['executable_path']=os.environ['AGNTIA_CHROMIUM_PATH']
            browser=playwright.chromium.launch(**args);results=[]
            for width,height in ((1440,1000),(390,844)):
                finding=FindingStore(fixture.service).list(pilot.actor,'tenantA')['items'][0]
                proposal=pilot.reviews.propose(pilot.actor,'tenantA',ReviewProposal(finding_id=finding['id'],expected_finding_revision=finding['revision'],action='set_context',reason='Synthetic browser review with source evidence',evidence_ids=[document['id']],exposure='internal',sensitivity='ordinary'),'synthetic-browser')
                page=browser.new_page(viewport={'width':width,'height':height},accept_downloads=True);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                page.goto(f'http://127.0.0.1:{port}/console')
                def login(actor,tenant='tenantA'):
                    page.get_by_label('Organización',exact=True).fill(tenant)
                    page.get_by_label('Credencial de lectura').fill(fixture.tokens[actor])
                    page.get_by_role('button',name='Consultar',exact=True).click()
                    page.get_by_role('status').filter(has_text='Datos de '+tenant).wait_for()
                login('viewerA')
                assert page.get_by_text('exhausted',exact=True).count()==1
                page.get_by_role('button',name=f'set_context · proposed · {proposal["id"][:8]}',exact=True).click()
                page.get_by_role('checkbox').check();page.get_by_role('button',name='Aprobar cambio local').click()
                page.locator('#detail').filter(has_text='403').wait_for()
                login('reviewerA')
                page.get_by_role('button',name=f'set_context · proposed · {proposal["id"][:8]}',exact=True).click()
                assert page.get_by_role('button',name='Aprobar cambio local').is_disabled()
                page.get_by_role('checkbox').check()
                # Download source evidence before human approval; API revalidates access.
                with page.expect_download() as download:
                    page.get_by_role('button',name=f'Evidencia {document["id"][:8]} · descargar vista',exact=True).click()
                assert download.value.suggested_filename==document['id']+'.txt'
                page.get_by_role('button',name='Aprobar cambio local').click()
                page.get_by_role('status').filter(has_text='Revisión registrada').wait_for()
                assert not page.locator('#actions').inner_text()
                login('reviewerA');assert page.get_by_text('exhausted',exact=True).count()==1
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                assert page.evaluate('localStorage.length===0 && sessionStorage.length===0')
                page.screenshot(path=str(screens/f'pilot-{width}.png'),full_page=True)
                login('operatorB','tenantB')
                assert page.locator('#jobs').inner_text()=='Sin ejecuciones. Cobertura no evaluada.'
                assert proposal['id'][:8] not in page.locator('#proposals').inner_text()
                assert 'exhausted' not in page.locator('#overview').inner_text()
                page.get_by_role('button',name='Cerrar sesión').click()
                assert not page.locator('#overview').inner_text()
                assert not page.locator('#proposals').inner_text()
                assert not errors,errors
                results.append({'width':width,'height':height,'viewer_approval_denied':True,'human_review_recorded':True,'source_downloaded':True,'tenant_switch_clears':True,'budget_exhausted_visible':True,'overflow':False,'javascript_errors':0})
                page.close()
            browser.close()
        print(json.dumps({'browser':'real Chromium','scan_input':'synthetic normalized fixture, not a real scanner run','results':results,'screenshots':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in screens.glob('pilot-*.png')}}))
    finally:
        if server:server.should_exit=True
        if thread:thread.join(timeout=3)
        pilot.tearDown()
if __name__=='__main__':main()
