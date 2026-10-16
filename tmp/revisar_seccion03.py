from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from urllib.parse import urlsplit,unquote
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.task_packages'))
from playwright.sync_api import sync_playwright
out=R/'tmp/demo6/seccion03';out.mkdir(exist_ok=True)
class QuietHandler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(R)))
Thread(target=server.serve_forever,daemon=True).start()
errors=[];missing=[];states=[]
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True)
  page=b.new_page(viewport={'width':1440,'height':1050})
  page.on('pageerror',lambda error:errors.append(str(error)))
  page.on('response',lambda response:missing.append(response.url) if '127.0.0.1' in response.url and response.status>=400 else None)
  page.goto(f'http://127.0.0.1:{server.server_port}/02_Prediccion_y_escenarios_de_riesgo/demo/demo6.html')
  page.wait_for_function('window.Umbral6')
  assert 'Acciones contra' in page.locator('#module-three-title').inner_text()
  assert page.locator('.d6-profile-empty').count()==1
  options=page.locator('#state option').evaluate_all('(items)=>items.filter(i=>i.value).map(i=>({key:i.value,name:i.textContent}))')
  for state in options:
   page.locator('#state').select_option(state['key'],force=True)
   page.locator('#state').dispatch_event('input')
   assert page.locator('#d6-state-profile h3').inner_text()==state['name']
   assert page.locator('#d6-state-profile tbody tr').count()==4
   assert page.locator('.d6-source-grid article').count()==7
   states.append(state['key'])
  page.evaluate("Umbral6.selectMunicipality('19013')")
  assert 'CHINA' in page.locator('.d6-profile-scope').inner_text()
  assert 'NUEVO LEON' in page.locator('#d6-state-profile h3').inner_text()
  for anchor in page.locator('.d6-source-grid a').evaluate_all('(nodes)=>nodes.map(a=>a.href)'):
   local=R/unquote(urlsplit(anchor).path).lstrip('/')
   assert local.is_file(),local
  dimensions=[]
  for width in [1440,918,390]:
   page.set_viewport_size({'width':width,'height':1050})
   page.locator('#modulo-3').evaluate('(el)=>el.scrollIntoView({block:"start"})')
   page.wait_for_timeout(300)
   bounds=page.evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth})')
   assert bounds['scroll']<=width+1,bounds
   dimensions.append(bounds)
   page.screenshot(path=str(out/f'seccion03_{width}.png'))
  assert page.locator('.d6-optional-simulation').get_attribute('open') is None
  page.locator('.d6-optional-simulation > summary').click()
  assert page.locator('#paso-3').is_visible()
  page.locator('.d6-optional-simulation > summary').click()
  assert not errors,errors
  assert not missing,missing
  result={'title':'Acciones contra la abstención en tu estado','states_loaded':len(states),'municipality_preserves_state':True,'documents_local':7,'viewports':dimensions,'simulation_disclosure':True,'javascript_errors':errors,'missing_resources':missing}
  (out/'revision.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
  print(json.dumps(result,ensure_ascii=True))
  b.close()
finally:server.shutdown();server.server_close()
