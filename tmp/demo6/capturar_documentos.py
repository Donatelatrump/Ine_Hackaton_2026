from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'.task_packages'))
from playwright.sync_api import sync_playwright
DEMO=ROOT/'02_Prediccion_y_escenarios_de_riesgo/demo'
OUT=DEMO/'verificacion/demo6'
OUT.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1050})
    page.goto((DEMO/'demo6.html').as_uri())
    page.wait_for_function('window.Umbral6')
    page.locator('#map').screenshot(path=str(OUT/'mapa_base.png'))
    page.evaluate("document.getElementById('action').value='sms_suecia';document.getElementById('reach').value='100000';document.getElementById('distribution').value='proporcional';update()")
    for mode,name in [('intervencion','mapa_intervencion.png'),('cambio','mapa_cambio.png')]:
        page.evaluate("mode=>{document.getElementById('map-mode').value=mode;update()}",mode)
        page.locator('#map').screenshot(path=str(OUT/name))
    config=page.evaluate("({selection:Umbral6.state,coverage:Number(document.getElementById('reach').value),distribution:document.getElementById('distribution').value,action:document.getElementById('action').value,additional:plan.additional})")
    assert abs(config['additional']-300)<1e-6
    (OUT/'configuracion.json').write_text(json.dumps(config,indent=2),encoding='utf-8')
    browser.close()
print('Capturas de demo6 generadas para reporte.')
