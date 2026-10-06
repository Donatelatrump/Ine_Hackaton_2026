"""Comprueba integridad del contrato entre modelo y demo."""
import json, math, hashlib
from pathlib import Path
TRACK=Path(__file__).resolve().parent.parent
r=json.loads((TRACK/'modelado/salidas/resultados.json').read_text(encoding='utf-8'))
rows=r['municipios'];keys=[m['key'] for m in rows]
assert len(keys)==len(set(keys))==2477
assert sum(m['risk'] is not None for m in rows)==1783
assert all(m['risk'] is None or 0<=m['risk']<=100 for m in rows)
assert all(m['risk'] is None or 0<=m['range_low']<=m['risk']<=m['range_high']<=100 for m in rows)
assert all(max(h['year'] for h in m['history'])==2024 for m in rows)
def finite(x):
    if isinstance(x,dict):return all(finite(v) for v in x.values())
    if isinstance(x,list):return all(finite(v) for v in x)
    return not isinstance(x,float) or math.isfinite(x)
assert finite(r)
geo=json.loads((TRACK/'demo/data/municipios.geojson').read_text(encoding='utf-8'))
assert {f['properties']['key'] for f in geo['features']}==set(keys)
assert len(geo['features'])==2477
assert (TRACK/'demo/data/resultados.json').read_bytes()==(TRACK/'modelado/salidas/resultados.json').read_bytes()
assert hashlib.sha256((TRACK/'datos_preparados/municipios_historico_con_calidad.csv').read_bytes()).hexdigest()==r['metadata']['input_sha256']
print('Integridad correcta: claves, cobertura, rangos, valores finitos, geometría, copia demo y SHA256')
