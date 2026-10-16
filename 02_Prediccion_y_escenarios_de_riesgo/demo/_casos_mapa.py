"""Temporal: casos concretos de aceptación del arreglo de niveles del mapa."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / '.task_packages'))
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
PROBE = """
(() => {
 const vis = n => { const p = map.getPane(n); return p ? getComputedStyle(p).visibility : 'missing'; };
 const b = map.getBounds(); const ext = b.getNorth()-b.getSouth();
 return {ext:+ext.toFixed(1), nacional: ext>18, estado:$('state').value,
   activo:(typeof demo5EstadoActivo==='undefined'?null:demo5EstadoActivo),
   modo:(typeof demo5ModoHistorico==='undefined'?null:demo5ModoHistorico),
   mun:vis('municipal-geography'), edo:vis('state-geography'),
   panel:(()=>{const e=document.getElementById('state-plan-panel'); return e? !e.hidden : null;})(),
   demo5Mun:!!(typeof demo5LayerMunicipal!=='undefined'&&demo5LayerMunicipal&&map.hasLayer(demo5LayerMunicipal)),
   detalle:document.getElementById('detail-name').textContent};
})()
"""
ESTADOS_PICKER = """
(key) => {
  const s = document.getElementById('state');
  s.value = key;
  document.getElementById('search').value = '';
  s.dispatchEvent(new Event('input', {bubbles:true}));
  s.dispatchEvent(new Event('change', {bubbles:true}));
}
"""


def ok(cond, texto):
    print(('  OK  ' if cond else '  FALLA ') + texto)
    return bool(cond)


with sync_playwright() as p:
    br = p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', headless=True)
    errores = []
    fallos = 0

    # ---------- demo5: buscador ----------
    page = br.new_page(viewport={'width': 1600, 'height': 1400})
    page.on('pageerror', lambda e: errores.append(str(e)))
    page.goto((HERE / 'demo5.html').as_uri())
    page.wait_for_function("typeof map!=='undefined' && map && typeof records!=='undefined' && typeof currentMapYear!=='undefined'", timeout=60000)
    page.wait_for_timeout(2100)
    page.locator('#map').scroll_into_view_if_needed()
    page.wait_for_timeout(400)
    print('demo5 · caso 1: elijo Chihuahua en el buscador')
    page.evaluate(ESTADOS_PICKER, '08')
    page.wait_for_timeout(1400)
    d = page.evaluate(PROBE)
    print('   ', json.dumps(d, ensure_ascii=False))
    fallos += not ok(d['estado'] == '08' and d['activo'] == '08' and d['mun'] == 'visible' and d['edo'] == 'hidden'
                     and not d['nacional'] and d['panel'], 'vista de estado con municipios y plan visible')

    print('demo5 · caso 2: elijo "Todo México" en el buscador')
    page.evaluate(ESTADOS_PICKER, '')
    page.wait_for_timeout(1600)
    d = page.evaluate(PROBE)
    print('   ', json.dumps(d, ensure_ascii=False))
    fallos += not ok(d['estado'] == '' and d['activo'] is None and d['nacional'] and d['mun'] == 'hidden'
                     and d['edo'] == 'visible' and not d['panel'], 'vista nacional con promedio por estado y sin municipios')

    print('demo5 · caso 3: otra vez desde el buscador y luego "Todo México" (repetido)')
    page.evaluate(ESTADOS_PICKER, '30')
    page.wait_for_timeout(1300)
    page.evaluate(ESTADOS_PICKER, '')
    page.wait_for_timeout(1500)
    d = page.evaluate(PROBE)
    fallos += not ok(d['nacional'] and d['mun'] == 'hidden' and d['activo'] is None, 'sigue coherente tras repetir')

    print('demo5 · caso 4: recorrido de clics (estado, municipio, clic derecho)')
    box = page.locator('#map').bounding_box()
    st = page.evaluate("""(()=>{const p=stateLayer.getLayers().find(l=>l.feature.properties.state==='08');
        const c=map.latLngToContainerPoint(p.getBounds().getCenter()); return {x:c.x,y:c.y};})()""")
    page.mouse.click(box['x'] + st['x'], box['y'] + st['y'])
    page.wait_for_timeout(1300)
    d1 = page.evaluate(PROBE)
    fallos += not ok(d1['activo'] == '08' and d1['mun'] == 'visible', 'clic en estado abre municipios')
    mun = page.evaluate("""(()=>{const bb=l=>{const x=l.getBounds();return (x.getNorth()-x.getSouth())*(x.getEast()-x.getWest());};
        const c=layer.getLayers().filter(l=>String(l.feature.properties.key).slice(0,2)==='08').map(l=>({key:String(l.feature.properties.key),area:bb(l)})).sort((a,b)=>b.area-a.area);
        const p=layer.getLayers().find(l=>l.feature.properties.key===c[0].key);
        const pt=map.latLngToContainerPoint(p.getBounds().getCenter()); return {x:pt.x,y:pt.y,key:c[0].key};})()""")
    page.mouse.click(box['x'] + mun['x'], box['y'] + mun['y'])
    page.wait_for_timeout(1300)
    d2 = page.evaluate(PROBE)
    fallos += not ok(d2['ext'] < 3 and d2['detalle'] != 'Selecciona un municipio', 'clic en municipio acerca y abre su ficha')
    muelles = []
    for i in range(3):
        page.mouse.click(box['x'] + mun['x'], box['y'] + mun['y'], button='right')
        page.wait_for_timeout(1300)
        muelles.append(page.evaluate(PROBE))
    fallos += not ok(muelles[0]['ext'] > 3 and muelles[0]['mun'] == 'visible', 'primer clic derecho vuelve a la vista del estado')
    fallos += not ok(muelles[-1]['nacional'] and muelles[-1]['mun'] == 'hidden' and muelles[-1]['activo'] is None,
                     'clic derecho hasta la vista nacional con promedio por estado')

    print('demo5 · caso 5: tras volver a nacional, un municipio sigue abriendo ficha (segundo ciclo)')
    page.evaluate(ESTADOS_PICKER, '08')
    page.wait_for_timeout(1300)
    mun2 = page.evaluate("""(()=>{const bb=l=>{const x=l.getBounds();return (x.getNorth()-x.getSouth())*(x.getEast()-x.getWest());};
        const c=layer.getLayers().filter(l=>String(l.feature.properties.key).slice(0,2)==='08').map(l=>({key:String(l.feature.properties.key),area:bb(l)})).sort((a,b)=>b.area-a.area);
        const p=layer.getLayers().find(l=>l.feature.properties.key===c[0].key);
        const pt=map.latLngToContainerPoint(p.getBounds().getCenter()); return {x:pt.x,y:pt.y};})()""")
    box = page.locator('#map').bounding_box()
    page.mouse.click(box['x'] + mun2['x'], box['y'] + mun2['y'])
    page.wait_for_timeout(1300)
    d3 = page.evaluate(PROBE)
    fallos += not ok(d3['ext'] < 3 and d3['detalle'] != 'Selecciona un municipio', 'segundo ciclo sigue abriendo la ficha')
    page.close()

    # ---------- index.html: segundo ciclo (el hack eliminado) ----------
    page = br.new_page(viewport={'width': 1600, 'height': 1400})
    page.on('pageerror', lambda e: errores.append('index: ' + str(e)))
    page.goto((HERE / 'index.html').as_uri())
    page.wait_for_function("document.getElementById('eligible').textContent!=='—'", timeout=60000)
    page.wait_for_timeout(1200)
    page.locator('#map').scroll_into_view_if_needed()
    page.wait_for_timeout(400)
    print('index.html · caso 6: ciclo completo de clics + segundo ciclo')
    box = page.locator('#map').bounding_box()
    st = page.evaluate("""(()=>{const p=stateLayer.getLayers().find(l=>l.feature.properties.state==='08');
        const c=map.latLngToContainerPoint(p.getBounds().getCenter()); return {x:c.x,y:c.y};})()""")
    page.mouse.click(box['x'] + st['x'], box['y'] + st['y'])
    page.wait_for_timeout(1200)
    mun = page.evaluate("""(()=>{const bb=l=>{const x=l.getBounds();return (x.getNorth()-x.getSouth())*(x.getEast()-x.getWest());};
        const c=layer.getLayers().filter(l=>String(l.feature.properties.key).slice(0,2)==='08').map(l=>({key:String(l.feature.properties.key),area:bb(l)})).sort((a,b)=>b.area-a.area);
        const p=layer.getLayers().find(l=>l.feature.properties.key===c[0].key);
        const pt=map.latLngToContainerPoint(p.getBounds().getCenter()); return {x:pt.x,y:pt.y};})()""")
    page.mouse.click(box['x'] + mun['x'], box['y'] + mun['y'])
    page.wait_for_timeout(1200)
    for i in range(3):
        page.mouse.click(box['x'] + mun['x'], box['y'] + mun['y'], button='right')
        page.wait_for_timeout(1200)
    d = page.evaluate(PROBE)
    fallos += not ok(d['nacional'] and d['mun'] == 'hidden' and d['estado'] == '', 'index.html vuelve a la vista nacional')
    page.mouse.click(box['x'] + st['x'], box['y'] + st['y'])
    page.wait_for_timeout(1200)
    box = page.locator('#map').bounding_box()
    mun = page.evaluate("""(()=>{const bb=l=>{const x=l.getBounds();return (x.getNorth()-x.getSouth())*(x.getEast()-x.getWest());};
        const c=layer.getLayers().filter(l=>String(l.feature.properties.key).slice(0,2)==='08').map(l=>({key:String(l.feature.properties.key),area:bb(l)})).sort((a,b)=>b.area-a.area);
        const p=layer.getLayers().find(l=>l.feature.properties.key===c[0].key);
        const pt=map.latLngToContainerPoint(p.getBounds().getCenter()); return {x:pt.x,y:pt.y};})()""")
    page.mouse.click(box['x'] + mun['x'], box['y'] + mun['y'])
    page.wait_for_timeout(1200)
    d = page.evaluate(PROBE)
    print('   ', json.dumps(d, ensure_ascii=False))
    fallos += not ok(d['ext'] < 3 and d['detalle'] != 'Selecciona un municipio', 'segundo ciclo abre ficha sin errores')
    page.close()

    print('errores JS:', errores)
    print('FALLOS:', fallos)
    br.close()
