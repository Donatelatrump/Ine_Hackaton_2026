"""Ejecuta cortes temporales congelados, sensibilidad y proyección exploratoria 2027."""
import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent / '.task_packages'))
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from core import (FEATURE_NAMES, FEATURE_NAMES_PROY, choose_model, make_features,
                  make_features_proy, metricas, missingness_bounds, valid_rate)
from conapo_loader import get_conapo_ggrupos, get_conapo_quinq1

OUT = ROOT / 'modelado/salidas'
OUT.mkdir(exist_ok=True)
source = ROOT / 'datos_preparados/municipios_historico_con_calidad.csv'
with source.open(encoding='utf-8-sig', newline='') as f:
    raw = list(csv.DictReader(f))
numeric = ['ano', 'ln', 'sv', 'nv', 'ns', 'no_especificados_pct', 'abstencion_pct', 'ln_18_29',
           'ln_60_mas', 'ln_urbana', 'ln_rural', 'ln_edad_mayor_120']
histories = defaultdict(list)
for r in raw:
    for c in numeric:
        r[c] = float(r[c]) if r[c] != '' else None
    r['ano'] = int(r['ano'])
    histories[r['clave_municipio_ine']].append(r)
for h in histories.values():
    h.sort(key=lambda r: r['ano'])

# ---------------------------------------------------------------------------
# Caché de examples() — evita recalcular make_features() en cada fold del CV
# (bug #2 del análisis: sin caché _cv_temporal re-itera miles de municipios
#  por cada alpha candidate × fold)
# ---------------------------------------------------------------------------
_examples_cache: dict = {}

def examples(target, ns_limit=10):
    cache_key = (target, ns_limit)
    if cache_key in _examples_cache:
        return _examples_cache[cache_key]
    output = []
    for mun_key, h in sorted(histories.items()):
        feat = make_features(h, target, ns_limit)
        observed = next((r for r in h if r['ano'] == target), None)
        if feat is not None and observed and valid_rate(observed, ns_limit):
            assert feat['source_year'] < target and feat['same_year'] < target
            output.append(dict(
                key=mun_key, year=target, feature=feat,
                y=observed['abstencion_pct'],
                weight=observed['sv'] + observed['nv'],
                state=observed['entidad_ine'],
            ))
    _examples_cache[cache_key] = output
    return output

# ---------------------------------------------------------------------------
# stable_catalog_states — versión O(estados × años) en vez de O(n²)
# (bug #7: la versión anterior filtraba raw tres veces anidado por estado+año)
# ---------------------------------------------------------------------------
def stable_catalog_states(target):
    by_state_year: dict = defaultdict(set)
    for r in raw:
        if r['ano'] <= target:
            by_state_year[(r['entidad_ine'], r['ano'])].add(r['clave_municipio_ine'])
    states = sorted({r['entidad_ine'] for r in raw})
    years = sorted({ano for (_, ano) in by_state_year})
    if not years:
        return []
    base_year = years[0]
    return [
        s for s in states
        if all(by_state_year[(s, y)] == by_state_year[(s, base_year)] for y in years)
    ]

# ---------------------------------------------------------------------------
# Validación temporal conjunta: busca el mejor alpha Y blend_weight en folds
# temporales, usando el caché de examples() para evitar trabajo redundante.
# (mejora #5 + fix del bug #6: blend_weight ahora se optimiza, no está fijo)
#
# Retorna (best_alpha, best_blend_weight).
# NUNCA usa datos del año objetivo ni posteriores.
# ---------------------------------------------------------------------------
ALPHA_CANDIDATES = [0.1, 1, 5, 10, 50, 100, 500]
BLEND_CANDIDATES = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]

def _cv_temporal(training_years, ns_limit=10):
    """Validación temporal cruzada: elige alpha y blend_weight conjuntamente."""
    if len(training_years) < 2:
        return 10, 0.25  # fallback conservador sin datos suficientes

    # Construir folds una sola vez (examples() usa caché)
    folds = []
    for fold_idx in range(1, len(training_years)):
        val_year = training_years[fold_idx]
        train_years = training_years[:fold_idx]
        fold_train = [r for y in train_years for r in examples(y, ns_limit)]
        fold_val = examples(val_year, ns_limit)
        if fold_train and fold_val:
            folds.append((fold_train, fold_val))

    if not folds:
        return 10, 0.25

    # --- Paso 1: buscar mejor alpha ---
    # Guardamos las predicciones ridge por fold para reutilizarlas en paso 2
    alpha_fold_preds: dict = {a: [] for a in ALPHA_CANDIDATES}
    alpha_errors: dict = {a: [] for a in ALPHA_CANDIDATES}

    for fold_train, fold_val in folds:
        X_tr = np.asarray([r['feature']['x'] for r in fold_train])
        y_tr = np.asarray([r['y'] - r['feature']['baseline'] for r in fold_train])
        X_val = np.asarray([r['feature']['x'] for r in fold_val])
        y_val = np.asarray([r['y'] for r in fold_val])
        base_val = np.asarray([r['feature']['baseline'] for r in fold_val])
        # Pesos proporcionales al tamaño del fold para no sesgar hacia folds pequeños
        fold_weight = len(fold_val)
        for a in ALPHA_CANDIDATES:
            pipe = make_pipeline(StandardScaler(), Ridge(alpha=a))
            pipe.fit(X_tr, y_tr)
            ridge_pred = np.clip(base_val + pipe.predict(X_val), 0, 100)
            mae = float(np.mean(np.abs(ridge_pred - y_val)))
            alpha_errors[a].append((mae, fold_weight))
            alpha_fold_preds[a].append((ridge_pred, base_val, y_val))

    # MAE ponderado por tamaño de fold (fix bug #9: antes era promedio simple)
    scored_alpha = {
        a: sum(mae * w for mae, w in pairs) / sum(w for _, w in pairs)
        for a, pairs in alpha_errors.items() if pairs
    }
    best_alpha = min(scored_alpha, key=scored_alpha.__getitem__)

    # --- Paso 2: buscar mejor blend_weight con el alpha elegido ---
    blend_errors: dict = {w: [] for w in BLEND_CANDIDATES}
    for ridge_pred, base_val, y_val in alpha_fold_preds[best_alpha]:
        fold_weight = len(y_val)
        for w in BLEND_CANDIDATES:
            blended = np.clip((1 - w) * ridge_pred + w * base_val, 0, 100)
            mae = float(np.mean(np.abs(blended - y_val)))
            blend_errors[w].append((mae, fold_weight))

    scored_blend = {
        w: sum(mae * wt for mae, wt in pairs) / sum(wt for _, wt in pairs)
        for w, pairs in blend_errors.items() if pairs
    }
    best_blend = min(scored_blend, key=scored_blend.__getitem__)

    print(
        f'  [CV] alpha: { {a: f"{v:.3f}" for a, v in sorted(scored_alpha.items())} } -> {best_alpha}\n'
        f'  [CV] blend: { {w: f"{v:.3f}" for w, v in sorted(scored_blend.items())} } -> {best_blend}',
        flush=True
    )
    return best_alpha, best_blend

def fit(before, ns_limit=10):
    """Entrena el modelo final sobre todos los años disponibles antes de `before`.

    Retorna (model, training, best_alpha, best_blend_weight).
    """
    available_years = sorted(y for y in [2015, 2018, 2021, 2024] if y < before)
    training = [r for year in available_years for r in examples(year, ns_limit)]
    assert training and all(r['year'] < before for r in training)
    best_alpha, best_blend = _cv_temporal(available_years, ns_limit)
    model = make_pipeline(StandardScaler(), Ridge(alpha=best_alpha))
    model.fit(
        np.asarray([r['feature']['x'] for r in training]),
        np.asarray([r['y'] - r['feature']['baseline'] for r in training])
    )
    return model, training, best_alpha, best_blend

def predict(model, records):
    result = (
        np.asarray([r['feature']['baseline'] for r in records])
        + model.predict(np.asarray([r['feature']['x'] for r in records]))
    )
    return np.clip(result, 0, 100).tolist()

def blend_predict(model, records, blend_weight):
    """Mezcla conservadora: (1-w)*Ridge + w*referencia.

    Reduce el sesgo de subestimación cuando Ridge corrige demasiado.
    blend_weight=0 → Ridge puro; blend_weight=1 → referencia pura.
    El peso se elige con validación temporal, nunca mirando el año objetivo.
    """
    ridge_pred = np.asarray(predict(model, records))
    baseline = np.asarray([r['feature']['baseline'] for r in records])
    return np.clip((1 - blend_weight) * ridge_pred + blend_weight * baseline, 0, 100).tolist()

def metrics(records, pred, k=50):
    return metricas(
        [r['y'] for r in records], pred,
        [r['weight'] for r in records], [r['key'] for r in records], k
    )

def bootstrap_difference(records, pred):
    groups: dict = defaultdict(list)
    for r, p in zip(records, pred):
        groups[r['state']].append(abs(r['y'] - r['feature']['baseline']) - abs(r['y'] - p))
    states = sorted(groups)
    rng = np.random.default_rng(123)
    estimates = []
    for _ in range(500):
        draws = rng.choice(states, len(states), replace=True)
        total = sum(sum(groups[s]) for s in draws)
        n = sum(len(groups[s]) for s in draws)
        estimates.append(total / n)
    return {
        'mejora_mae_pp': float(np.mean([v for a in groups.values() for v in a])),
        'bootstrap_entidades_p025': float(np.quantile(estimates, .025)),
        'bootstrap_entidades_p975': float(np.quantile(estimates, .975)),
        'advertencia': 'Sensibilidad por conglomerados de entidad; no incorpora incertidumbre temporal de futuras elecciones.',
    }

# ---------------------------------------------------------------------------
# Evaluación por corte temporal
# ---------------------------------------------------------------------------
checks = {}
predictions = []
state_metrics = []
alpha_log = {}
blend_log = {}

for target in [2021, 2024]:
    model, training, best_alpha, best_blend = fit(target)
    test = examples(target)
    pred = predict(model, test)
    pred_blend = blend_predict(model, test, best_blend)
    base = [r['feature']['baseline'] for r in test]
    checks[str(target)] = {
        'entrenamiento_anos': sorted({r['year'] for r in training}),
        'n_train': len(training),
        'alpha_elegido': best_alpha,
        'blend_weight_elegido': best_blend,
        'persistencia': metrics(test, base),
        'ridge': metrics(test, pred),
        'blend_conservador': metrics(test, pred_blend),
        'bootstrap': bootstrap_difference(test, pred),
    }
    alpha_log[str(target)] = best_alpha
    blend_log[str(target)] = best_blend
    stable = stable_catalog_states(target)
    indexes = [i for i, r in enumerate(test) if r['state'] in stable]
    check_records = [test[i] for i in indexes]
    checks[str(target)]['catalogo_estable'] = {
        'entidades': stable, 'n': len(indexes),
        'persistencia': metrics(check_records, [base[i] for i in indexes]),
        'ridge': metrics(check_records, [pred[i] for i in indexes]),
        'nota': 'Estabilidad de catálogo es proxy; no acredita estabilidad de límites.',
    }
    for r, p, pb, b in zip(test, pred, pred_blend, base):
        predictions.append({
            'ano': target,
            'clave_municipio_ine': r['key'],
            'entidad_ine': r['state'],
            'observado': r['y'],
            'persistencia': b,
            'ridge': p,
            'blend': pb,
            'ultimo_ano_predictor': r['feature']['source_year'],
            'ano_mismo_tipo': r['feature']['same_year'],
            'peso_observado': r['weight'],
        })
    for state in sorted({r['state'] for r in test}):
        ix = [i for i, r in enumerate(test) if r['state'] == state]
        for name, values in [('persistencia', base), ('ridge', pred), ('blend', pred_blend)]:
            state_metrics.append({
                'ano': target, 'entidad_ine': state, 'metodo': name,
                **metrics([test[i] for i in ix], [values[i] for i in ix], min(10, len(ix))),
            })
    m_base = checks[str(target)]['persistencia']
    m_ridge = checks[str(target)]['ridge']
    m_blend = checks[str(target)]['blend_conservador']
    print(
        f'{target}: n={len(test)}, alpha={best_alpha}, blend_w={best_blend}, '
        f'MAE base={m_base["mae"]:.3f} (sesgo={m_base["sesgo"]:+.2f}), '
        f'Ridge={m_ridge["mae"]:.3f} (sesgo={m_ridge["sesgo"]:+.2f}), '
        f'Blend={m_blend["mae"]:.3f} (sesgo={m_blend["sesgo"]:+.2f})',
        flush=True
    )

# ---------------------------------------------------------------------------
# Selección del modelo final
# ---------------------------------------------------------------------------
# Paso 1: ¿Ridge supera a persistencia en 2021?
selected = choose_model(checks['2021']['persistencia'], checks['2021']['ridge'])
# Paso 2: ¿Blend supera a Ridge en 2021? (evaluado con misma regla, antes de ver 2024)
blend_vs_ridge_2021 = choose_model(checks['2021']['ridge'], checks['2021']['blend_conservador'])
selected_final = 'blend' if selected == 'ridge' and blend_vs_ridge_2021 == 'ridge' else selected

# ---------------------------------------------------------------------------
# error90: calculado sobre el método SELECCIONADO (fix bug #4)
# Antes se usaba siempre 'ridge' aunque selected_final fuera 'blend'
# ---------------------------------------------------------------------------
errors = [
    abs(r['observado'] - r[selected_final])
    for r in predictions if r['ano'] == 2021
]
error90 = float(np.quantile(errors, .9))

sensitivities = []
for limit in [5, 10, 20]:
    model_s, _, alpha_s, blend_s = fit(2021, limit)
    test_s = examples(2021, limit)
    sensitivities.append({
        'ns_max_pct': limit, 'alpha': alpha_s, 'blend_weight': blend_s,
        'persistencia': metrics(test_s, [r['feature']['baseline'] for r in test_s]),
        'ridge': metrics(test_s, predict(model_s, test_s)),
        'blend': metrics(test_s, blend_predict(model_s, test_s, blend_s)),
    })

# Modelo final para proyección 2027
final_model, final_training, final_alpha, final_blend = fit(2027)
final_stable_states = set(stable_catalog_states(2024))

# Cargar datos CONAPO para proyección demográfica 2027
conapo_ggrupos = get_conapo_ggrupos()
conapo_quinq1 = get_conapo_quinq1()

# Preparar dict de demografía proyectada por municipio para 2027
conapo_demog_2027 = {}
for clave, datos in conapo_ggrupos.items():
    if 2027 in datos and 2024 in datos:
        conapo_demog_2027[clave] = {2024: datos[2024], 2027: datos[2027]}

rows = []
for key, h in sorted(histories.items()):
    latest = h[-1]
    feat = make_features_proy(h, 2027, conapo_demog_2027)
    estimate = None
    baseline = None
    ridge = None
    blend = None
    contributions = []
    demo_proy = None
    if feat:
        baseline = feat['baseline']
        ridge = predict(final_model, [{'feature': feat}])[0]
        blend = blend_predict(final_model, [{'feature': feat}], final_blend)[0]
        if selected_final == 'blend':
            estimate = blend
        elif selected_final == 'ridge':
            estimate = ridge
        else:
            estimate = baseline
        scaler, regressor = final_model.steps[0][1], final_model.steps[1][1]
        # Usar FEATURE_NAMES + FEATURE_NAMES_PROY para contributions
        all_features = FEATURE_NAMES + FEATURE_NAMES_PROY
        contributions = sorted(
            zip(all_features, (scaler.transform([feat['x']])[0] * regressor.coef_).tolist()),
            key=lambda pair: -abs(pair[1])
        )[:3]
        demo_proy = feat.get('demo_proy')
    ns_bounds = missingness_bounds(latest['sv'], latest['nv'], latest['ns'])
    flags = []
    if not feat:
        flags.append('Antecedentes insuficientes o NS superior al umbral')
    if latest['nombres_historicos_distintos'] != '1':
        flags.append('Nombre histórico variable: revisar territorio')
    if latest['anos_disponibles'] != '6':
        flags.append('Historial incompleto')
    if float(latest['ln_edad_mayor_120']) > 0:
        flags.append('Edades extremas excluidas de proporción etaria')
    state_stable = latest['entidad_ine'] in final_stable_states
    if not state_stable:
        flags.append('Entidad con cambios de catálogo; límites no armonizados')
    rows.append({
        'key': key, 'state': latest['entidad_ine'], 'state_name': latest['entidad_nombre'],
        'name': latest['municipio_nombre_cartografia'] or latest['municipio_nombre'],
        'ln': latest['ln'], 'risk': estimate, 'baseline': baseline,
        'ridge': ridge, 'blend': blend, 'method': selected_final,
        'range_low': max(0, estimate - error90) if estimate is not None else None,
        'range_high': min(100, estimate + error90) if estimate is not None else None,
        'latest_ns': latest['no_especificados_pct'],
        'latest_ns_low': ns_bounds[0], 'latest_ns_high': ns_bounds[1],
        'stable_catalog_state': state_stable, 'flags': flags,
        'contributions': contributions if selected_final in ('ridge', 'blend') else [],
        'demo_proy': demo_proy,
        'history': [
            {'year': r['ano'], 'risk': r['abstencion_pct'],
             'ns': r['no_especificados_pct'], 'ln': r['ln']}
            for r in h
        ],
    })

valid = [r['risk'] for r in rows if r['risk'] is not None]
low, high = np.quantile(valid, [1 / 3, 2 / 3]).tolist()
for r in rows:
    r['level'] = (
        'sin_datos' if r['risk'] is None
        else ('alto' if r['risk'] >= high else 'bajo' if r['risk'] < low else 'medio')
    )

metadata = {
    'titulo': 'Atlas de decisión municipal', 'horizonte': 2027,
    'tipo_eleccion': 'intermedia', 'datos_hasta': 2024,
    'selected_model': selected_final,
    'alpha_final': final_alpha,
    'blend_weight_final': final_blend,
    'alpha_por_corte': alpha_log,
    'blend_weight_por_corte': blend_log,
    'selection_rule': (
        '2021: MAE al menos 1% menor, MAE ponderado y precisión top50 no peores, '
        'sesgo no degradado más de 3 pp respecto al baseline.'
    ),
    'selection_caveat': (
        '2021 se usa para seleccionar; no es evaluación independiente posterior a selección. '
        '2024 es comprobación adicional presidencial, no valida 2027. '
        'Alpha y blend_weight elegidos con CV temporal sobre 2021; '
        'blend_weight evaluado antes de ver resultados de 2024.'
    ),
    'feature_names': FEATURE_NAMES + FEATURE_NAMES_PROY,
    'ns_limit_pct': 10,
    'checks': checks,
    'sensitivities': sensitivities,
    'risk_thresholds': {
        'low': low, 'high': high,
        'definition': 'Tercios relativos de estimaciones válidas; no probabilidades.',
    },
    'historical_error_p90_pp': error90,
    'error90_method': selected_final,
    'range_definition': (
        f'Estimación ± percentil 90 del error absoluto de {selected_final} en 2021. '
        'Rango ilustrativo; no intervalo probabilístico calibrado para 2027.'
    ),
    'n_municipios': len(rows), 'n_estimables': len(valid),
    'n_sin_estimacion': len(rows) - len(valid),
    'train_final_years': sorted({r['year'] for r in final_training}),
    'territorial_definition': (
        'Claves INE, polígonos de referencia visual de mayo 2024. '
        'Límites históricos sin armonizar.'
    ),
    'scenario_definition': (
        'Participación adicional hipotética = alcance × abstención estimada/100 × respuesta supuesta/100. '
        'Alcance limitado por LN histórica 2024; no es una población proyectada a 2027.'
    ),
    'sources': [
        {'label': 'CCPC', 'url': 'https://ine.mx/transparencia/datos-abiertos/visualizacion-datos/conteos-censales-participacion/'},
        {'label': 'Cartografía INE', 'url': 'https://pautas.ine.mx/transparencia/mapas/index_2025.html'},
        {'label': 'CONAPO Proyecciones 2024-2027', 'url': 'https://www.gob.mx/conapo'},
    ],
    'coefficients_standardized': [
        {'feature': n, 'coefficient': float(c)}
        for n, c in zip(FEATURE_NAMES + FEATURE_NAMES_PROY, final_model.steps[1][1].coef_)
    ],
    'ridge_intercept': float(final_model.steps[1][1].intercept_),
    'input_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
}

assert len(rows) == 2477 and len({r['key'] for r in rows}) == len(rows)
assert all(r['risk'] is None or 0 <= r['risk'] <= 100 for r in rows)

(OUT / 'resultados.json').write_text(
    json.dumps({'metadata': metadata, 'municipios': rows},
               ensure_ascii=False, allow_nan=False, separators=(',', ':')),
    encoding='utf-8'
)
(OUT / 'metricas.json').write_text(
    json.dumps(metadata, ensure_ascii=False, allow_nan=False, indent=2),
    encoding='utf-8'
)

def save_csv(name, data):
    with (OUT / name).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(data[0]))
        w.writeheader()
        w.writerows(data)

save_csv('backtest_predicciones.csv', predictions)
save_csv('metricas_entidad.csv', state_metrics)
# El CSV de proyección incluye 'blend' y el campo 'method' para que los
# consumidores sepan qué columna es la estimación final (fix bug #18)
save_csv('proyeccion_exploratoria_2027.csv', [
    {k: v for k, v in r.items() if k not in ['history', 'flags', 'contributions']}
    for r in rows
])
print(
    f'Seleccion: {selected_final} (alpha={final_alpha}, blend_w={final_blend}). '
    f'Estimables: {len(valid)}/{len(rows)}. Rango historico ±{error90:.2f} pp.',
    flush=True
)
