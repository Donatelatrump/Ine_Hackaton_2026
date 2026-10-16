"""Temporal: reproduce la secuencia de clics y captura solo el mapa, sin elementos de página encima."""
import json
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / '.task_packages'))
from playwright.sync_api import sync_playwright

PAGE = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
TAG = PAGE.replace('.html', '')

STATE = """
(() => {
 const panes = {};
 for (const n of ['municipal-geography','state-geography','demo4-land-mask']) {
   const p = map.getPane(n);
   panes[n] = p ? getComputedStyle(p).visibility : 'missing';
 }
 return {
   panes,
   state: $('state').value, search: $('search').value,
   activo: (typeof demo5EstadoActivo==='undefined'?null:demo5EstadoActivo),
   modoHistorico: (typeof demo5ModoHistorico==='undefined'?null:demo5ModoHistorico),
   focus: (typeof geographyFocusKey==='undefined'?null:geographyFocusKey),
   history: geographyHistory.length,
   zoom: map.getZoom(),
   demo5Mun: !!(typeof demo5LayerMunicipal!=='undefined'&&demo5LayerMunicipal&&map.hasLayer(demo5LayerMunicipal)),
   demo5Edo: !!(typeof demo5LayerEstado!=='undefined'&&demo5LayerEstado&&map.hasLayer(demo5LayerEstado)),
 };
})()
"""

CENTER_ESTADO = """
(key) => {
  const p = stateLayer.getLayers().find(l=>l.feature.properties.state===key);
  if(!p) return null;
  const pt = map.latLngToContainerPoint(p.getBounds().getCenter());
  return {x:pt.x, y:pt.y, key:key};
}
"""

CENTER_MUN = """
(key) => {
  const p = layer.getLayers().find(l=>l.feature.properties.key===key);
  if(!p) return null;
  const pt = map.latLngToContainerPoint(p.getBounds().getCenter());
  return {x:pt.x, y:pt.y, key:key};
}
"""

BIGGEST = """
(state) => {
  const b = l => { const x = l.getBounds(); return (x.getNorth()-x.getSouth())*(x.getEast()-x.getWest()); };
  const cands = layer.getLayers().filter(l=>String(l.feature.properties.key).slice(0,2)===state)
    .map(l=>({key:String(l.feature.properties.key), area:b(l)})).sort((a,b)=>b.area-a.area);
  return cands.length?cands[0].key:null;
}
"""

HIDE = "body :not(#map):not(#map *) { visibility: hidden !important; }"


def report(page, label):
    print('---', label, json.dumps(page.evaluate(STATE), ensure_ascii=False))


def shot(page, name):
    page.locator('#map').screenshot(path=str(HERE / ('_repro_%s_%s.png' % (name, TAG))))


with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        headless=True)
    page = browser.new_page(viewport={'width': 1600, 'height': 1400})
    page.on('pageerror', lambda e: print('PAGEERROR:', e))
    page.on('console', lambda m: print('CONSOLE:', m.text) if 'demo5' in m.text else None)
    page.goto((HERE / PAGE).as_uri())
    page.wait_for_function("typeof map!=='undefined' && map && typeof records!=='undefined'", timeout=60000)
    page.wait_for_timeout(1800)
    page.add_style_tag(content=HIDE)
    page.wait_for_timeout(300)
    report(page, 'inicio')
    shot(page, 'inicio')
    box = page.locator('#map').bounding_box()

    for state_key in ['08', '26', '30', '14', '21']:
        pt = page.evaluate(CENTER_ESTADO, state_key)
        if not pt:
            continue
        page.mouse.click(box['x'] + pt['x'], box['y'] + pt['y'])
        page.wait_for_timeout(900)
        if page.evaluate("document.getElementById('state').value") == state_key:
            print('estado elegido', state_key)
            break
    report(page, 'tras clic estado')
    shot(page, 'estado')

    key = page.evaluate(BIGGEST, state_key)
    pt = page.evaluate(CENTER_MUN, key) if key else None
    print('municipio', key, pt)
    if pt:
        page.mouse.click(box['x'] + pt['x'], box['y'] + pt['y'])
        page.wait_for_timeout(1200)
    report(page, 'tras clic municipio')
    shot(page, 'municipio')

    for i in (1, 2, 3):
        if pt:
            page.mouse.click(box['x'] + pt['x'], box['y'] + pt['y'], button='right')
        page.wait_for_timeout(1400)
        report(page, f'clic derecho {i}')
        shot(page, 'derecho%d' % i)

    browser.close()
