"""Temporal: batería de interacciones que detecta la vista nacional con capa municipal visible."""
import json
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / '.task_packages'))
from playwright.sync_api import sync_playwright

PAGE = sys.argv[1] if len(sys.argv) > 1 else 'demo5.html'

PROBE = """
(() => {
 const vis = n => { const p = map.getPane(n); return p ? getComputedStyle(p).visibility : 'missing'; };
 const b = map.getBounds();
 const nacional = (b.getNorth()-b.getSouth()) > 25;   // extensión de todo el país
 const mun = vis('municipal-geography'), edo = vis('state-geography');
 return {
   nacional, mun, edo,
   state: $('state').value, search: $('search').value,
   activo: (typeof demo5EstadoActivo==='undefined'?null:demo5EstadoActivo),
   zoom: map.getZoom(), history: geographyHistory.length,
   demo5Mun: !!(typeof demo5LayerMunicipal!=='undefined'&&demo5LayerMunicipal&&map.hasLayer(demo5LayerMunicipal)),
   fallo: (nacional && mun==='visible') || (mun==='visible' && !$('state').value && !(typeof demo5EstadoActivo!=='undefined'&&demo5EstadoActivo)),
 };
})()
"""

CLICK_ESTADO = """
(key) => {
  const p = stateLayer.getLayers().find(l=>l.feature.properties.state===key);
  if(!p) return null;
  const pt = map.latLngToContainerPoint(p.getBounds().getCenter());
  return {x:pt.x, y:pt.y};
}
"""

CLICK_MUN = """
(key) => {
  const p = layer.getLayers().find(l=>l.feature.properties.key===key);
  if(!p) return null;
  const pt = map.latLngToContainerPoint(p.getBounds().getCenter());
  return {x:pt.x, y:pt.y};
}
"""

BIGGEST = """
(state) => {
  const bb = l => { const x = l.getBounds(); return (x.getNorth()-x.getSouth())*(x.getEast()-x.getWest()); };
  const c = layer.getLayers().filter(l=>String(l.feature.properties.key).slice(0,2)===state)
    .map(l=>({key:String(l.feature.properties.key), area:bb(l)})).sort((a,b)=>b.area-a.area);
  return c.length ? c[0].key : null;
}
"""


class Runner:
    def __init__(self, page, box):
        self.page, self.box = page, box
        self.violations = []

    def probe(self, etiqueta):
        d = self.page.evaluate(PROBE)
        if d['fallo']:
            self.violations.append((etiqueta, d))
            print('  !! FALLO en', etiqueta, json.dumps(d, ensure_ascii=False))
        return d

    def click(self, pt, boton='left', wait=900):
        self.page.mouse.click(self.box['x'] + pt['x'], self.box['y'] + pt['y'], button=boton)
        self.page.wait_for_timeout(wait)

    def click_estado(self, key='08'):
        pt = self.page.evaluate(CLICK_ESTADO, key)
        if pt:
            self.click(pt)
            self.probe('clic estado ' + key)
        return pt

    def click_municipio(self, key):
        pt = self.page.evaluate(CLICK_MUN, key)
        if pt:
            self.click(pt, wait=1100)
            self.probe('clic municipio ' + key)
        return pt

    def derecho(self, pt, n=1):
        for i in range(n):
            self.click(pt, boton='right', wait=1200)
            self.probe('clic derecho %d' % (i + 1))

    def reset(self):
        self.page.evaluate("typeof volverAMexico==='function' ? volverAMexico() : returnToMexico()")
        self.page.wait_for_timeout(800)


def run(page, nombre, secuencia):
    print('==', nombre)
    box = page.locator('#map').bounding_box()
    r = Runner(page, box)
    r.probe('inicio')
    secuencia(r)
    return r.violations


with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        headless=True)
    page = browser.new_page(viewport={'width': 1600, 'height': 1400})
    errores = []
    page.on('pageerror', lambda e: errores.append(str(e)))
    page.goto((HERE / PAGE).as_uri())
    page.wait_for_function("typeof map!=='undefined' && map && typeof records!=='undefined'", timeout=60000)
    page.wait_for_timeout(1800)

    todos = []

    def s1(r):
        r.click_estado()
        r.derecho(r.page.evaluate(CLICK_ESTADO, '08') or {'x': 200, 'y': 150}, 2)

    def s2(r):
        r.click_estado()
        pt = r.click_municipio(r.page.evaluate(BIGGEST, '08'))
        r.derecho(pt, 3)

    def s3(r):
        r.click_estado()
        pt = r.click_municipio(r.page.evaluate(BIGGEST, '08'))
        r.derecho(pt, 1)
        r.click_municipio(r.page.evaluate(BIGGEST, '08'))
        r.derecho(pt, 3)

    def s4(r):
        r.click_estado()
        pt = r.click_municipio(r.page.evaluate(BIGGEST, '08'))
        r.page.evaluate("document.querySelector('#state-plan-panel button[onclick^=\"volverAMexico\"]')?.click()")
        r.page.wait_for_timeout(900)
        r.probe('boton volver a nacional')
        r.derecho(pt if pt else {'x': 300, 'y': 200}, 2)

    def s5(r):
        # simulación de estado (desactiva el modo histórico de demo5)
        r.click_estado()
        r.page.evaluate("document.querySelector('#state-plan-panel button[onclick^=\"simularEstadoCompleto\"]')?.click()")
        r.page.wait_for_timeout(1200)
        r.probe('simular estado completo')
        r.derecho(r.page.evaluate(CLICK_ESTADO, '08') or {'x': 300, 'y': 200}, 3)

    def s6(r):
        # estado vía buscador y luego clic en mapa
        r.page.evaluate("""
          (function(){
            const s=document.getElementById('state');
            s.value='08';
            s.dispatchEvent(new Event('input',{bubbles:true}));
            s.dispatchEvent(new Event('change',{bubbles:true}));
          })()""")
        r.page.wait_for_timeout(1000)
        r.probe('estado por buscador')
        pt = r.click_estado()
        r.derecho(pt or {'x': 300, 'y': 200}, 3)

    def s7(r):
        r.click_estado()
        pt = r.click_municipio(r.page.evaluate(BIGGEST, '08'))
        r.derecho(pt, 1)
        r.page.evaluate("document.getElementById('map-year') && document.getElementById('map-year').dispatchEvent(new Event('change'))")
        r.page.wait_for_timeout(900)
        r.probe('cambio de año')
        r.derecho(pt, 3)

    def s8(r):
        r.click_estado()
        pt = r.click_municipio(r.page.evaluate(BIGGEST, '08'))
        r.page.evaluate("document.getElementById('stable').checked=true;document.getElementById('stable').dispatchEvent(new Event('input',{bubbles:true}))")
        r.page.wait_for_timeout(900)
        r.probe('filtro catálogo')
        r.derecho(pt, 4)

    secuencias = [('S1 estado+2 derecho', s1), ('S2 estado+municipio+3 derecho', s2),
                  ('S3 municipio, derecho, municipio, 3 derecho', s3),
                  ('S4 botón volver a nacional', s4), ('S5 simular estado completo', s5),
                  ('S6 estado por buscador', s6), ('S7 cambio de año', s7), ('S8 filtro catálogo', s8)]
    for nombre, fn in secuencias:
        try:
            todos += run(page, nombre, fn)
            page.reload()
            page.wait_for_function("typeof map!=='undefined' && map && typeof records!=='undefined'", timeout=60000)
            page.wait_for_timeout(1600)
        except Exception as e:
            print('  error en', nombre, e)
    print('TOTAL fallos:', len(todos))
    print('ERRORES JS:', errores[:5])
    browser.close()
