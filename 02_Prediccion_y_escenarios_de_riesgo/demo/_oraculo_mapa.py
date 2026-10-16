"""Temporal: mide si el mapa final parece nacional (32 estados) o municipal (miles de polígonos)."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
import scipy.ndimage as nd
import json
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / '.task_packages'))
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
TAG = PAGE.replace('.html', '')
HIDE = "body :not(#map):not(#map *) { visibility: hidden !important; }"


def regiones(path):
    a = np.array(Image.open(path).convert('RGB'))
    a = (a // 24 * 24)  # cuantiza colores
    lab, n = nd.label(np.ones(a.shape[:2], bool))
    # etiqueta por color: agrupa píxeles vecinos del mismo color cuantizado
    uniq = {}
    key = a[:, :, 0].astype(np.int64) * 65536 + a[:, :, 1].astype(np.int64) * 256 + a[:, :, 2]
    total = 0
    for c in np.unique(key):
        m = key == c
        if m.sum() < 40:
            continue
        l, k = nd.label(m)
        total += int(k)
    return total


def probe(page):
    return page.evaluate("""
    (() => {
      const vis = n => { const p = map.getPane(n); return p ? getComputedStyle(p).visibility : 'missing'; };
      const b = map.getBounds();
      return {ext:(b.getNorth()-b.getSouth()).toFixed(1), zoom:map.getZoom(), state:$('state').value,
              mun:vis('municipal-geography'), edo:vis('state-geography'),
              activo:(typeof demo5EstadoActivo==='undefined'?null:demo5EstadoActivo),
              hist:geographyHistory.length};
    })()""")


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', headless=True)
    page = browser.new_page(viewport={'width': 1600, 'height': 1400})
    page.on('pageerror', lambda e: print('PAGEERROR:', e))
    page.goto((HERE / PAGE).as_uri())
    page.wait_for_function("typeof map!=='undefined' && map && typeof records!=='undefined'", timeout=60000)
    page.wait_for_timeout(1800)
    page.add_style_tag(content=HIDE)
    page.wait_for_timeout(400)
    page.locator('#map').screenshot(path=str(HERE / ('_oraculo_nacional_%s.png' % TAG)))
    print('referencia nacional:', probe(page), 'regiones =', regiones(str(HERE / ('_oraculo_nacional_%s.png' % TAG))))

    # vista de estado
    box = page.locator('#map').bounding_box()
    pt = page.evaluate("""(()=>{const p=stateLayer.getLayers().find(l=>l.feature.properties.state==='08');
        const c=map.latLngToContainerPoint(p.getBounds().getCenter()); return {x:c.x,y:c.y};})()""")
    page.mouse.click(box['x'] + pt['x'], box['y'] + pt['y'])
    page.wait_for_timeout(1200)
    page.locator('#map').screenshot(path=str(HERE / ('_oraculo_estado_%s.png' % TAG)))
    print('referencia estado  :', probe(page), 'regiones =', regiones(str(HERE / ('_oraculo_estado_%s.png' % TAG))))

    # secuencia del usuario
    mun = page.evaluate("""(()=>{const bb=l=>{const x=l.getBounds();return (x.getNorth()-x.getSouth())*(x.getEast()-x.getWest());};
        const c=layer.getLayers().filter(l=>String(l.feature.properties.key).slice(0,2)==='08')
          .map(l=>({key:String(l.feature.properties.key),area:bb(l)})).sort((a,b)=>b.area-a.area);
        const p=layer.getLayers().find(l=>l.feature.properties.key===c[0].key);
        const pt=map.latLngToContainerPoint(p.getBounds().getCenter()); return {x:pt.x,y:pt.y,key:c[0].key};})()""")
    page.mouse.click(box['x'] + mun['x'], box['y'] + mun['y'])
    page.wait_for_timeout(1200)
    for i in (1, 2, 3):
        page.mouse.click(box['x'] + mun['x'], box['y'] + mun['y'], button='right')
        page.wait_for_timeout(1400)
        f = str(HERE / ('_oraculo_derecho%d_%s.png' % (i, TAG)))
        page.locator('#map').screenshot(path=f)
        print('derecho %d          :' % i, probe(page), 'regiones =', regiones(f))
    browser.close()
