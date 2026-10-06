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
    assert page.locator('#explore-entry').is_visible()
    page.locator('#plan-entry').click()
    assert page.locator('#planning-settings').evaluate('e=>e.open')
    assert '50 municipios' in page.locator('#scenario-assumptions').inner_text()
    assert page.locator('#documents a').count()>=5
    assert 'Pendiente de corrección' in page.locator('#report-status').inner_text()
    page.locator('#planning-settings summary').click()
    assert 'Filtro activo' in page.locator('#filter-summary').inner_text()
    assert not page.locator('#planning-settings').evaluate('e=>e.open')
    page.locator('#show-all').click()
    assert page.locator('#eligible').inner_text()=='1,783'
    assert not page.locator('#show-all').is_visible()
    page.locator('a[href="#planning-settings"]').first.click()
    assert page.locator('#planning-settings').evaluate('e=>e.open')
    page.locator('#settings summary').click()
    page.locator('#stable').uncheck()
    assert page.locator('#eligible').inner_text()=='1,783'
    assert page.locator('#missing-count').inner_text()=='694'
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
    assert '2 municipios' in page.locator('#scenario-assumptions').inner_text()
    assert '25%' in page.locator('#scenario-assumptions').inner_text()
    page.locator('#confidence').check()
    page.locator('[data-scenario-map="cambio"]').click()
    assert page.locator('#map-mode').input_value()=='cambio'
    assert not page.locator('#confidence').is_checked()
    page.locator('[data-scenario-map="base"]').click()
    with page.expect_download() as d:page.locator('#export').click()
    d.value.save_as(OUT/'plan.csv')
    rows=list(csv.DictReader((OUT/'plan.csv').open(encoding='utf-8-sig',newline='')))
    assert len(rows)==2 and all(float(r['Respuesta supuesta (%)'])==25 for r in rows)
    assert all(float(r['Personas alcanzadas (supuesto)'])<=float(r['Base observable 2024 (SV+NV)']) for r in rows)
    assert all(abs(float(r['No votarían (con acción, %)'])-(float(r['No votarían (estimado 2027, %)'])-100*float(r['Personas adicionales que votarían (supuesto)'])/float(r['Base observable 2024 (SV+NV)'])))<0.011 for r in rows)
    assert all(r['Entidad']==r['Entidad'].title() and r['Municipio']==r['Municipio'].title() for r in rows), 'Nombres en formato título'
    assert [int(r['Puesto']) for r in rows]==[1,2], 'Puesto consecutivo desde 1'
    with page.expect_download() as d:page.locator('#export').click()
    d.value.save_as(OUT/'leeme.csv')
    doc=list(csv.reader((OUT/'leeme.csv').open(encoding='utf-8-sig',newline='')))
    assert doc[0]==['Sección','Elemento','Detalle'], 'Encabezado del leeme'
    sec={r[0] for r in doc[1:]}
    assert {'Documento','Filtros aplicados','Simulación','Resumen del plan','Diccionario de columnas','Limitaciones'}<=sec, 'Secciones del leeme completas'
    page.locator('#search').fill('noexiste123')
    assert page.locator('#selected').inner_text()=='0' and page.locator('#export').is_disabled()
    page.locator('#search').fill('')
    page.locator('#reach').fill('-1')
    assert 'Corrige' in page.locator('#scenario-assumptions').inner_text()
    assert page.locator('#export').is_disabled()
    assert page.locator('#selected').inner_text()=='—'
    assert page.locator('#map').evaluate("e=>getComputedStyle(e).visibility")=='hidden'
    page.locator('#reach').fill('1000')
    page.locator('#capacity').fill('50')
    page.locator('#response').fill('5')
    page.locator('#stable').check()
    assert not page.locator('.technical-details').evaluate('e=>e.open')
    page.locator('.technical-details > summary').click()
    assert '8.58' in page.locator('#metrics').inner_text()
    page.locator('.technical-details > summary').click()
    page.locator('#response').fill('100')
    page.locator('#reach').fill('1000000')
    key=page.evaluate('plan.selected[0].key')
    baseline_color=page.evaluate("layer.getLayers().find(l=>l.feature.properties.key==='"+key+"').options.fillColor")
    page.locator('#map-mode').select_option('intervencion')
    scenario_color=page.evaluate("layer.getLayers().find(l=>l.feature.properties.key==='"+key+"').options.fillColor")
    assert baseline_color!=scenario_color
    assert page.locator('#after').inner_text()=='0.00%'
    page.locator('#map-mode').select_option('cambio')
    assert 'reducción' in page.locator('#map-caption').inner_text().lower()
    assert '60%' in page.locator('.map-guide').inner_text()
    page.locator('#confidence').check()
    assert '6/6' in page.locator('#confidence-note').inner_text()
    assert '6 de 6' in page.locator('#map-caption').inner_text()
    assert 'nunca entran' in page.locator('.map-guide').inner_text()
    page.locator('#confidence').uncheck()
    page.locator('#method').select_option('baseline')
    assert page.evaluate('byKey.get(plan.selected[0].key).risk===byKey.get(plan.selected[0].key).baseline')
    page.locator('#method').select_option('ridge')
    page.locator('.lens-card[data-lens="volumen"]').click()
    assert page.locator('.lens-card[data-lens="volumen"]').get_attribute('aria-checked')=='true'
    assert page.locator('.lens-card[data-lens="tasa"]').get_attribute('aria-checked')=='false'
    assert page.locator('#lens').input_value()=='volumen'
    assert page.evaluate('plan.selected[0].risk*plan.selected[0].observed>=plan.selected[1].risk*plan.selected[1].observed')
    page.locator('.lens-card[data-lens="deterioro"]').click()
    assert page.locator('#lens').input_value()=='deterioro'
    assert page.evaluate('plan.selected[0].risk-plan.selected[0].baseline>=plan.selected[1].risk-plan.selected[1].baseline')
    page.locator('.lens-card[data-lens="tasa"]').click()
    assert page.locator('#lens').input_value()=='tasa'
    page.evaluate("document.querySelector('.lens-card[data-lens=\"volumen\"]').focus()")
    page.keyboard.press('Enter')
    assert page.locator('#lens').input_value()=='volumen', 'Enter en tarjeta debe cambiar el criterio'
    page.locator('.lens-card[data-lens="tasa"]').click()
    assert page.locator('#lens').input_value()=='tasa'
    assert page.evaluate("document.querySelector('.lens-card[data-lens=\"tasa\"]').tabIndex==0&&document.querySelector('.lens-card[data-lens=\"volumen\"]').tabIndex==-1"), 'Roving tabindex en las tarjetas'
    assert page.locator('#entity-table tr').count()>0
    page.locator('#ranking button').first.click()
    assert '¿Por qué está aquí?' in page.locator('#detail-content').inner_text()
    assert 'Acción sugerida' in page.locator('#detail-content').inner_text()
    assert 'Perfil CCPC observado 2024' in page.locator('#detail-content').text_content()
    assert page.locator('#plan-summary strong').count()>=8
    assert page.locator('#frontier-summary').text_content().strip() not in ('','—')
    assert page.locator('#frontier-table > div').count()==3
    assert page.locator('#perfil-nacional tr').count()>=8
    page.locator('#capacity-mode').select_option('personas')
    page.locator('#persons').fill('100000')
    page.locator('#reach').fill('1000')
    page.locator('#response').fill('25')
    assert page.evaluate('plan.selected.length')>0 and page.evaluate('plan.served<=100000+1e-6')
    page.locator('#capacity-mode').select_option('municipios')
    page.locator('#capacity').fill('50')
    page.locator('#response').fill('5')
    page.locator('#min-confidence').select_option('media')
    media=int(page.locator('#selected').inner_text())
    page.locator('#min-confidence').select_option('todas')
    assert int(page.locator('#selected').inner_text())>=media
    page.evaluate("detail(records.find(r=>r.risk===null).key)")
    assert 'supera' in page.locator('#detail-content').inner_text() or 'sin' in page.locator('#detail-content').inner_text().lower()
    assert 'Prioridad 0' not in page.locator('#detail-state').inner_text(), 'Un municipio sin estimación no tiene puesto cero'
    assert 'No significa riesgo bajo' in page.locator('#detail-content').inner_text()
    assert 'Zona de revisión' not in page.locator('#detail-content').inner_text(), 'Sin datos no equivale a frontera predictiva'
    page.locator('#sin-estimacion details > summary').click()
    missing_key=page.locator('.missing-row').first.get_attribute('data-key')
    page.locator('.missing-row').first.click()
    assert missing_key in page.locator('#detail-state').inner_text()
    assert 'Sin prioridad predictiva' in page.locator('#detail-state').inner_text()
    assert page.evaluate('!plan.selected.some(r=>r.key===activeKey)')
    page.locator('#sin-estimacion details > summary').click()
    page.evaluate("detail('23008')")
    page.locator('#state').select_option('01')
    assert 'Prioridad 0' not in page.locator('#detail-state').inner_text()
    assert 'Fuera del filtro actual' in page.locator('#detail-state').inner_text()
    assert 'coinciden dentro' not in page.locator('#detail-content').inner_text()
    page.locator('#state').select_option('')
    page.locator('#response').fill('25')
    page.locator('#reach').fill('10000')
    page.locator('#map-mode').select_option('base')
    page.locator('#ranking button').first.click()
    assert page.locator('#map canvas').count()>0
    page.locator('.map-panel').screenshot(path=str(OUT/'mapa_base.png'))
    page.screenshot(path=str(OUT/'escritorio.png'),full_page=True)
    page.locator('#map-mode').select_option('intervencion')
    page.locator('.map-panel').screenshot(path=str(OUT/'mapa_intervencion.png'))
    page.locator('#map-mode').select_option('cambio')
    page.locator('.map-panel').screenshot(path=str(OUT/'mapa_cambio.png'))
    page.set_viewport_size({'width':390,'height':844})
    page.reload()
    page.wait_for_function("document.getElementById('status').textContent.startsWith('Datos locales cargados')")
    assert page.evaluate('document.body.scrollWidth<=window.innerWidth'), 'Desbordamiento móvil'
    page.screenshot(path=str(OUT/'movil.png'),full_page=True)
    offline=browser.new_page(viewport={'width':1440,'height':1000})
    offline.on('pageerror',lambda e:errors.append(str(e)))
    offline.goto((Path(__file__).resolve().parent/'index.html').as_uri())
    offline.wait_for_function("document.getElementById('status').textContent.startsWith('Datos locales cargados')")
    assert offline.locator('#eligible').inner_text()=='1,144'
    offline.locator('#map-mode').select_option('intervencion')
    assert offline.locator('#map canvas').count()>0
    assert not errors,errors
    (OUT/'resultado.json').write_text(json.dumps({'passed':True,'checks':['cobertura','filtros','detalle','respuesta_cero','capacidad','exportacion_denominador','seleccion_vacia','entrada_invalida','metricas','mapa','movil','capas_escenario','delta','estabilidad','metodos','lentes','entidades','fichas_y_exclusiones','plan_sugerido','frontera','perfil_ccpc','capacidad_humana','confianza_minima','apertura_file','sin_estimacion_sin_puesto','consulta_exclusiones','evidencia_desplegable','ficha_fuera_del_filtro'],'page_errors':errors},indent=2),encoding='utf-8')
    browser.close()
print('28 verificaciones de navegador correctas, incluida apertura file:// y municipios sin estimación')
