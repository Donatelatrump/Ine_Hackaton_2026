"""Temporal: traza el recorrido exacto del usuario (estado -> municipio -> clic derecho xN) paso a paso."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / '.task_packages'))
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
PAGINA = sys.argv[1] if len(sys.argv) > 1 else 'demo5.html'

PROBE = """
(() => {
 const vis = n => { const p = map.getPane(n); return p ? getComputedStyle(p).visibility : 'missing'; };
 const b = map.getBounds(); const ext = b.getNorth()-b.getSouth();
 return {ext:+ext.toFixed(1), nacional: ext>18, estado:$('state').value,
   activo:(typeof demo5EstadoActivo==='undefined'?null:demo5EstadoActivo),
   mun:vis('municipal-geography'), edo:vis('state-geography'),
   hist:geographyHistory.length, focus:(typeof geographyFocusKey==='undefined'?null:geographyFocusKey),
   panel:(()=>{const e=document.getElementById('state-plan-panel'); return e? !e.hidden : null;})(),
   detalle:document.getElementById('detail-name').textContent};
})()
"""


def muestra(page, etiqueta, errores):
    d = page.evaluate(PROBE)
    coherente = (not d['nacional']) or (d['mun'] == 'hidden' and d['edo'] == 'visible')
    print(('  OK  ' if coherente else '  FALLA ') + etiqueta + ' ' + json.dumps(d, ensure_ascii=False))
    if errores:
        print('        errores JS:', errores[-2:])
    return coherente, d


with sync_playwright() as p:
    br = p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', headless=True)
    page = br.new_page(viewport={'width': 1600, 'height': 1400})
    errores = []
    page.on('pageerror', lambda e: errores.append(str(e)))
    page.goto((HERE / PAGINA).as_uri())
    page.wait_for_function("typeof map!=='undefined' && map && typeof records!=='undefined'", timeout=60000)
    page.wait_for_timeout(2100)
    page.locator('#map').scroll_into_view_if_needed()
    page.wait_for_timeout(500)
    box = page.locator('#map').bounding_box()
    # Instrumentar goBackGeography para saber qué entrada saca del historial en cada clic derecho.
    page.evaluate("""() => {
      window.__historial = [];
      window.__goBack = window.goBackGeography;
      window.goBackGeography = function(){
        const antes = JSON.parse(JSON.stringify(geographyHistory));
        const antesEstado = $('state').value, antesActivo = demo5EstadoActivo;
        const r = window.__goBack.apply(this, arguments);
        window.__historial.push({antes, antesEstado, antesActivo,
          despuesEstado: $('state').value, despuesActivo: demo5EstadoActivo,
          focus: geographyFocusKey, exts: (map.getBounds().getNorth()-map.getBounds().getSouth()).toFixed(1)});
        return r;
      };
    }""")
    fallos = 0
    ok, _ = muestra(page, 'inicio', errores)
    fallos += not ok

    st = page.evaluate("""(()=>{const p=stateLayer.getLayers().find(l=>l.feature.properties.state==='08');
        const c=map.latLngToContainerPoint(p.getBounds().getCenter()); return {x:c.x,y:c.y};})()""")
    page.mouse.click(box['x'] + st['x'], box['y'] + st['y'])
    page.wait_for_timeout(1400)
    ok, d = muestra(page, '1) clic izquierdo en estado 08', errores)
    fallos += not (ok and d['activo'] == '08' and d['mun'] == 'visible' and not d['nacional'])

    mun = page.evaluate("""(()=>{const bb=l=>{const x=l.getBounds();return (x.getNorth()-x.getSouth())*(x.getEast()-x.getWest());};
        const c=layer.getLayers().filter(l=>String(l.feature.properties.key).slice(0,2)==='08').map(l=>({key:String(l.feature.properties.key),area:bb(l)})).sort((a,b)=>b.area-a.area);
        const p=layer.getLayers().find(l=>l.feature.properties.key===c[0].key);
        const pt=map.latLngToContainerPoint(p.getBounds().getCenter()); return {x:pt.x,y:pt.y,key:c[0].key};})()""")
    page.mouse.click(box['x'] + mun['x'], box['y'] + mun['y'])
    page.wait_for_timeout(1400)
    ok, d = muestra(page, '2) clic izquierdo en municipio ' + mun['key'], errores)
    fallos += not (ok and d['ext'] < 3)

    for i in range(1, 5):
        page.mouse.click(box['x'] + mun['x'], box['y'] + mun['y'], button='right')
        page.wait_for_timeout(1400)
        ok, d = muestra(page, '%d) clic derecho' % (i + 2), errores)
        print('        historial:', json.dumps(page.evaluate('window.__historial').pop(), ensure_ascii=False))
        if i <= 2:
            fallos += not ok

    print('FALLOS:', fallos, '| errores JS:', errores)
    br.close()
