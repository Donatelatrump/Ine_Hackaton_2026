"""Genera un complemento insular local para demo5 sin sustituir el continente.

Fuente: servicios de entidades y municipios 2025 del INEGI, EPSG:4326,
generalización del servicio de 0.001 grados. Las descargas se conservan aquí.
Solo incorpora componentes separados que no tocan la geometría estatal actual;
no interpreta diferencias entre costas como territorio nuevo.
"""
import hashlib
import json
import unicodedata
from pathlib import Path

from shapely.geometry import shape, mapping
from shapely import make_valid

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / 'demo' / 'data'
SERVICE = 'https://lcidsig.inegi.org.mx/server/rest/services/Hosted/'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def normal(value):
    return ''.join(c for c in unicodedata.normalize('NFD', value.upper())
                   if c.isalnum() and not unicodedata.combining(c))


def polygons(geometry):
    if geometry.geom_type == 'Polygon':
        yield geometry
    elif hasattr(geometry, 'geoms'):
        for part in geometry.geoms:
            yield from polygons(part)


def main():
    states = json.loads((DATA / 'estados.js').read_text(encoding='utf-8')
                        .split('=', 1)[1].strip().rstrip(';'))
    base = {f['properties']['state']: shape(f['geometry']) for f in states['features']}
    municipalities = load(DATA / 'municipios.geojson')['features']
    by_name = {}
    for f in municipalities:
        p = f['properties']
        by_name.setdefault((p['key'][:2], normal(p['municipio_nombre'])), []).append(p['key'])
    source_states = load(ROOT / 'entidades_inegi_2025_insular.geojson')
    source_municipalities = load(ROOT / 'municipios_inegi_2025_insular.geojson')
    official = {}
    for f in source_municipalities['features']:
        p = f['properties']
        official.setdefault(p['cve_ent'], []).append((p, make_valid(shape(f['geometry']))))

    islands = []
    for f in source_states['features']:
        state = f['properties']['cve_ent']
        geometry = make_valid(shape(f['geometry']))
        for polygon in polygons(geometry):
            if polygon.intersects(base[state].buffer(0.003)):
                continue
            # La asignación usa la superficie de intersección con el municipio oficial,
            # seguida de nombre + entidad; no supone equivalencia de claves INE/INEGI.
            matches = [(polygon.intersection(g).area, p)
                       for p, g in official.get(state, []) if polygon.intersects(g)]
            area, owner = max(matches, key=lambda pair: pair[0]) if matches else (0, None)
            keys = by_name.get((state, normal(owner['nomgeo'])), []) if owner else []
            key = keys[0] if len(keys) == 1 and area / polygon.area > .95 else None
            properties = {'state': state, 'key': key,
                          'municipio_inegi': owner['cvegeo'] if owner else None,
                          'municipio_nombre': owner['nomgeo'] if owner else None}
            islands.append({'type': 'Feature', 'properties': properties,
                            'geometry': mapping(polygon)})

    unresolved = [f['properties'] for f in islands if not f['properties']['key']]
    assert not unresolved, f'Islas pendientes de vinculación: {unresolved}'
    collection = {'type': 'FeatureCollection', 'features': islands}
    payload = json.dumps(collection, ensure_ascii=False, separators=(',', ':'))
    runtime = """;
// Complemento insular INEGI 2025. Se integra antes de inicializar Leaflet.
(() => {
  const states = new Map(window.UMBRAL_STATES.features.map(f => [f.properties.state, f]));
  const municipalities = new Map(window.UMBRAL_GEO.features.map(f => [f.properties.key, f]));
  function append(feature, polygon) {
    if (!feature) return;
    const geometry = feature.geometry;
    if (geometry.type === 'Polygon') {
      feature.geometry = {type:'MultiPolygon', coordinates:[geometry.coordinates, polygon.coordinates]};
    } else {
      geometry.coordinates.push(polygon.coordinates);
    }
  }
  for (const island of window.UMBRAL_ISLANDS.features) {
    append(states.get(island.properties.state), island.geometry);
    append(municipalities.get(island.properties.key), island.geometry);
  }
})();
"""
    (DATA / 'islas.js').write_text('window.UMBRAL_ISLANDS=' + payload + runtime, encoding='utf-8')
    metadata = {
        'fecha': '2026-10-16',
        'fuentes': [SERVICE + name + '/FeatureServer/0' for name in
                    ('Entidades_federativas_2025', 'Municipios_2025')],
        'crs': 'EPSG:4326', 'generalizacion_grados': .001,
        'componentes_insulares_anadidos': len(islands),
        'municipios_vinculados': sorted({f['properties']['key'] for f in islands if f['properties']['key']}),
        'sin_correspondencia_municipal': unresolved,
        'alcance': 'Complemento visual; no modifica estimaciones ni el continente de la base.',
        'sha256_fuentes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                          (ROOT / 'entidades_inegi_2025_insular.geojson', ROOT / 'municipios_inegi_2025_insular.geojson')},
    }
    (DATA / 'islas_metadatos.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(metadata, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
