"""Temporal: recorridos ampliados en demo5.html; detecta vista nacional con capa municipal visible."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '.task_packages'))
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
PAGE = 'demo5.html'

PROBE = """
(() => {
 const vis = n => { const p = map.getPane(n); return p ? getComputedStyle(p).visibility : 'missing'; };
 const b = map.getBounds(); const ext = b.getNorth()-b.getSouth();
 return {ext:+ext.toFixed(1), state:$('state').value, search:$('search').value, mun:vis('municipal-geography'),
   edo:vis('state-geography'), activo:(typeof demo5EstadoActivo==='undefined'?null:demo5EstadoActivo),
   modo:(typeof demo5ModoHistorico==='undefined'?null:demo5ModoHistorico), anio:currentMapYear,
   hist:geographyHistory.length, titulo:document.getElementById('map-title').textContent,
   fallo:(ext>18 && vis('municipal-geography')==='visible')};
})()
"""

PTO_ESTADO = """(key) => { const p=stateLayer.getLayers().find(l=>l.feature.properties.state===key);
  const c=map.latLngToContainerPoint(p.getBounds().getCenter()); return {x:c.x,y:c.y}; }"""
PTO_MUN = """(key) => { const p=layer.getLayers().find(l=>l.feature.properties.key===key);
  const c=map.latLngToContainerPoint(p.getBounds().getCenter()); return {x:c.x,y:c.y}; }"""
GRANDE = """(state) => { const bb=l=>{const x=l.getBounds();return (x.getNorth()-x.getSouth())*(x.getEast()-x.getWest());};
  const c=layer.getLayers().filter(l=>String(l.feature.properties.key).slice(0,2)===state)
    .map(l=>({key:String(l.feature.properties.key),area:bb(l)})).sort((a,b)=>b.area-a.area); return c.length?c[0].key:null; }"""


class Run:
    def __init__(self, page, box):
        self.page, self.box, self.fallos = page, box, []

    def probe(self, etiqueta):
        d = self.page.evaluate(PROBE)
        if d['fallo']:
            self.fallos.append((etiqueta, d))
            print('  !! FALLO', etiqueta, json.dumps(d, ensure_ascii=False))
        return d

    def click(self, pt, boton='left', wait=1100):
        self.page.mouse.click(self.box['x'] + pt['x'], self.box['y'] + pt['y'], button=boton)
        self.page.wait_for_timeout(wait)

    def estado_mapa(self, key='08'):
        self.click(self.page.evaluate(PTO_ESTADO, key))
        return self.probe('clic estado ' + key)

    def municipio_mapa(self, key):
        self.click(self.page.evaluate(PTO_MUN, key), wait=1200)
        return self.probe('clic municipio ' + key)

    def derecho(self, pt, n=1):
        for i in range(n):
            self.click(pt, boton='right', wait=1200)
            self.probe('clic derecho %d' % (i + 1))

    def estado_buscador(self, key='08'):
        self.page.evaluate("""(key)=>{ const s=document.getElementById('state'); s.value=key;
          document.getElementById('search').value='';
          s.dispatchEvent(new Event('input',{bubbles:true}));
          s.dispatchEvent(new Event('change',{bubbles:true})); }""", key)
        self.page.wait_for_timeout(1100)
        return self.probe('estado por buscador')

    def municipio_buscador(self, key, nombre):
        self.page.evaluate("""(arg)=>{
          document.getElementById('search').value=arg.nombre;
          document.getElementById('search').dispatchEvent(new Event('input',{bubbles:true}));
          const polygon=layer.getLayers().find(p=>p.feature.properties.key===arg.key);
          if(polygon && !(demo5ModoHistorico && currentMapYear!==2027) && typeof focusMunicipality==='function'){ focusMunicipality(arg.key, polygon); } }""",
            {'key': key, 'nombre': nombre})
        self.page.wait_for_timeout(1100)
        return self.probe('municipio por buscador')

    def anio(self, y):
        self.page.evaluate("""(y)=>{ const s=document.getElementById('map-year'); s.value=String(y);
          s.dispatchEvent(new Event('change',{bubbles:true})); }""", y)
        self.page.wait_for_timeout(1100)
        return self.probe('año ' + str(y))


with sync_playwright() as p:
    br = p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', headless=True)
    page = br.new_page(viewport={'width': 1600, 'height': 1400})
    errores = []
    page.on('pageerror', lambda e: errores.append(str(e)))
    page.goto((HERE / PAGE).as_uri())
    page.wait_for_function("typeof map!=='undefined' && map && typeof records!=='undefined' && typeof currentMapYear!=='undefined'", timeout=60000)
    page.wait_for_timeout(2000)
    page.evaluate("document.getElementById('map-year').value=String(currentMapYear)")

    def reiniciar():
        page.reload()
        page.wait_for_function("typeof map!=='undefined' && map && typeof records!=='undefined' && typeof currentMapYear!=='undefined'", timeout=60000)
        page.wait_for_timeout(2000)

    def mejor_mun():
        return page.evaluate(GRANDE, '08')

    def s1(r):
        r.estado_mapa(); m = r.municipio_mapa(mejor_mun()); r.derecho(m, 3)

    def s2(r):
        # clic en municipio, dos clics derechos, y clic en otro municipio
        r.estado_mapa(); m = r.municipio_mapa(mejor_mun()); r.derecho(m, 1)
        m2 = page.evaluate(GRANDE, '08')
        r.municipio_mapa(m2); r.derecho(m2, 4)

    def s3(r):
        r.estado_buscador(); m = r.municipio_mapa(mejor_mun()); r.derecho(m, 3)

    def s4(r):
        r.estado_buscador(); r.estado_mapa(); m = r.municipio_mapa(mejor_mun()); r.derecho(m, 4)

    def s5(r):
        # año histórico distinto de 2027
        r.anio(2024); r.estado_mapa(); m = r.municipio_mapa(mejor_mun()); r.derecho(m, 4)

    def s6(r):
        # municipio elegido en el buscador (con año 2024 se salta focusMunicipality)
        r.anio(2024); r.estado_buscador(); r.municipio_buscador('08001', 'AHUMADA')
        r.derecho(page.evaluate(PTO_MUN, '08001'), 4)

    def s7(r):
        # botón "Simular todos los municipios del estado"
        r.estado_mapa()
        page.evaluate("document.querySelector('#state-plan-panel button[onclick^=\"simularEstadoCompleto\"]').click()")
        page.wait_for_timeout(1200); r.probe('simular estado completo')
        r.derecho(page.evaluate(PTO_ESTADO, '08'), 4)

    def s8(r):
        # dos ciclos completos
        r.estado_mapa(); m = r.municipio_mapa(mejor_mun()); r.derecho(m, 3)
        r.estado_mapa(); m2 = r.municipio_mapa(mejor_mun()); r.derecho(m2, 4)
        r.estado_mapa(); m3 = r.municipio_mapa(mejor_mun()); r.derecho(m3, 4)

    def s9(r):
        # volver con el botón del plan y luego seguir navegando
        r.estado_mapa()
        page.evaluate("document.querySelector('#state-plan-panel button[onclick^=\"volverAMexico\"]').click()")
        page.wait_for_timeout(1200); r.probe('botón volver a nacional')
        r.estado_mapa(); m = r.municipio_mapa(mejor_mun()); r.derecho(m, 4)

    def s10(r):
        # cambiar el año estando en la vista de estado
        r.estado_mapa(); r.anio(2018); m = r.municipio_mapa(mejor_mun()); r.derecho(m, 4)

    def s11(r):
        # municipio por buscador en la vista de estado con año 2027
        r.estado_mapa(); r.municipio_buscador('08001', 'AHUMADA')
        r.derecho(page.evaluate(PTO_MUN, '08001'), 4)

    secuencias = [('S1', s1), ('S2', s2), ('S3', s3), ('S4', s4), ('S5', s5), ('S6', s6),
                  ('S7', s7), ('S8', s8), ('S9', s9), ('S10', s10), ('S11', s11)]
    total = 0
    for nombre, fn in secuencias:
        print('==', nombre)
        r = Run(page, page.locator('#map').bounding_box())
        r.probe('inicio')
        try:
            fn(r)
        except Exception as e:
            print('  excepción:', type(e).__name__, str(e)[:160])
        total += len(r.fallos)
        reiniciar()
    print('TOTAL fallos:', total, '| errores JS:', errores[:4])
    br.close()
