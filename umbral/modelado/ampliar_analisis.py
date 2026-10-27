"""Añade evaluación posterior congelada y variantes sin cambiar alpha/selección."""
import json
import csv
from pathlib import Path
import ejecutar as original
from ampliacion import classification_metrics, size_bin, exclusion_reasons
from core import make_features
import numpy as np

OUT = original.OUT
data = json.loads((OUT / 'resultados.json').read_text(encoding='utf-8'))

additional = {
    'version': 'analisis_posterior_2026_10_06',
    'warning': (
        'Métricas añadidas después de conocer MAE; no nueva evaluación independiente '
        'ni ajuste de alpha. Alpha y blend_weight ya elegidos en ejecutar.py.'
    ),
    'cuts': {},
    'error_by_size': {},
    'weight_definition': (
        'SV+NV del objetivo histórico para MAE ponderado; '
        'tamaño usa SV+NV del último antecedente disponible.'
    ),
}

# ---------------------------------------------------------------------------
# Bug #1 corregido: fit() ahora retorna 4 valores (model, training, alpha, blend)
# ---------------------------------------------------------------------------
for year in [2021, 2024]:
    model, train, _, best_blend = original.fit(year)
    test = original.examples(year)
    threshold = float(np.quantile([r['y'] for r in train], 2 / 3))
    local_preds = {
        'persistencia': [r['feature']['baseline'] for r in test],
        'ridge': original.predict(model, test),
        'blend': original.blend_predict(model, test, best_blend),
    }
    methods = {}
    for method, values in local_preds.items():
        m = classification_metrics([r['y'] for r in test], values, threshold)
        true_tercio = float(np.quantile([r['y'] for r in test], 2 / 3))
        red = [i for i, v in enumerate(values) if v >= threshold]
        m['precision_rojo_vs_tercio_observado_test'] = (
            sum(test[i]['y'] >= true_tercio for i in red) / len(red) if red else None
        )
        m['umbral_tercio_observado_test_solo_evaluacion'] = true_tercio
        methods[method] = m
        bins: dict = {}
        for r, p in zip(test, values):
            latest = next(
                h for h in original.histories[r['key']]
                if h['ano'] == r['feature']['source_year']
            )
            bins.setdefault(size_bin(latest['sv'] + latest['nv']), []).append(abs(r['y'] - p))
        additional['error_by_size'][f'{year}_{method}'] = {
            name: {
                'n': len(errors),
                'mae': float(np.mean(errors)),
                'p90_abs_error_pp': float(np.quantile(errors, .9)),
            }
            for name, errors in bins.items()
        }
    additional['cuts'][str(year)] = methods

# ---------------------------------------------------------------------------
# Variantes de NS limit — también con desempaquetado correcto de 4 valores
# ---------------------------------------------------------------------------
variant_values = {r['key']: {} for r in data['municipios']}
for limit in [5, 10, 20]:
    model, _, alpha_v, blend_v = original.fit(2027, limit)
    for key, h in original.histories.items():
        feat = make_features(h, 2027, limit)
        variant_values[key][f'persistencia_{limit}'] = feat['baseline'] if feat else None
        variant_values[key][f'ridge_{limit}'] = (
            original.predict(model, [{'feature': feat}])[0] if feat else None
        )
        variant_values[key][f'blend_{limit}'] = (
            original.blend_predict(model, [{'feature': feat}], blend_v)[0] if feat else None
        )

# ---------------------------------------------------------------------------
# Enriquecer municipios con métricas adicionales
# ---------------------------------------------------------------------------
for r in data['municipios']:
    h = original.histories[r['key']]
    latest = h[-1]
    r['observed'] = latest['sv'] + latest['nv']
    r['latest_sv'] = latest['sv']
    r['latest_nv'] = latest['nv']
    r['variants'] = variant_values[r['key']]
    r['exclusion_reasons'] = exclusion_reasons(h, 2027, 10) if r['risk'] is None else []
    if r['risk'] is None and not r['exclusion_reasons']:
        r['exclusion_reasons'] = ['Características agregadas inválidas o sin denominador etario válido']
    r['profile'] = {
        'young_pct': 100 * latest['ln_18_29'] / latest['ln'] if latest['ln'] else None,
        'older_pct': (
            100 * max(0, latest['ln_60_mas'] - latest['ln_edad_mayor_120'])
            / max(1, latest['ln'] - latest['ln_edad_mayor_120'])
        ),
        'urban_pct': 100 * latest['ln_urbana'] / latest['ln'] if latest['ln'] else None,
        'size_bin': size_bin(r['observed']),
    }

data['metadata']['additional_evaluation'] = additional
data['metadata']['scenario_definition'] = (
    'Base observable SV+NV 2024 para alcance máximo, reducción y ponderación; '
    'NS fuera del escenario. No población proyectada 2027; respuesta hipotética.'
)
# Actualizado: ya no dice "alpha10" porque el alpha se elige con CV temporal
data['metadata']['variant_definition'] = (
    'Tres métodos (persistencia, ridge, blend) × NS máximo 5/10/20, alpha y blend_weight '
    'elegidos con CV temporal. Frecuencia topN descriptiva, no probabilidad; '
    'no elegible cuenta como no seleccionado e informa cobertura de variantes.'
)
data['metadata']['weight_definition'] = additional['weight_definition']

(OUT / 'evaluacion_adicional.json').write_text(
    json.dumps(additional, ensure_ascii=False, allow_nan=False, indent=2),
    encoding='utf-8'
)
(OUT / 'resultados.json').write_text(
    json.dumps(data, ensure_ascii=False, allow_nan=False, separators=(',', ':')),
    encoding='utf-8'
)
(OUT / 'metricas.json').write_text(
    json.dumps(data['metadata'], ensure_ascii=False, allow_nan=False, indent=2),
    encoding='utf-8'
)

# Bug #15 corregido: el CSV ahora incluye 'blend' y 'method' para que los
# consumidores sepan qué columna es la estimación seleccionada
with (OUT / 'proyeccion_exploratoria_2027.csv').open('w', encoding='utf-8-sig', newline='') as f:
    fields = [
        'key', 'state', 'state_name', 'name', 'ln', 'observed',
        'risk', 'baseline', 'ridge', 'blend', 'method',
        'level', 'latest_ns', 'stable_catalog_state', 'exclusion_reasons',
    ]
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for r in data['municipios']:
        w.writerow({
            k: '; '.join(r[k]) if k == 'exclusion_reasons' else r[k]
            for k in fields
        })

print(json.dumps(additional['cuts'], ensure_ascii=True, indent=2))
