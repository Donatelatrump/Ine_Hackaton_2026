"""Comprueba selección, históricos, agregaciones, CSV y escenarios de demo6."""
from pathlib import Path
import csv
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'.task_packages'))
from playwright.sync_api import sync_playwright

HERE=Path(__file__).resolve().parent
OUT=ROOT/'tmp/demo6/modular'
OUT.mkdir(parents=True,exist_ok=True)

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1050},accept_downloads=True)
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto((HERE/'demo6.html').as_uri())
    page.wait_for_function('window.Umbral6 && document.getElementById("d6-summary").textContent.includes("1,783")',timeout=30000)
    assert page.locator('#method').input_value()=='hgb'
    assert page.evaluate("typeof records==='undefined' && window.map instanceof HTMLElement && typeof geographyFocusKey==='undefined' && !window.UmbralDemo6Views && !window.UmbralAnalytics")
    assert page.evaluate("typeof window.__backToNacional==='undefined'")
    page.locator('#modulo-1').screenshot(path=str(OUT/'demo6_nacional.png'))
    page.evaluate("Umbral6.selectMunicipality('01001')")
    assert 'AGUASCALIENTES' in page.locator('#d6-state-profile h3').inner_text().upper()
    assert 'todo AGUASCALIENTES' in page.locator('.d6-profile-scope').inner_text()
    assert page.locator('.d6-optional-simulation').get_attribute('open') is None
    assert page.evaluate("Umbral6.state.municipality==='01001' && Umbral6.inspect().focusKey==='01001'")
    assert page.locator('#d6-summary').inner_text().startswith('Abstención\n52.42%')
    expected=page.evaluate("Umbral6.inspect('01').stateRate")
    actual=page.evaluate("parseFloat(document.getElementById('d6-context').textContent.match(/([0-9.]+)%/)[1])")
    assert abs(expected-actual)<.006
    before=page.evaluate('Object.values(Umbral6.inspect().map)')
    page.locator('#map-year').select_option('2009')
    assert page.evaluate("Umbral6.state.municipality==='01001' && Umbral6.inspect().focusKey==='01001'")
    assert not page.locator('#map-year').is_disabled()
    after=page.evaluate('Object.values(Umbral6.inspect().map)')
    assert before==after,(before,after)
    text=page.locator('#detail-content').inner_text()
    assert 'Abstención observada · 2009' in text
    assert 'Qué se estima' not in text and 'Acción sugerida' not in text
    assert page.locator('#modulo-3').is_hidden()
    assert page.locator('#method').is_disabled()
    page.locator('#modulo-2').screenshot(path=str(OUT/'demo6_historico.png'))
    with page.expect_download() as download:
        page.locator('#d6-export').click()
    download.value.save_as(str(OUT/'consulta_2009.csv'))
    exported=list(csv.DictReader((OUT/'consulta_2009.csv').open(encoding='utf-8-sig',newline='')))
    assert len(exported)==1 and exported[0]['Año']=='2009' and exported[0]['Tipo de dato']=='Observado'
    page.locator('#map').click(button='right')
    assert page.evaluate("!Umbral6.inspect().focusKey && Umbral6.state.state==='01' && !Umbral6.state.municipality")
    page.locator('#map').click(button='right')
    assert page.evaluate("Umbral6.state.state==='' && !Umbral6.inspect().focusKey")
    page.locator('#map-year').select_option('2027')
    page.evaluate("Umbral6.selectMunicipality('01001')")
    page.locator('#method').select_option('ridge')
    page.locator('#method').dispatch_event('input')
    assert page.locator('#d6-summary').inner_text().startswith('Abstención\n49.04%')
    assert '49.04%' in page.locator('#detail-content').inner_text()
    for method in ['hgb','lightgbm','catboost','ridge','baseline']:
        page.locator('#method').select_option(method)
        page.locator('#method').dispatch_event('input')
        assert page.evaluate("Math.abs(Umbral6.inspect().municipalityRate-Number(document.querySelector('#d6-summary strong').textContent.replace('%','')))<.006")
    assert page.locator('#d6-metrics tr').count()==10
    page.locator('#method').select_option('hgb')
    page.locator('#method').dispatch_event('input')
    page.locator('.d6-optional-simulation > summary').click()
    page.locator('[data-d6-preset="sms"]').click()
    assert page.locator('#simulation-results').is_visible()
    assert page.evaluate('Math.abs(Umbral6.inspect().additional-3)<1e-7')
    assert page.locator('#d6-scenario-comparison').is_visible()
    page.locator('#modulo-3').screenshot(path=str(OUT/'demo6_simulacion.png'))
    page.locator('[data-d6-preset="reset"]').click()
    assert page.locator('#simulation-results').is_hidden()
    page.evaluate("Umbral6.returnToMexico()")
    with page.expect_download() as download:
        page.locator('#d6-export').click()
    download.value.save_as(str(OUT/'consulta_nacional.csv'))
    national=list(csv.DictReader((OUT/'consulta_nacional.csv').open(encoding='utf-8-sig',newline='')))
    assert len(national)==2477,len(national)
    assert sum(row['Abstención (%)']!='' for row in national)==1783
    # Los promedios de mapa y resumen usan la misma definición de tasa/denominador.
    assert page.evaluate("(()=>{const d=Umbral6.inspect('01');return d.stateFill===({bajo:'#8bbbad',medio:'#e8b451',alto:'#bd5472',sin_datos:'#8997ab'})[Decision.level(d.stateRate,d.thresholds)];})()")
    page.locator('#d6-evidence-title').scroll_into_view_if_needed()
    page.locator('.d6-evidence').screenshot(path=str(OUT/'demo6_metricas.png'))
    page.set_viewport_size({'width':390,'height':844})
    page.evaluate("Umbral6.selectMunicipality('01001')")
    page.locator('#modulo-1').screenshot(path=str(OUT/'demo6_movil.png'))
    assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1')
    assert not errors,errors
    browser.close()
    report={'seleccion_unificada':True,'historico_conserva_encuadre':True,'clic_derecho_por_nivel':True,
            'agregacion_ponderada':True,'metodos':True,'csv_nacional_filas':len(national),
            'csv_historico':True,'escenario_sms_1000':3,'mobile':True,
            'estado_interno_privado':True,'ficha_estatal_conservada':True,'errores_js':errors}
    (OUT/'verificacion_demo6.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
