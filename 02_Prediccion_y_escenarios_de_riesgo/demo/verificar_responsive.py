"""Comprueba margenes de Umbral en ocho ventanas, con paneles desplegados."""
from datetime import date
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import base64
import csv
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

DEMO=Path(__file__).resolve().parent
ROOT=DEMO.parents[1]
OUT=DEMO/'verificacion/demo7'
OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(DEMO.parent/'tools'))
from browser_cdp import CDP

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key in ('src','href') and value:
                self.links.append(value)

links=Links()
links.feed((DEMO/'demo7.html').read_text(encoding='utf-8'))
local=[unquote(urlsplit(link).path) for link in links.links if not urlsplit(link).scheme and urlsplit(link).path]
assert all((DEMO/path).exists() for path in local),[p for p in local if not (DEMO/p).exists()]
assert '../modelado/salidas/comparacion_modelos/proyeccion_2027.csv' in local
assert '../datos_preparados/municipios_historico_con_calidad.csv' in local

edge=next((p for p in [Path(os.environ.get('PROGRAMFILES(X86)','C:/Program Files (x86)'))/'Microsoft/Edge/Application/msedge.exe',Path(os.environ.get('PROGRAMFILES','C:/Program Files'))/'Microsoft/Edge/Application/msedge.exe'] if p.exists()),None)
if edge is None:
    raise RuntimeError('Edge no está instalado; no se puede acreditar la verificación de navegador.')
with socket.socket() as probe:
    probe.bind(('127.0.0.1',0))
    port=probe.getsockname()[1]
profile=Path(tempfile.mkdtemp(prefix='umbral-requisitos-edge-')).resolve()
process=subprocess.Popen([str(edge),'--headless=new','--disable-gpu','--no-first-run','--disable-background-networking',f'--remote-debugging-port={port}','--user-data-dir='+str(profile),'about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
checks={'local_links':len(local)}
c=None
try:
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    deadline=time.monotonic()+20
    while True:
        try:
            targets=json.loads(opener.open(f'http://127.0.0.1:{port}/json',timeout=1).read())
            target=next(p for p in targets if p['type']=='page')
            break
        except (OSError,StopIteration):
            if time.monotonic()>deadline:raise RuntimeError('Edge no inició el puerto local.')
            time.sleep(.2)
    c=CDP(target['webSocketDebuggerUrl'])
    c.call('Runtime.enable');c.call('Page.enable')
    c.call('Emulation.setEmulatedMedia',{'features':[{'name':'prefers-reduced-motion','value':'reduce'}]})
    c.call('Emulation.setDeviceMetricsOverride',{'width':1440,'height':1000,'deviceScaleFactor':1,'mobile':False})
    def wait_for(expression):
        deadline=time.monotonic()+15
        while not c.evaluate(expression):
            if time.monotonic()>deadline:raise AssertionError(expression)
            time.sleep(.15)
    def value(element,value,event='input'):
        c.evaluate(f'document.getElementById({json.dumps(element)}).value={json.dumps(value)};document.getElementById({json.dumps(element)}).dispatchEvent(new Event({json.dumps(event)},{{bubbles:true}}))')
    def screenshot(name,selector=None):
        params={'format':'png','captureBeyondViewport':bool(selector)}
        if selector:
            c.evaluate(f'document.querySelector({json.dumps(selector)}).scrollIntoView({{behavior:"instant",block:"center"}})')
            time.sleep(.5)
            c.evaluate('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
            params['clip']=c.evaluate(f'(()=>{{const r=document.querySelector({json.dumps(selector)}).getBoundingClientRect();return {{x:r.x+scrollX,y:r.y+scrollY,width:r.width,height:r.height,scale:1}}}})()')
        (OUT/name).write_bytes(base64.b64decode(c.call('Page.captureScreenshot',params)['data']))
    c.call('Page.navigate',{'url':(DEMO/'demo7.html').as_uri()})
    wait_for('Boolean(window.Umbral7 && window.Umbral7Planning)')
    c.evaluate('document.fonts.ready.then(()=>{document.documentElement.style.setProperty("scroll-behavior","auto","important")})')
    OUT=DEMO/'verificacion/responsive'
    OUT.mkdir(exist_ok=True)
    value('state','23')
    wait_for('window.Umbral7Planning.snapshot?.served>0')
    c.evaluate("document.head.insertAdjacentHTML('beforeend','<style>*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}.d7-reveal{opacity:1!important;transform:none!important}</style>')")
    results=[]
    for width,height in [(1440,900),(1024,768),(768,1024),(700,800),(540,720),(390,844),(320,568),(844,390)]:
        c.call('Emulation.setDeviceMetricsOverride',{'width':width,'height':height,'deviceScaleFactor':1,'mobile':False})
        for scope in ['state','municipality']:
            if scope=='municipality':
                c.evaluate('window.Umbral7.example()')
                wait_for('window.Umbral7Planning.snapshot?.additional===3')
            else:
                value('search','');value('state','23');value('action','ninguna','change')
            c.evaluate('document.querySelectorAll("main details").forEach(e=>e.open=true);window.scrollTo(0,0);window.Umbral7.refreshMaps()')
            time.sleep(.3)
            issues=c.evaluate("""(()=>{const nodes=[...document.querySelectorAll('main *,header *, .d7-context-bar *')];return nodes.flatMap(e=>{const r=e.getBoundingClientRect();if(!e.checkVisibility()||!r.width||!r.height||e.closest('.leaflet-pane,.hero-art,table,svg'))return [];const outside=r.right>document.documentElement.clientWidth+1||r.left< -1;const clipped=e.clientWidth>0&&e.scrollWidth>e.clientWidth+2&&getComputedStyle(e).overflowX==='hidden'&&!e.matches('.leaflet-container,.hero');return outside||clipped?[{tag:e.tagName,id:e.id,cls:e.className,outside,clipped,left:Math.round(r.left),right:Math.round(r.right)}]:[]})})()""")
            results.append({'width':width,'height':height,'scope':scope,'issues':issues})
            if width in [320,390,768] and scope=='municipality':
                for name,selector in [('info','#detail'),('actions','#paso-3')]:
                    c.evaluate(f'document.querySelector({json.dumps(selector)}).scrollIntoView({{block:"start"}})')
                    time.sleep(.15)
                    screenshot(f'{width}-{name}.png')
    result={'date':date.today().isoformat(),'details_expanded':True,'sources':{p:hashlib.sha256((DEMO/p).read_bytes()).hexdigest() for p in ['demo7.html','assets/demo7.css','assets/demo7.js']},'application':'Umbral','checks':results,'page_errors':c.errors,'passed':not c.errors and all(not r['issues'] for r in results)}
    (OUT/'audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
    assert result['passed'],'Responsive layout issues; see verificacion/responsive/audit.json'

finally:
    if c:
        try:c.call('Browser.close')
        except (OSError,RuntimeError):pass
        c.sock.close()
    try:process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.terminate()
        process.wait(timeout=5)
    if profile.parent==Path(tempfile.gettempdir()).resolve() and profile.name.startswith('umbral-requisitos-edge-'):
        shutil.rmtree(profile,ignore_errors=True)
