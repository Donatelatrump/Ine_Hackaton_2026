"""Temporal: comprueba con oraculo que las dos protecciones nuevas evitan la vista nacional con
divisiones municipales. Variantes: demo5.html (arreglado), _oraculo_prev.html (sin ninguna de las dos
protecciones), _oraculo_net.html y _oraculo_geo.html (con una sola)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / '.task_packages'))
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
PROBE = """
(() => {
 const vis = n => { const p = map.getPane(n); return p ? getComputedStyle(p).visibility : 'missing'; };
 const b = map.getBounds();
 return {ext:+(b.getNorth()-b.getSouth()).toFixed(1), estado:$('state').value,
   activo:(typeof demo5EstadoActivo==='undefined'?null:demo5EstadoActivo),
   mun:vis('municipal-geography'), edo:vis('state-geography')};
})()
"""


def escenario(page, pagina):
    """Estado del que parte el fallo: hay foco municipal y el nivel ya es nacional, pero las capas
    siguen en modo municipal. Luego el usuario da clic derecho."""
    page.goto((HERE / pagina).as_uri())
    page.wait_for_function("typeof map!=='undefined' && map && typeof records!=='undefined'", timeout=60000)
    page.wait_for_timeout(2100)
    page.locator('#map').scroll_into_view_if_needed()
    page.wait_for_timeout(500)
    box = page.locator('#map').bounding_box()
    st = page.evaluate("""(()=>{const p=stateLayer.getLayers().find(l=>l.feature.properties.state==='08');
        const c=map.latLngToContainerPoint(p.getBounds().getCenter()); return {x:c.x,y:c.y};})()""")
    page.mouse.click(box['x'] + st['x'], box['y'] + st['y'])
    page.wait_for_timeout(1300)
    mun = page.evaluate("""(()=>{const bb=l=>{const x=l.getBounds();return (x.getNorth()-x.getSouth())*(x.getEast()-x.getWest());};
        const c=layer.getLayers().filter(l=>String(l.feature.properties.key).slice(0,2)==='08').map(l=>({key:String(l.feature.properties.key),area:bb(l)})).sort((a,b)=>b.area-a.area);
        const p=layer.getLayers().find(l=>l.feature.properties.key===c[0].key);
        const pt=map.latLngToContainerPoint(p.getBounds().getCenter()); return {x:pt.x,y:pt.y,key:c[0].key};})()""")
    page.mouse.click(box['x'] + mun['x'], box['y'] + mun['y'])
    page.wait_for_timeout(1300)
    # El nivel vuelve a nacional sin que nadie sincronice las capas ni los paneles (el estado del fallo).
    page.evaluate("""() => {
      geographyHistory.length = 0;
      const s = document.getElementById('state'); s.value = '';
      document.getElementById('search').value = '';
    }""")
    antes = page.evaluate(PROBE)
    page.mouse.click(box['x'] + mun['x'], box['y'] + mun['y'], button='right')
    page.wait_for_timeout(1500)
    return antes, page.evaluate(PROBE), mun['key']


with sync_playwright() as p:
    br = p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', headless=True)
    casos = [
        ('demo5.html', True, 'arreglo completo'),
        ('_oraculo_prev.html', False, 'sin las dos protecciones (antes)'),
        ('_oraculo_net.html', True, 'solo la red de seguridad'),
        ('_oraculo_geo.html', True, 'solo el arreglo de la vuelta atras'),
    ]
    fallos = 0
    for pagina, debe_quedar_bien, etiqueta in casos:
        page = br.new_page(viewport={'width': 1600, 'height': 1400})
        errores = []
        page.on('pageerror', lambda e: errores.append(str(e)))
        antes, despues, clave = escenario(page, pagina)
        coherente = despues['ext'] > 18 and despues['mun'] == 'hidden' and despues['edo'] == 'visible'
        sintoma = despues['ext'] > 18 and despues['mun'] == 'visible'
        bien = (coherente == debe_quedar_bien) and (not (debe_quedar_bien is False and not sintoma))
        print(('  OK  ' if bien else '  FALLA ') + etiqueta + ' · ' + pagina)
        print('        antes   ', json.dumps(antes, ensure_ascii=False))
        print('        despues ', json.dumps(despues, ensure_ascii=False), '| sintoma:', sintoma, '| coherente:', coherente)
        if errores:
            print('        errores JS:', errores[:2])
        fallos += not bien
        page.close()
    print('FALLOS:', fallos)
    br.close()
