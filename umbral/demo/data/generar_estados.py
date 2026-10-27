"""Genera una capa estatal de referencia visual a partir de municipios.

Requiere Shapely. El cierre de 0.003 grados une pequeños huecos causados
por la simplificación municipal; no sirve para cálculos territoriales.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / '.task_geometry'))
from shapely.geometry import shape, mapping
from shapely import make_valid, union_all

folder = Path(__file__).resolve().parent
municipios = json.loads((folder / 'municipios.geojson').read_text(encoding='utf-8'))
groups = {}
for feature in municipios['features']:
    state = feature['properties']['key'][:2]
    groups.setdefault(state, []).append(make_valid(shape(feature['geometry'])))
features = []
for state, geometries in sorted(groups.items()):
    geometry = union_all([g.buffer(0.003) for g in geometries]).buffer(-0.003)
    geometry = make_valid(geometry.simplify(0.006, preserve_topology=True))
    features.append({'type': 'Feature', 'properties': {'state': state},
                     'geometry': mapping(geometry)})
collection = {'type': 'FeatureCollection', 'features': features}
payload = json.dumps(collection, ensure_ascii=False, separators=(',', ':'))
(folder / 'estados.js').write_text('window.UMBRAL_STATES=' + payload + ';\n', encoding='utf-8')
print(f'Capa de referencia generada: {len(features)} entidades, {len(payload)} caracteres')
