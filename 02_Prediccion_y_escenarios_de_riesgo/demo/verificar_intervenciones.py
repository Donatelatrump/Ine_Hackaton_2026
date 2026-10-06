"""Verifica selector, aritmética, exportación y vista móvil en la demo file://."""
import csv
import tempfile
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '.task_packages'))
from playwright.sync_api import sync_playwright

with sync_playwright() as p, tempfile.TemporaryDirectory() as out:
    browser = p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 1000}, accept_downloads=True)
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(Path(__file__).with_name('index.html').as_uri())
    page.wait_for_function("document.getElementById('eligible').textContent === '1,144'", timeout=60000)
    assert page.locator('#action').input_value() == 'ninguna'
    assert page.locator('#before').inner_text() == page.locator('#after').inner_text()
    assert page.locator('#custom-response').is_hidden()
    page.locator('#action').select_option('sms_suecia')
    assert '0.3 pp' in page.locator('#action-evidence').inner_text()
    assert 'México' in page.locator('#action-evidence').inner_text()
    assert page.locator('#action-evidence a').get_attribute('href') == 'https://doi.org/10.1017/S0007123424000504'
    assert '0.13–0.48' in page.locator('#action-evidence').inner_text()
    assert 'No es un intervalo validado para México' in page.locator('#effect-range').inner_text()
    assert page.evaluate('Math.abs(plan.additional-plan.served*0.003)<1e-8')
    page.evaluate("document.getElementById('planning-settings').open=true")
    page.locator('#reach').fill('2000')
    assert page.evaluate('plan.served === 2000 && Math.abs(plan.additional-6)<1e-8')
    downloads=[]
    page.on('download',lambda d: downloads.append(d))
    page.locator('#export').click()
    page.wait_for_timeout(900)
    assert len(downloads)==2
    for d in downloads:
        d.save_as(str(Path(out)/d.suggested_filename))
    with (Path(out)/'Umbral_plan_municipios.csv').open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    assert rows and None not in rows[0]
    assert rows[0]['Estimador del estudio']=='ITT'
    assert rows[0]['URL fuente']=='https://doi.org/10.1017/S0007123424000504'
    assert rows[0]['Respuesta supuesta (%)']==''
    assert rows[0]['Votos adicionales límite inferior']!=''
    assert float(rows[0]['Reducción (pp)'])>0, 'No redondear a cero un efecto SMS pequeño'
    assert abs(float(rows[0]['Reducción (pp)'])-100*float(rows[0]['Personas adicionales que votarían (supuesto)'])/float(rows[0]['Base observable 2024 (SV+NV)']))<0.000051
    leeme=(Path(out)/'Umbral_plan_leeme.csv').read_text(encoding='utf-8-sig')
    assert 'Lindgren' in leeme and 'Transferencia' in leeme
    page.locator('#action').select_option('plan_voto')
    assert 'completarías la llamada' in page.locator('#reach-label').inner_text()
    assert '1.7 pp' in page.locator('#effect-range').inner_text()
    page.locator('#action').select_option('personalizada')
    assert page.locator('#custom-response').is_visible()
    assert page.evaluate("filtered.some(r=>!selectedMap.has(r.key))")
    page.evaluate("detail(filtered.find(r=>Number.isFinite(r.risk)&&!selectedMap.has(r.key)).key)")
    assert 'no factible o sin alcance' in page.locator('#detail-content').text_content() or 'Ya está en nivel bajo' in page.locator('#detail-content').text_content()
    page.locator('#response').fill('0')
    assert page.locator('#before').inner_text()==page.locator('#after').inner_text()
    page.locator('#action').select_option('sms_eeuu')
    assert '0.25 pp' in page.locator('#action-evidence').inner_text()
    assert 'planeas enviar el SMS en total' in page.locator('#reach-label').inner_text()
    national_population=page.evaluate('Decision.territorialScenario(filtered,plan).population')
    page.locator('#simulation-scope').select_option('estado')
    page.locator('#simulation-state').select_option('01')
    assert page.evaluate("filtered.every(r=>r.state==='01')")
    assert page.evaluate('Decision.territorialScenario(filtered,plan).population')<national_population
    page.locator('#simulation-scope').select_option('municipio')
    page.locator('#simulation-municipality').select_option('01001')
    assert page.evaluate("filtered.length===1 && filtered[0].key==='01001'")
    page.locator('#simulation-scope').select_option('pais')
    assert page.evaluate("document.getElementById('state').value==='' && document.getElementById('search').value===''")
    assert page.evaluate('Decision.territorialScenario(filtered,plan).population')==national_population
    assert 'municipios con estimación incluidos' in page.locator('#simulation-scope').inner_text()
    assert 'Cobertura de datos:' in page.locator('#scope-coverage').inner_text()
    priority_count=page.evaluate('plan.selected.length')
    page.locator('#distribution').select_option('proporcional')
    assert page.evaluate("plan.distribution==='proporcional' && plan.served===2000")
    assert page.evaluate('plan.selected.length')>priority_count
    assert page.evaluate('plan.selected.every(r=>Number.isInteger(r.served)&&r.served<=r.observed)')
    assert 'mayor resto' in page.locator('#distribution-help').inner_text()
    page.locator('#simulation-scope').select_option('municipio')
    page.locator('#simulation-state').select_option('01')
    page.locator('#simulation-municipality').select_option('01001')
    assert page.evaluate('filtered.length===1 && plan.selected.length===1 && plan.served===2000')
    page.locator('#simulation-scope').select_option('pais')
    page.locator('#distribution').select_option('prioridad')
    page.locator('#reach').fill('')
    assert page.locator('#export').is_disabled()
    page.locator('#reach').fill('1000')
    assert page.locator('#export').is_enabled()
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth+1')
    page.locator('#action').scroll_into_view_if_needed()
    page.screenshot(path=str(ROOT/'.task_packages/intervenciones_movil.png'))
    page.set_viewport_size({'width':1440,'height':1000})
    page.locator('#paso-3').scroll_into_view_if_needed()
    page.screenshot(path=str(ROOT/'.task_packages/intervenciones_escritorio.png'))
    assert not errors, errors
    browser.close()
print('OK: selector, 3 estudios, ITT/ATT, presupuesto, CSV con citas, entradas inválidas, móvil y file://; sin errores JS.')
