"""Comprueba el recorrido de consulta y la activación de la simulación."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '.task_packages'))
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 1000})
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(Path(__file__).with_name('index.html').as_uri())
    page.wait_for_function("document.getElementById('eligible').textContent === '1,144'")
    assert page.locator('#simulation-results').count() == 1, 'Falta separar los resultados de simulación'
    assert page.locator('#simulation-results').is_hidden(), 'La consulta inicial no debe mostrar resultados de una acción'
    assert page.locator('#paso-3 #planning-settings').count() == 1, 'Prioridad y acción deben estar juntas'
    assert page.locator('#plan-entry').get_attribute('href') == '#paso-3'
    assert 'simulación' not in page.locator('#paso-2').inner_text().lower()
    page.locator('#municipality-list > summary').click()
    assert page.locator('#ranking button').count() == 25, 'Se pueden explorar municipios antes de planear'
    page.locator('#ranking button').first.click()
    assert page.locator('#detail-content .fact-cards strong').count() == 2
    assert 'Acción del simulador' not in page.locator('#detail-content').inner_text()
    page.locator('#state-picker').fill('Aguascalientes')
    page.locator('#state-picker').press('Enter')
    page.locator('#search').fill('Aguascalientes')
    page.locator('#search').press('Enter')
    assert page.evaluate("filtered.length===1 && filtered[0].key==='01001'")
    page.locator('#municipality-list > summary').click() if not page.locator('#ranking').is_visible() else None
    page.locator('#ranking button').first.click()
    page.locator('#action').select_option('sms_suecia')
    assert page.locator('#simulation-results').is_visible()
    page.locator('#reach').fill('2000')
    assert page.evaluate('Math.abs(plan.additional-6)<1e-8')
    assert page.locator('#export').is_enabled()
    assert page.locator('#rounding-note').is_visible(), 'Un efecto pequeño debe explicarse sin aparentar cero'
    page.locator('#reach').fill('')
    assert page.locator('#map').is_visible(), 'Un error de cobertura no debe impedir explorar el mapa'
    assert page.locator('#detail-content .fact-cards strong').count() >= 2, 'La consulta municipal debe seguir disponible'
    assert page.locator('#simulation-results').is_hidden(), 'No presentar cifras pendientes como resultados válidos'
    assert page.locator('#export').is_disabled()
    page.locator('#reach').fill('2000')
    page.locator('#action-evidence summary').click()
    assert page.locator('#action-evidence a').first.is_visible(), 'La fuente debe seguir accesible'
    page.locator('#action').select_option('ninguna')
    assert page.locator('#simulation-results').is_hidden()
    assert page.locator('#map-mode').input_value() == 'base'
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth+1')
    assert page.locator('#detail').bounding_box()['y'] < page.locator('#municipality-list').bounding_box()['y']
    assert not errors, errors
    browser.close()
print('OK: consulta inicial, controles agrupados, ficha prioritaria, simulación opcional, fuentes y móvil.')
