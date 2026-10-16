from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.task_packages'))
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True)
 page=b.new_page();page.on('pageerror',lambda e:print('ERROR',str(e)))
 page.goto((R/'02_Prediccion_y_escenarios_de_riesgo/demo/demo6.html').as_uri());page.wait_for_function('window.Umbral6')
 page.evaluate("Umbral6.selectMunicipality('08001')")
 print('SELECCION',page.evaluate('({state:Umbral6.state.state,municipality:Umbral6.state.municipality,title:document.querySelector("#d6-state-profile h3").textContent})'))
 print(page.evaluate("({records:typeof records,map:typeof map,mapDOM:window.map instanceof HTMLElement,focus:typeof geographyFocusKey,views:typeof window.UmbralDemo6Views,analytics:typeof window.UmbralAnalytics,oldBack:typeof window.__backToNacional,scripts:[...document.scripts].map(s=>s.src)})"))
 b.close()
