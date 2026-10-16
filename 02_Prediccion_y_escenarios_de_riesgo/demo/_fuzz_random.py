"""Temporal: fuzz aleatorio de interacciones sobre demo5.html buscando incoherencias de nivel/paneles."""
import json
import random
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '.task_packages'))
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'demo5.html'
PROBE = """
(() => {
 const vis = n => { const p = map.getPane(n); return p ? getComputedStyle(p).visibility : 'missing'; };
 const b = map.getBounds(); const ext = b.getNorth()-b.getSouth();
 const mun = vis('municipal-geography'), edo = vis('state-geography');
 const activo = (typeof demo5EstadoActivo==='undefined'?null:demo5EstadoActivo);
 const modo = (typeof demo5ModoHistorico==='undefined'?null:demo5ModoHistorico);
 return {ext:+ext.toFixed(1), nacional: ext>18, state:$('state').value, activo, modo,
   mun, edo, hist:geographyHistory.length, focus:(typeof geographyFocusKey==='undefined'?null:geographyFocusKey),
   busqueda:$('search').value,
   panelesVisiblesNivel: (ext>18 ? (edo==='visible' && mun==='hidden') : true)};
})()
"""

PUNTOS = """
(() => {
  const out = {estados:{}, municipios:[]};
  for (const l of stateLayer.getLayers()) {
    const c = map.latLngToContainerPoint(l.getBounds().getCenter());
    out.estados[l.feature.properties.state] = {x:c.x, y:c.y};
  }
  for (const l of layer.getLayers()) {
    const key = l.feature.properties.key;
    if (!key.endsWith('001') && !key.endsWith('030')) continue;
    const c = map.latLngToContainerPoint(l.getBounds().getCenter());
    out.municipios.push({key:key, x:c.x, y:c.y});
  }
  return out;
})()
"""


def accion(page, box, pasos, rng):
    puntos = page.evaluate(PUNTOS)
    estados = list(puntos['estados'].items())
    eleccion = rng.random()
    if eleccion < 0.34 and puntos['municipios']:
        mun = rng.choice(puntos['municipios'])
        pt = {k: v for k, v in mun.items() if k != 'key'}
        boton = 'right' if rng.random() < 0.5 else 'left'
        page.mouse.click(box['x'] + pt['x'], box['y'] + pt['y'], button=boton)
        pasos.append('%s municipio %s' % (boton, mun['key']))
    elif eleccion < 0.62:
        key, pt = rng.choice(estados)
        page.mouse.click(box['x'] + pt['x'], box['y'] + pt['y'])
        pasos.append('clic estado ' + key)
    elif eleccion < 0.74:
        key = rng.choice(estados)[0]
        page.evaluate("""(k)=>{const s=document.getElementById('state'); s.value=k;
          document.getElementById('search').value='';
          s.dispatchEvent(new Event('input',{bubbles:true}));
          s.dispatchEvent(new Event('change',{bubbles:true}));}""", key)
        pasos.append('buscador estado ' + key)
    elif eleccion < 0.82:
        page.evaluate("""()=>{const s=document.getElementById('state'); s.value='';
          document.getElementById('search').value='';
          s.dispatchEvent(new Event('input',{bubbles:true}));
          s.dispatchEvent(new Event('change',{bubbles:true}));}""")
        pasos.append('buscador Todo México')
    elif eleccion < 0.88:
        y = rng.choice([2009, 2012, 2015, 2018, 2021, 2024, 2027])
        page.evaluate("""(y)=>{const s=document.getElementById('map-year'); if(!s) return; s.value=String(y); s.dispatchEvent(new Event('change',{bubbles:true}));}""", y)
        pasos.append('año ' + str(y))
    elif eleccion < 0.93:
        visible = page.evaluate("""()=>{const b=document.querySelector('#state-plan-panel button[onclick^="volverAMexico"]'); return !!(b && b.getClientRects().length);}""")
        if visible:
            page.evaluate("""()=>{const b=document.querySelector('#state-plan-panel button[onclick^="volverAMexico"]'); if(b) b.click();}""")
            pasos.append('botón volver a nacional')
    elif eleccion < 0.97:
        visible = page.evaluate("""()=>{const b=document.querySelector('#state-plan-panel button[onclick^="simularEstadoCompleto"]'); return !!(b && b.getClientRects().length);}""")
        if visible:
            page.evaluate("""()=>{const b=document.querySelector('#state-plan-panel button[onclick^="simularEstadoCompleto"]'); if(b) b.click();}""")
            pasos.append('botón simular estado')
    else:
        page.evaluate("""()=>{const s=document.getElementById('stable'); s.checked=!s.checked;
          s.dispatchEvent(new Event('input',{bubbles:true}));}""")
        pasos.append('alternar filtro catálogo')
    page.wait_for_timeout(700)


def sesion(page, semilla):
    rng = random.Random(semilla)
    page.goto((HERE / PAGE).as_uri())
    page.wait_for_function("typeof map!=='undefined' && map && typeof records!=='undefined'", timeout=60000)
    page.wait_for_timeout(1900)
    page.locator('#map').scroll_into_view_if_needed()
    page.wait_for_timeout(500)
    box = page.locator('#map').bounding_box()
    pasos = []
    for i in range(30):
        accion(page, box, pasos, rng)
        d = page.evaluate(PROBE)
        if d['nacional'] and d['mun'] == 'visible':
            print('  !! INCOHERENCIA tras:', ' -> '.join(pasos[-6:]))
            print('     ', json.dumps(d, ensure_ascii=False))
            return pasos, d
    return None, None


with sync_playwright() as p:
    br = p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', headless=True)
    page = br.new_page(viewport={'width': 1600, 'height': 1400})
    errores = []
    page.on('pageerror', lambda e: errores.append(str(e)))
    hallados = 0
    for semilla in range(6):
        print('== sesión', semilla)
        pasos, d = sesion(page, semilla)
        if d:
            hallados += 1
    print('sesiones con incoherencia:', hallados)
    print('errores JS:', errores[:5])
    br.close()
