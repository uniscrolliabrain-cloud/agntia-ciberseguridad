"""Real Chromium desktop/mobile against synthetic local API; no customer data."""
import json
import hashlib
import os
from pathlib import Path
import socket
import threading
import time
import uvicorn
from playwright.sync_api import sync_playwright
from tests.support import Fixture

def main():
    fixture=Fixture();screens=Path(os.getenv('AGNTIA_BROWSER_EVIDENCE','/tmp/agntia-browser25'));screens.mkdir(parents=True,exist_ok=True)
    with socket.socket() as socket_:socket_.bind(('127.0.0.1',0));port=socket_.getsockname()[1]
    server=uvicorn.Server(uvicorn.Config(fixture.app,host='127.0.0.1',port=port,log_level='error',access_log=False))
    thread=threading.Thread(target=server.run,daemon=True);thread.start()
    try:
        for _ in range(100):
            if server.started:break
            time.sleep(.02)
        else:raise RuntimeError('Synthetic server not ready')
        with sync_playwright() as playwright:
            args={'headless':True}
            executable=os.getenv('AGNTIA_CHROMIUM_PATH')
            if executable:args['executable_path']=executable
            browser=playwright.chromium.launch(**args)
            results=[]
            for width,height in ((1440,1000),(390,844)):
                page=browser.new_page(viewport={'width':width,'height':height});errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
                page.goto(f'http://127.0.0.1:{port}/console')
                page.get_by_label('Organización',exact=True).fill('tenantA')
                page.get_by_label('Credencial de lectura').fill(fixture.tokens['viewerA'])
                page.get_by_role('button',name='Consultar',exact=True).click()
                page.get_by_role('status').filter(has_text='Datos de tenantA').wait_for()
                assert page.get_by_text('not_tested',exact=True).count()==1
                assert page.get_by_text('not_monitored',exact=True).count()==1
                assert page.locator('#token').input_value()==''
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                assert page.evaluate('localStorage.length')==0
                page.screenshot(path=str(screens/f'console-{width}.png'),full_page=True)
                # A viewer cannot move to a foreign organization through UI input.
                page.get_by_label('Organización',exact=True).fill('tenantB')
                page.get_by_label('Credencial de lectura').fill(fixture.tokens['viewerA'])
                page.get_by_role('button',name='Consultar',exact=True).click()
                page.get_by_role('status').filter(has_text='404').wait_for()
                assert page.locator('#overview').inner_text()==''
                page.get_by_role('button',name='Cerrar sesión').click()
                # A late dashboard response must not repopulate data after logout.
                page.evaluate('() => { window.originalFetch=window.fetch; window.fetch=()=>new Promise(resolve=>{window.resolveDashboard=resolve;}); }')
                page.get_by_label('Organización',exact=True).fill('tenantA')
                page.get_by_label('Credencial de lectura').fill(fixture.tokens['viewerA'])
                page.get_by_role('button',name='Consultar',exact=True).click()
                page.get_by_role('button',name='Cerrar sesión').click()
                page.evaluate('() => { window.resolveDashboard({ok:true,json:async()=>({tenant_id:"tenantA"})});window.fetch=window.originalFetch; }')
                page.wait_for_timeout(50)
                assert page.get_by_role('status').inner_text()=='Sesión cerrada.'
                assert page.locator('#overview').inner_text()==''
                assert not errors,errors
                results.append({'width':width,'height':height,'overflow':False,'cross_tenant_denied':True,'javascript_errors':0,'logout_race_denied':True})
                page.close()
            browser.close()
        print(json.dumps({'browser':'real Chromium','synthetic_only':True,'results':results,'screenshots':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in screens.glob('*.png')}}))
    finally:
        server.should_exit=True;thread.join(timeout=3);fixture.service.telemetry.close();fixture.close()
if __name__=='__main__':main()
