import sys, json, csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'.task_packages'))
from playwright.sync_api import sync_playwright
OUT=Path(__file__).resolve().parent/'verificacion'
OUT.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1000},accept_downloads=True)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://127.0.0.1:8765')
    page.wait_for_function("document.getElementById('status').textContent.startsWith('Datos locales cargados')",timeout=60000)
    assert page.locator('#eligible').inner_text()=='1,144'
    page.locator('#stable').uncheck()
    assert page.locator('#eligible').inner_text()=='1,783'
    page.locator('#state').select_option('01')
    page.locator('#search').fill('01001')
    assert page.locator('#eligible').inner_text()=='1'
    page.locator('#ranking button').first.click()
    assert 'AGUASCALIENTES' in page.locator('#detail-name').inner_text()
    page.locator('#search').fill('')
    page.locator('#state').select_option('')
    page.locator('#response').fill('0')
    assert page.locator('#before').inner_text()==page.locator('#after').inner_text()
    page.locator('#capacity').fill('2')
    page.locator('#response').fill('25')
    assert page.locator('#selected').inner_text()=='2'
    with page.expect_download() as d:page.locator('#export').click()
    d.value.save_as(OUT/'plan.csv')
    rows=list(csv.DictReader((OUT/'plan.csv').open(encoding='utf-8-sig',newline='')))
    assert len(rows)==2 and all(float(r['respuesta_supuesta_pct'])==25 for r in rows)
    assert all(float(r['alcance_limitado'])<=float(r['ln_referencia_2024']) for r in rows)
    page.locator('#search').fill('noexiste123')
    assert page.locator('#selected').inner_text()=='0' and page.locator('#export').is_disabled()
    page.locator('#search').fill('')
    page.locator('#reach').fill('-1')
    assert page.locator('#export').is_disabled()
    assert page.locator('#selected').inner_text()=='—'
    assert page.locator('#map').evaluate("e=>getComputedStyle(e).visibility")=='hidden'
    page.locator('#reach').fill('1000')
    page.locator('#capacity').fill('50')
    page.locator('#response').fill('5')
    page.locator('#stable').check()
    assert '8.58' in page.locator('#metrics').inner_text()
    assert page.locator('#map canvas').count()>0
    page.screenshot(path=str(OUT/'escritorio.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':844})
    page.reload()
    page.wait_for_function("document.getElementById('status').textContent.startsWith('Datos locales cargados')")
    assert page.evaluate('document.body.scrollWidth<=window.innerWidth'), 'Desbordamiento móvil'
    page.screenshot(path=str(OUT/'movil.png'),full_page=True)
    assert not errors,errors
    (OUT/'resultado.json').write_text(json.dumps({'passed':True,'checks':['cobertura','filtros','detalle','respuesta_cero','capacidad','exportacion','seleccion_vacia','entrada_invalida','metricas','mapa','movil'],'page_errors':errors},indent=2),encoding='utf-8')
    browser.close()
print('11 verificaciones de navegador correctas')
