"""Aceptación de Demo7 en Edge local, sin dependencias Python externas.

Guarda evidencia del navegador y CSV; no reentrena ni consulta servicios externos.
"""
from datetime import date
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import zipfile
import xml.etree.ElementTree as ET
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
    checks['initial_method']=c.evaluate('document.getElementById("method").value')
    assert checks['initial_method']=='hgb'
    assert c.evaluate('document.querySelectorAll("[id]").length===new Set([...document.querySelectorAll("[id]")].map(e=>e.id)).size')
    screenshot('mapa_base.png','#map')
    value('state','23')
    wait_for('window.Umbral7Planning.snapshot?.served>0')
    initial=c.evaluate('window.Umbral7Planning.snapshot')
    checks['state_plan']={'served':initial['served'],'additional':initial['additional'],'rows':len(initial['rows'])}
    assert abs(initial['additional']-initial['served']*.015)<1e-6
    assert c.evaluate('!document.getElementById("d7-action-editor") && !document.getElementById("d7-plan-coverage")')
    state_comparison=c.evaluate('document.getElementById("d6-plan-comparison-values").textContent')
    assert 'supuesto' in c.evaluate('document.getElementById("d7-impact-caption").textContent')
    assert any(r['before'] is None for r in initial['rows'])
    # Capture both maps and differences for exactly the same state plan.
    c.evaluate('document.getElementById("d7-map-before").scrollIntoView({behavior:"instant"});window.Umbral7.refreshMaps()')
    wait_for('document.querySelectorAll(".d7-map canvas").length===3')
    screenshot('escenario_sin.png','#d7-map-before')
    screenshot('mapa_intervencion.png','#d7-map-after')
    c.evaluate('document.querySelector("[data-d7-map-view=difference]").click()')
    wait_for('!document.getElementById("d7-difference-wrap").hidden')
    screenshot('mapa_cambio.png','#d7-map-difference')
    checks['map_comparison']=c.evaluate('document.getElementById("d7-maps-context").textContent')
    # Download the full distribution despite a visible filter and pagination.
    with tempfile.TemporaryDirectory(prefix='umbral-demo7-download-') as download_dir:
        c.call('Browser.setDownloadBehavior',{'behavior':'allow','downloadPath':download_dir})
        value('d7-allocation-filter','sin_datos','change')
        c.evaluate('document.getElementById("d7-allocation-download").click()')
        path=Path(download_dir)/'Umbral_distribucion.csv'
        deadline=time.monotonic()+10
        while not path.exists():
            assert time.monotonic()<deadline,'CSV no descargado'
            time.sleep(.1)
        rows=list(csv.DictReader(path.open(encoding='utf-8-sig',newline='')))
        assert len(rows)==len(initial['rows'])
        assert sum(float(r['Personas asignadas']) for r in rows)==initial['served']
        assert len(rows[0])==19
        rates=sorted(r['hgb'] for r in json.loads((DEMO/'data/comparacion_modelos.json').read_text(encoding='utf-8'))['forecasts'] if r.get('hgb') is not None)
        def quantile(q):
            pos=(len(rates)-1)*q;i=int(pos)
            return rates[i]+(rates[min(i+1,len(rates)-1)]-rates[i])*(pos-i)
        for r in rows:
            assert r['Método']=='HistGradientBoosting' and r['Fuente de la acción'] and r['Límites']
            if r['Abstención base (%)']:
                before=float(r['Abstención base (%)']);after=float(r['Abstención con acción (%)'])
                assert abs(before-after-float(r['Reducción (pp)']))<1e-9
                low=quantile(1/3);high=quantile(2/3)
                classify=lambda x:'alto' if x>=high else 'bajo' if x<low else 'medio'
                assert r['Semáforo sin acción']==classify(before)
                assert r['Semáforo con acción']==classify(after)
            else:
                assert r['Semáforo sin acción']==r['Semáforo con acción']=='sin_datos'
                assert r['Abstención con acción (%)']=='' and float(r['Personas asignadas'])==0
        shutil.copyfile(path,OUT/'distribucion_ejemplo.csv')
        checks['csv']={'rows':len(rows),'columns':len(rows[0]),'full_despite_filter':True,'scenario_and_sources':True}
    # Zero coverage must preserve both rates; switching methods must invalidate exports.
    value('action','sms_suecia','change');value('reach','0')
    wait_for('window.Umbral7Planning.snapshot?.served===0')
    zero=c.evaluate('window.Umbral7Planning.snapshot')
    assert zero['additional']==0 and all(r['reduction'] in (0,None) for r in zero['rows'])
    value('method','ridge')
    wait_for('window.Umbral7Planning.snapshot?.method==="ridge"')
    assert c.evaluate('window.Umbral7Planning.snapshot.additional')==0
    checks['zero_coverage_and_method']=True
    value('method','hgb');value('action','ninguna','change')
    assert c.evaluate('document.getElementById("d6-plan-comparison-values").textContent')==state_comparison
    c.evaluate('document.getElementById("stable").checked=true;document.getElementById("stable").dispatchEvent(new Event("input"))')
    stable=c.evaluate('window.Umbral7Planning.snapshot')
    assert stable['served']==int(stable['population']*.1) and stable['served']<=initial['served'] and stable['served']>0
    checks['catalog_filter_updates_coverage']=True
    c.evaluate('document.getElementById("stable").checked=false;document.getElementById("stable").dispatchEvent(new Event("input"))')
    # Preserve the documented municipal example and exact arithmetic.
    c.evaluate('window.Umbral7.example()')
    wait_for('window.Umbral7Planning.snapshot?.additional===3')
    example=c.evaluate('window.Umbral7Planning.snapshot')
    assert example['served']==1000 and example['method']=='hgb'
    row=next(r for r in example['rows'] if r['key']=='23008')
    assert abs(row['before']-61.63622241492481)<1e-9
    checks['municipal_example']={'additional':example['additional'],'reduction_pp':row['reduction']}
    with tempfile.TemporaryDirectory(prefix='umbral-action-download-') as download_dir:
        c.call('Browser.setDownloadBehavior',{'behavior':'allow','downloadPath':download_dir})
        c.evaluate('document.getElementById("export").click()')
        path=Path(download_dir)/'Umbral_distribucion.xlsx'
        deadline=time.monotonic()+10
        while not path.exists():
            assert time.monotonic()<deadline,'Excel de acciones no descargado'
            time.sleep(.1)
        ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        with zipfile.ZipFile(path) as workbook:
            assert workbook.testzip() is None
            for name in workbook.namelist():ET.fromstring(workbook.read(name))
            sheet=ET.fromstring(workbook.read('xl/worksheets/sheet1.xml'))
            cells={c.attrib['r']:c for c in sheet.findall('.//s:c',ns)}
            assert cells['B5'].find('s:is/s:t',ns).text=='23008'
            assert float(cells['F5'].find('s:v',ns).text)==1000
            assert abs(float(cells['I5'].find('s:v',ns).text)-row['reduction'])<1e-9
            assert sheet.find('s:autoFilter',ns).attrib['ref']=='A4:L5'
            assert sheet.find('.//s:pane',ns).attrib['state']=='frozen'
            styles=ET.fromstring(workbook.read('xl/styles.xml'))
            assert styles.find('.//s:border/s:left[@style="thin"]',ns) is not None
            assert 'xl/worksheets/sheet2.xml' in workbook.namelist()
        shutil.copyfile(path,OUT/'Umbral_distribucion_ejemplo.xlsx')
        c.evaluate('document.getElementById("d6-excel").click()')
        query=Path(download_dir)/'Umbral_consulta_23008_2027.xlsx'
        deadline=time.monotonic()+10
        while not query.exists():
            assert time.monotonic()<deadline,'Excel de consulta no descargado'
            time.sleep(.1)
        with zipfile.ZipFile(query) as workbook:
            assert workbook.testzip() is None
            sheet=ET.fromstring(workbook.read('xl/worksheets/sheet1.xml'))
            cell=sheet.find('.//s:c[@r="G5"]/s:v',ns)
            assert abs(float(cell.text)-row['before'])<1e-9
        shutil.copyfile(query,OUT/'Umbral_consulta_ejemplo.xlsx')
        checks['excel_downloads']={'sheets':2,'borders':True,'frozen_headers':True,'numeric_cells':True,'current_scenario':True}
    # Only action coverage is editable; the documented state plan stays fixed.
    fixed=c.evaluate('document.getElementById("d6-plan-comparison-values").textContent')
    value('reach','-1')
    assert c.evaluate('window.Umbral7Planning.snapshot===null && document.getElementById("d7-allocation-download").disabled')
    assert c.evaluate('document.getElementById("d6-plan-comparison-values").textContent')==fixed
    checks['invalid_action_coverage_preserves_state_plan']=True
    value('reach','1000')
    c.call('Emulation.setDeviceMetricsOverride',{'width':390,'height':844,'deviceScaleFactor':1,'mobile':True})
    c.evaluate('document.getElementById("paso-3").scrollIntoView({behavior:"instant"})')
    time.sleep(.5)
    assert c.evaluate('document.documentElement.scrollWidth<=innerWidth')
    screenshot('movil.png')
    checks['mobile_width']=390
    value('map-year','2024','change')
    assert c.evaluate('document.getElementById("modulo-3").hidden')
    checks['historical_hides_future_scenario']=True
    assert not c.errors,c.errors
    sources=['demo7.html','assets/demo7.js','assets/demo7.css','data/comparacion_modelos.js']
    result={'date':date.today().isoformat(),'passed':True,'checks':checks,'page_errors':c.errors,'sources':{p:hashlib.sha256((DEMO/p).read_bytes()).hexdigest() for p in sources}}
    (OUT/'resultado.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=True,indent=2))
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
