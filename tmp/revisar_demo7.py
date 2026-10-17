"""Browser acceptance review using Edge CDP and only the Python standard library."""
from pathlib import Path
import base64
import json
import os
import re
import socket
import shutil
import struct
import subprocess
import tempfile
import time
import urllib.request
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'tmp/demo7'
OUT.mkdir(exist_ok=True)

class CDP:
    def __init__(self,url):
        u=urlsplit(url)
        self.sock=socket.create_connection((u.hostname,u.port),timeout=15)
        self.sock.sendall((f'GET {u.path} HTTP/1.1\r\nHost: {u.hostname}:{u.port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: '+base64.b64encode(os.urandom(16)).decode()+'\r\nSec-WebSocket-Version: 13\r\n\r\n').encode())
        response=b''
        while b'\r\n\r\n' not in response:response+=self.sock.recv(1)
        if not response.startswith(b'HTTP/1.1 101 '):raise RuntimeError(response.decode())
        self.id=0
        self.errors=[]
    def read(self,n):
        data=b''
        while len(data)<n:
            chunk=self.sock.recv(n-len(data))
            if not chunk:raise RuntimeError('CDP disconnected')
            data+=chunk
        return data
    def call(self,method,params=None):
        self.id+=1
        data=json.dumps({'id':self.id,'method':method,'params':params or {}}).encode()
        n=len(data)
        header=bytes([129,128+n]) if n<126 else bytes([129,254])+struct.pack('!H',n) if n<65536 else bytes([129,255])+struct.pack('!Q',n)
        mask=os.urandom(4)
        self.sock.sendall(header+mask+bytes(x^mask[i%4] for i,x in enumerate(data)))
        while True:
            first,second=self.read(2)
            size=second&127
            if size==126:size=struct.unpack('!H',self.read(2))[0]
            elif size==127:size=struct.unpack('!Q',self.read(8))[0]
            masking=self.read(4) if second&128 else None
            payload=self.read(size)
            if masking:payload=bytes(x^masking[i%4] for i,x in enumerate(payload))
            if first&15!=1:continue
            msg=json.loads(payload)
            if msg.get('method')=='Runtime.exceptionThrown':self.errors.append(msg['params'])
            if msg.get('id')==self.id:
                if 'error' in msg:raise RuntimeError(msg['error'])
                return msg.get('result',{})
    def evaluate(self,expression):
        response=self.call('Runtime.evaluate',{'expression':expression,'returnByValue':True,'awaitPromise':True})
        if 'exceptionDetails' in response:raise RuntimeError(response['exceptionDetails'])
        return response.get('result',{}).get('value')
    def screenshot(self,name):
        result=self.call('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})
        (OUT/name).write_bytes(base64.b64decode(result['data']))

probe=socket.socket();probe.bind(('127.0.0.1',0));port=probe.getsockname()[1];probe.close()
profile=tempfile.mkdtemp(prefix='umbral-demo7-edge-')
process=subprocess.Popen([r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe','--headless=new','--disable-gpu','--no-first-run','--disable-background-networking',f'--remote-debugging-port={port}','--user-data-dir='+profile,'about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
try:
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    for _ in range(80):
        try:
            pages=json.loads(opener.open(f'http://127.0.0.1:{port}/json',timeout=1).read())
            target=next(p for p in pages if p['type']=='page');break
        except (OSError,StopIteration):time.sleep(.25)
    else:raise RuntimeError('Edge did not expose its local debugging endpoint')
    c=CDP(target['webSocketDebuggerUrl'])
    c.call('Runtime.enable');c.call('Page.enable')
    c.call('Browser.setDownloadBehavior',{'behavior':'allow','downloadPath':str(OUT)})
    for name in ['Umbral_demo7_ficha_23.html','Umbral_demo7_distribucion.csv']:
        target_file=OUT/name
        if target_file.exists():target_file.unlink()
    c.call('Emulation.setDeviceMetricsOverride',{'width':1440,'height':1000,'deviceScaleFactor':1,'mobile':False})
    c.call('Page.navigate',{'url':(ROOT/'02_Prediccion_y_escenarios_de_riesgo/demo/demo7.html').as_uri()})
    for _ in range(100):
        if c.evaluate('Boolean(window.Umbral7)'):break
        time.sleep(.2)
    else:raise RuntimeError('Demo7 failed to start: '+str(c.evaluate('document.getElementById("status")?.textContent'))+' '+str(c.errors))
    checks={}
    checks['startup']=c.evaluate('({context:document.getElementById("d7-context-label").textContent,avatars:[...document.querySelectorAll(".collaborator-orb img")].every(i=>i.complete&&i.naturalWidth>0),duplicateIds:[...document.querySelectorAll("[id]")].map(e=>e.id).filter((id,i,a)=>a.indexOf(id)!==i)})')
    c.screenshot('desktop_hero.png')
    c.evaluate('document.getElementById("state").value="23";document.getElementById("state").dispatchEvent(new Event("input"))');time.sleep(.5)
    checks['automatic_impact']=c.evaluate('({action:document.getElementById("action").value,values:[...document.querySelectorAll("#d6-plan-comparison-values strong")].map(e=>e.textContent),metrics:document.querySelectorAll("#d7-plan-impact-metrics article").length,note:document.getElementById("d6-plan-comparison-note").textContent,beforePlan:document.getElementById("d6-plan-comparison").getBoundingClientRect().top<document.getElementById("d6-state-plan-content").getBoundingClientRect().top})')
    checks['initial_difference_view']=c.evaluate('({view:document.getElementById("d7-map-view").value,pairedHidden:document.getElementById("d7-paired-maps").hidden,differenceVisible:!document.getElementById("d7-difference-wrap").hidden})')
    c.evaluate('document.getElementById("d6-state-plan").scrollIntoView({behavior:"instant"})');time.sleep(.4);c.screenshot('automatic_impact.png')
    checks['recommendation_evidence']=c.evaluate('({cards:document.querySelectorAll(".d7-action-rationale").length,diagnosis:document.getElementById("d7-diagnosis").textContent,activities:document.getElementById("d7-plan-action").options.length})')
    c.evaluate('document.getElementById("d7-action-reach").value="1000";document.getElementById("d7-action-reach").dispatchEvent(new Event("input"));document.getElementById("d7-action-distribution").value="prioridad";document.getElementById("d7-action-distribution").dispatchEvent(new Event("input"))');time.sleep(.4)
    checks['per_action']=c.evaluate('(()=>{const s=window.Umbral7Planning.snapshot;return {served:s.served,additional:s.additional,assigned:s.rows.reduce((n,r)=>n+r.served,0),pending:s.rows.filter(r=>r.status==="Pendiente").length,missing:s.rows.filter(r=>r.status==="Sin estimación").length}})()')
    c.evaluate('document.getElementById("d7-plan-action").value="1";document.getElementById("d7-plan-action").dispatchEvent(new Event("change"))');time.sleep(.2)
    checks['unquantified_action']=c.evaluate('({effect:document.getElementById("d7-action-effect").value,additional:window.Umbral7Planning.snapshot.additional})')
    c.evaluate('document.getElementById("d7-plan-action").value="0";document.getElementById("d7-plan-action").dispatchEvent(new Event("change"))');time.sleep(.2)
    checks['saved_action']=c.evaluate('({reach:document.getElementById("d7-action-reach").value,additional:window.Umbral7Planning.snapshot.additional})')
    c.evaluate('document.getElementById("d7-action-high").value="0.5";document.getElementById("d7-action-high").dispatchEvent(new Event("input"))');time.sleep(.2)
    checks['invalid_effect']=c.evaluate('({error:document.getElementById("d7-editor-error").textContent,exportDisabled:document.getElementById("d7-download-brief").disabled,scenario:window.Umbral7Planning.snapshot})')
    c.evaluate('document.getElementById("d7-action-high").value="3";document.getElementById("d7-action-high").dispatchEvent(new Event("input"));document.getElementById("d7-action-distribution").value="proporcional";document.getElementById("d7-action-distribution").dispatchEvent(new Event("input"))');time.sleep(.3)
    c.evaluate('document.getElementById("d7-action-editor").scrollIntoView({behavior:"instant"})');time.sleep(.3);c.screenshot('action_editor.png')
    c.evaluate('document.getElementById("d7-download-brief").click();document.getElementById("d7-allocation-download").click()');time.sleep(.7)
    brief_html=c.evaluate('window.Umbral7Planning.lastBrief')
    checks['exports']={'html':(OUT/'Umbral_demo7_ficha_23.html').exists(),'csv':(OUT/'Umbral_demo7_distribucion.csv').exists(),'self_contained':'<html' in brief_html and '<script src' not in brief_html,'sources':'CCPC' in brief_html and 'Fuentes y límites' in brief_html}
    c.evaluate('document.getElementById("d7-allocation-filter").value="sin_datos";document.getElementById("d7-allocation-filter").dispatchEvent(new Event("change"))')
    checks['allocation_filter']=c.evaluate('({rows:document.querySelectorAll("#d7-allocation-rows tr").length,text:document.getElementById("d7-allocation-rows").textContent})')
    c.evaluate('document.getElementById("d7-allocation-filter").value="todos";document.getElementById("d7-allocation-filter").dispatchEvent(new Event("change"))')
    c.evaluate('window.Umbral7.example()');time.sleep(1)
    checks['example']=c.evaluate('({state:window.Umbral7.state,action:document.getElementById("action").value,scope:document.getElementById("simulation-scope").value})')
    c.evaluate('document.getElementById("d7-prepare-plan").click()');time.sleep(1)
    checks['state_plan']=c.evaluate('({state:window.Umbral7.state,action:document.getElementById("action").value,reach:document.getElementById("reach").value,actions:document.querySelectorAll(".d7-action-list li").length,note:document.getElementById("d6-plan-comparison-note").textContent})')
    c.evaluate('document.getElementById("d6-state-plan").scrollIntoView({behavior:"instant"})');time.sleep(.5);c.screenshot('desktop_plan.png')
    c.evaluate('document.querySelector("[data-d7-map-view=paired]").click();document.getElementById("d7-map-before").scrollIntoView({behavior:"instant"});window.Umbral7.refreshMaps()');time.sleep(1)
    checks['maps']=c.evaluate('({canvases:document.querySelectorAll(".d7-map canvas").length,description:document.getElementById("d7-maps-context").textContent,overflow:document.documentElement.scrollWidth>innerWidth})')
    c.evaluate('document.querySelector("#d7-map-before .leaflet-control-zoom-in").click()');time.sleep(.6)
    checks['synchronized_zoom']=c.evaluate('window.Umbral7.comparisonMaps')
    c.evaluate('document.getElementById("d7-fit-maps").click()');time.sleep(.4)
    c.screenshot('desktop_maps.png')
    c.evaluate('document.getElementById("d7-map-view").value="difference";document.getElementById("d7-map-view").dispatchEvent(new Event("change"));document.getElementById("d7-map-difference").scrollIntoView({behavior:"instant"});window.Umbral7.refreshMaps()');time.sleep(.7)
    checks['difference_map']=c.evaluate('({visible:!document.getElementById("d7-difference-wrap").hidden,legend:document.getElementById("d7-map-legend").textContent,views:window.Umbral7.comparisonMaps})')
    c.screenshot('difference_map.png')
    difference_reach=c.evaluate('document.getElementById("reach").value')
    c.evaluate('document.getElementById("reach").scrollIntoView({behavior:"instant"});document.getElementById("reach").value="1000";document.getElementById("reach").dispatchEvent(new Event("input"))');time.sleep(.4)
    c.evaluate('document.getElementById("d7-map-difference").scrollIntoView({behavior:"instant"})');time.sleep(.7)
    checks['difference_reentry']=c.evaluate('({context:document.getElementById("d7-maps-context").textContent,summary:document.getElementById("d7-change-summary").textContent})')
    c.evaluate('document.getElementById("reach").value='+json.dumps(difference_reach)+';document.getElementById("reach").dispatchEvent(new Event("input"))');time.sleep(.3)
    c.evaluate('document.getElementById("d7-map-view").value="paired";document.getElementById("d7-map-view").dispatchEvent(new Event("change"))');time.sleep(.3)
    previous_reach=c.evaluate('document.getElementById("reach").value')
    c.evaluate('document.getElementById("reach").value="0";document.getElementById("reach").dispatchEvent(new Event("input"));document.getElementById("method").value="ridge";document.getElementById("method").dispatchEvent(new Event("input"))');time.sleep(.5)
    checks['zero_coverage_and_method']=c.evaluate('({context:document.getElementById("d7-context-label").textContent,values:[...document.querySelectorAll("#d6-plan-comparison-values strong")].map(e=>e.textContent),additional:document.getElementById("additional").textContent})')
    c.evaluate('document.getElementById("reach").value='+json.dumps(previous_reach)+';document.getElementById("method").value="hgb";document.getElementById("method").dispatchEvent(new Event("input"))');time.sleep(.5)
    c.call('Emulation.setDeviceMetricsOverride',{'width':390,'height':844,'deviceScaleFactor':1,'mobile':False})
    c.evaluate('window.scrollTo({top:0,behavior:"instant"})');time.sleep(.6);c.screenshot('mobile_hero.png')
    checks['mobile']=c.evaluate('({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,navigation:getComputedStyle(document.querySelector(".quick-nav")).display})')
    c.evaluate('document.getElementById("d7-map-before").scrollIntoView({behavior:"instant"});window.Umbral7.refreshMaps()');time.sleep(.8);c.screenshot('mobile_maps.png')
    c.evaluate('document.getElementById("map-year").value="2024";document.getElementById("map-year").dispatchEvent(new Event("change"))');time.sleep(.5)
    checks['historical']=c.evaluate('({year:window.Umbral7.state.year,backVisible:!document.getElementById("d7-back-forecast").hidden,actionsHidden:document.getElementById("modulo-3").hidden})')
    c.evaluate('document.getElementById("d7-back-forecast").click();document.getElementById("d7-pause-motion").click()');time.sleep(.5)
    checks['return_and_pause']=c.evaluate('({year:window.Umbral7.state.year,paused:document.getElementById("d7-pause-motion").getAttribute("aria-pressed")})')
    c.call('Emulation.setEmulatedMedia',{'features':[{'name':'prefers-reduced-motion','value':'reduce'}]})
    checks['reduced_motion']=c.evaluate('({seal:getComputedStyle(document.querySelector(".art-seal")).animationName,headingVisible:getComputedStyle(document.querySelector(".module-heading")).opacity})')
    c.evaluate('document.getElementById("d7-start-tour").click()');time.sleep(.3)
    tour_titles=[]
    for step in range(5):
        tour_titles.append(c.evaluate('document.getElementById("d7-tour-title").textContent'))
        c.evaluate('document.getElementById("d7-tour-next").click()');time.sleep(.15)
    checks['tour']={'titles':tour_titles,'closed':c.evaluate('!document.getElementById("d7-tour").open')}
    c.evaluate('document.getElementById("action").value="ninguna";document.getElementById("state").value="08";document.getElementById("search").value="";document.getElementById("state").dispatchEvent(new Event("input"));document.querySelector("[data-d7-map-view=difference]").click();document.getElementById("d7-comparison-block").scrollIntoView({behavior:"instant"})');time.sleep(.8)
    checks['chihuahua_change']=c.evaluate('({context:document.getElementById("d7-maps-context").textContent,summary:document.getElementById("d7-change-summary").textContent,explanation:document.getElementById("d7-change-explanation").textContent,legend:document.getElementById("d7-map-legend").textContent,overflow:document.documentElement.scrollWidth>innerWidth,view:document.getElementById("d7-map-view").value,collapsedReasons:[...document.querySelectorAll(".d7-action-rationale")].every(e=>e.tagName==="DETAILS"&&!e.open),assumptionsCollapsed:!document.getElementById("d6-plan-comparison-note").closest("details").open})')
    c.screenshot('chihuahua_change_mobile.png')
    c.call('Emulation.setDeviceMetricsOverride',{'width':1440,'height':1000,'deviceScaleFactor':1,'mobile':False})
    c.evaluate('document.getElementById("d7-comparison-block").scrollIntoView({behavior:"instant"});window.Umbral7.refreshMaps()');time.sleep(.6);c.screenshot('chihuahua_change_desktop.png')
    c.call('Page.navigate',{'url':'data:text/html;base64,'+base64.b64encode(brief_html.encode()).decode()});time.sleep(.6)
    pdf=base64.b64decode(c.call('Page.printToPDF',{'printBackground':True,'preferCSSPageSize':True})['data'])
    (OUT/'ficha_validada.pdf').write_bytes(pdf)
    checks['brief_pdf_pages']=len(re.findall(rb'/Type\s*/Page\b',pdf))
    checks['errors']=c.errors
    (OUT/'review.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(checks,ensure_ascii=True,indent=2))
    assert checks['startup']['avatars'] and not checks['startup']['duplicateIds']
    assert checks['initial_difference_view']['view']=='difference' and checks['initial_difference_view']['pairedHidden'] and checks['initial_difference_view']['differenceVisible']
    assert checks['automatic_impact']['action']=='ninguna' and checks['automatic_impact']['metrics']==3
    assert len(checks['automatic_impact']['values'])==2 and '—' not in checks['automatic_impact']['values']
    assert not checks['automatic_impact']['beforePlan'] and 'automático' in checks['automatic_impact']['note']
    assert checks['example']['scope']=='municipio'
    assert checks['state_plan']['actions']>0 and checks['state_plan']['action']=='info_institucional'
    assert checks['maps']['canvases']==3 and checks['maps']['description']
    assert checks['synchronized_zoom'][0]==checks['synchronized_zoom'][1]==checks['synchronized_zoom'][2]
    assert checks['recommendation_evidence']['cards']==checks['recommendation_evidence']['activities']>0
    assert checks['per_action']['served']==checks['per_action']['assigned']==1000 and abs(checks['per_action']['additional']-15)<1e-8
    assert checks['per_action']['pending']>0 and checks['per_action']['missing']>0
    assert float(checks['unquantified_action']['effect'])==0 and checks['unquantified_action']['additional']==0
    assert checks['saved_action']['reach']=='1000' and abs(checks['saved_action']['additional']-15)<1e-8
    assert checks['invalid_effect']['error'] and checks['invalid_effect']['exportDisabled'] and checks['invalid_effect']['scenario'] is None
    assert all(checks['exports'].values())
    assert 'Sin estimación' in checks['allocation_filter']['text']
    assert checks['difference_map']['visible'] and 'Escala relativa' in checks['difference_map']['legend']
    assert '≈ 15' in checks['difference_reentry']['summary'] and '0.00108' in checks['difference_reentry']['summary']
    assert checks['tour']['closed'] and len(set(checks['tour']['titles']))==5
    assert 'Municipios con reducción' in checks['chihuahua_change']['summary'] and not checks['chihuahua_change']['overflow']
    assert 'CHIHUAHUA' in checks['chihuahua_change']['context']
    assert checks['chihuahua_change']['collapsedReasons'] and checks['chihuahua_change']['assumptionsCollapsed']
    assert checks['brief_pdf_pages']==1
    assert 'Ridge' in checks['zero_coverage_and_method']['context']
    assert len(set(checks['zero_coverage_and_method']['values']))==1 and checks['zero_coverage_and_method']['additional'].replace('\u2248','').strip()=='0'
    assert checks['mobile']['scrollWidth']<=checks['mobile']['width']
    assert checks['historical']['year']==2024 and checks['historical']['backVisible']
    assert checks['return_and_pause']['year']==2027 and checks['return_and_pause']['paused']=='true'
    assert checks['reduced_motion']['seal']=='none' and checks['reduced_motion']['headingVisible']=='1'
    assert not checks['errors']
finally:
    process.terminate()
    try:process.wait(timeout=5)
    except subprocess.TimeoutExpired:process.kill()
    profile_path=Path(profile).resolve()
    if profile_path.parent==Path(tempfile.gettempdir()).resolve() and profile_path.name.startswith('umbral-demo7-edge-'):
        shutil.rmtree(profile_path,ignore_errors=True)
