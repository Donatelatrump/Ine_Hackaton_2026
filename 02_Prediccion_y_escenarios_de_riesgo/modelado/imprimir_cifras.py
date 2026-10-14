"""Comando único para reimprimir cifras citadas, sin reentrenamiento.

Requiere haber ejecutado primero:
  1. ejecutar.py         → genera salidas/resultados.json
  2. ampliar_analisis.py → añade el campo 'variants' y 'observed' a cada municipio

Si falta alguno de esos pasos, el script lo indica explícitamente.
"""
import json
import sys
from pathlib import Path

_salidas = Path(__file__).resolve().parent / 'salidas'
_resultados_path = _salidas / 'resultados.json'

# ---------------------------------------------------------------------------
# Bug #3 corregido: guardia explícita antes de acceder a 'variants' y 'observed'
# ---------------------------------------------------------------------------
if not _resultados_path.exists():
    print('ERROR: ejecuta primero ejecutar.py para generar salidas/resultados.json', file=sys.stderr)
    sys.exit(1)

d = json.loads(_resultados_path.read_text(encoding='utf-8'))
m = d['metadata']

# Verificar que ampliar_analisis.py ya se ejecutó (añade 'variants' y 'observed')
_sample = d['municipios'][0] if d['municipios'] else {}
if 'variants' not in _sample or 'observed' not in _sample:
    print(
        'ERROR: el campo "variants"/"observed" no existe en resultados.json.\n'
        'Ejecuta ampliar_analisis.py antes de correr este script.',
        file=sys.stderr,
    )
    sys.exit(1)

pool = [r for r in d['municipios'] if r['stable_catalog_state']]
selected = sorted(
    (r for r in pool if r['risk'] is not None),
    key=lambda r: (-r['risk'], r['key'])
)[:50]

# Leer las variantes disponibles directamente del JSON (fix bug #16: no hardcodeado)
_variant_keys = sorted(
    {k for r in pool for k in r.get('variants', {}).keys()
     if r['variants'][k] is not None},
)
counts = {r['key']: 0 for r in pool}
for v in _variant_keys:
    for r in sorted(
        (r for r in pool if r.get('variants', {}).get(v) is not None),
        key=lambda r: (-r['variants'][v], r['key'])
    )[:50]:
        counts[r['key']] += 1

pop = sum(r['observed'] for r in selected)
before = sum(r['risk'] * r['observed'] for r in selected) / pop
add = sum(min(1000, r['observed']) * r['risk'] / 100 * .05 for r in selected)

print(json.dumps(
    {
        'equipo': 'aguas.exe',
        'cortes_originales': m['checks'],
        'cobertura': {k: m[k] for k in ['n_municipios', 'n_estimables', 'n_sin_estimacion']},
        'analisis_posterior': m.get('additional_evaluation'),
        'configuracion_inicial': {
            'metodo': m.get('selected_model', 'ridge'),
            'criterio': 'tasa',
            'catalogo_constante': True,
            'N': 50,
            'alcance': 1000,
            'respuesta_pct': 5,
            'estimables': sum(r['risk'] is not None for r in pool),
            'variantes_disponibles': _variant_keys,
            'nucleo_robusto': sum(counts[r['key']] == len(_variant_keys) for r in selected),
            'seleccionados': len(selected),
            'observados_referencia': pop,
            'alcance_limitado': sum(min(1000, r['observed']) for r in selected),
            'adicional_hipotetica': add,
            'tasa_base': before,
            'tasa_escenario': before - 100 * add / pop,
        },
        'advertencia': 'Frecuencia no es probabilidad; escenario hipotetico, NS fuera.',
    },
    ensure_ascii=True, allow_nan=False, indent=2,
))
