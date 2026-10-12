"""Regenera capturas y CSV de una configuración explícita de la demo vigente."""
import json
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'.task_packages'))
from playwright.sync_api import sync_playwright
OUT=HERE/'verificacion'
OUT.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1000},accept_downloads=True)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto((HERE/'index.html').as_uri())
    page.wait_for_function("document.getElementById('eligible').textContent==='1,144'",timeout=60000)
    page.screenshot(path=str(OUT/'inicio_escritorio.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':844})
    page.screenshot(path=str(OUT/'inicio_movil.png'),full_page=True)
    page.set_viewport_size({'width':1440,'height':1000})
    page.locator('#action').select_option('sms_suecia')
    page.locator('#planning-settings > summary').click()
    page.locator('#distribution').select_option('proporcional')
    page.locator('#reach').fill('100000')
    for mode,name in [('base','mapa_base.png'),('intervencion','mapa_intervencion.png'),('cambio','mapa_cambio.png')]:
        page.locator('#map-mode').select_option(mode)
        page.locator('.map-panel').screenshot(path=str(OUT/name))
    page.locator('#map-mode').select_option('base')
    page.locator('#planning-settings > summary').click()
    page.evaluate("detail(plan.selected[0].key)")
    page.screenshot(path=str(OUT/'escritorio.png'),full_page=True)
    downloads=[]
    page.on('download',lambda d:downloads.append(d))
    page.locator('#export').click()
    page.wait_for_timeout(900)
    for download in downloads:
        name='leeme.csv' if 'leeme' in download.suggested_filename else 'plan.csv'
        download.save_as(str(OUT/name))
        artifact=OUT/name
        artifact.write_bytes(artifact.read_bytes().replace(b'\r\n',b'\n'))
    assert len(downloads)==2 and not errors
    configuration=page.evaluate("({scope:document.getElementById('simulation-scope').value,stable:document.getElementById('stable').checked,distribution:plan.distribution,action:plan.action.id,coverage_total:Number(document.getElementById('reach').value),served:plan.served,additional:plan.additional,municipalities:plan.selected.length,territory:Decision.territorialScenario(filtered,plan)})")
    (OUT/'configuracion_capturas.json').write_text(json.dumps(configuration,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    page.set_viewport_size({'width':390,'height':844})
    page.screenshot(path=str(OUT/'movil.png'),full_page=True)
    browser.close()
print('Capturas actuales: México incluido, catálogo constante, SMS Suecia, proporcional, cobertura total 100,000.')
