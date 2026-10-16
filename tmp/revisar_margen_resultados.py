from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.task_packages'))
from playwright.sync_api import sync_playwright
out=R/'tmp/demo6/margenes';out.mkdir(exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True)
 page=b.new_page()
 for width in [1440,1100,918,390]:
  page.set_viewport_size({'width':width,'height':900})
  page.goto((R/'02_Prediccion_y_escenarios_de_riesgo/demo/demo6.html').as_uri())
  page.wait_for_function('window.Umbral6')
  page.evaluate("Umbral6.selectMunicipality('19013')")
  page.locator('#paso-2').scroll_into_view_if_needed()
  print(width,page.evaluate("(()=>{const p=document.querySelector('#paso-2'),s=p.querySelector('.stats'),d=document.querySelector('#detail');return {panel:p.getBoundingClientRect().width,stats:s.getBoundingClientRect().width,detail:d.getBoundingClientRect().width,scroll:p.scrollWidth,client:p.clientWidth};})()"))
  page.screenshot(path=str(out/f'resultados_{width}.png'))
 b.close()
