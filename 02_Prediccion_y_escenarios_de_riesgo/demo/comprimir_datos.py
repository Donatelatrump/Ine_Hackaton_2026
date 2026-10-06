"""Redondea los floats de data/datos_embebidos.js para reducir el peso de parseo.

Las coordenadas GeoJSON traen ~9 decimales (~0.1 mm) y las tasas 10+ decimales;
la demo muestra 2 decimales. Redondear coordenadas a 5 decimales y el resto a 4
no cambia nada visible y acorta el JSON que el navegador parsea en cada carga.
Uso: python comprimir_datos.py   (reescritura in situ, idempotente)
"""
import json
import re
from pathlib import Path

SRC = Path(__file__).resolve().parent / 'data' / 'datos_embebidos.js'
text = SRC.read_text(encoding='utf-8')

prefixes = ('window.UMBRAL_DATA=', 'window.UMBRAL_PERFIL=', 'window.UMBRAL_GEO=')


def round_floats(obj, decimals, depth_geo=False):
    """Recursivo: redondea floats; para GEO usa menos decimales en coordenadas."""
    if isinstance(obj, float):
        r = round(obj, decimals)
        return int(r) if r == int(r) and abs(r) < 1e15 else r
    if isinstance(obj, list):
        return [round_floats(v, decimals) for v in obj]
    if isinstance(obj, dict):
        return {k: round_floats(v, decimals) for k, v in obj.items()}
    return obj


out = []
pos = 0
while pos < len(text):
    matched = next((p for p in prefixes if text.startswith(p, pos)), None)
    if matched:
        start = pos + len(matched)
        depth = 0
        i = start
        while True:
            c = text[i]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        data = json.loads(text[start:i + 1])
        dec = 5 if matched == 'window.UMBRAL_GEO=' else 4
        compact = json.dumps(round_floats(data, dec), ensure_ascii=False,
                             separators=(',', ':'))
        out.append(text[pos:start])
        out.append(compact)
        out.append(';')
        pos = i + 1
        if text[pos:pos + 1] == ';':
            pos += 1
        continue
    nxt = len(text)
    for p in prefixes:
        j = text.find(p, pos)
        if j != -1:
            nxt = min(nxt, j)
    out.append(text[pos:nxt])
    pos = nxt

SRC.write_text(''.join(out), encoding='utf-8')
new_size = SRC.stat().st_size
print(f'listo: {len(text):,} -> {new_size:,} bytes ({100 * (1 - new_size / len(text)):.1f}% menos)')
