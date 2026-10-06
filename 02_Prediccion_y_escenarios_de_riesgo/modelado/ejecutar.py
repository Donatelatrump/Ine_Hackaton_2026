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
from core import FEATURE_NAMES, choose_model, make_features, metricas, missingness_bounds, valid_rate

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

def examples(target, ns_limit=10):
    output = []
    for key, h in sorted(histories.items()):
        feat = make_features(h, target, ns_limit)
        observed = next((r for r in h if r['ano'] == target), None)
        if feat is not None and observed and valid_rate(observed, ns_limit):
            assert feat['source_year'] < target and feat['same_year'] < target
            output.append(dict(key=key, year=target, feature=feat, y=observed['abstencion_pct'],
                weight=observed['sv'] + observed['nv'], state=observed['entidad_ine']))
    return output

# ---------------------------------------------------------------------------
# Búsqueda temporal de alpha (mejora #5 del análisis):
# Se prueban alphas candidatos en ventanas de entrenamiento anteriores al
# corte. Se elige el que minimiza el MAE promedio en validación temporal,
# NUNCA usando datos del año objetivo ni posterior.
# ---------------------------------------------------------------------------
ALPHA_CANDIDATES = [0.1, 1, 5, 10, 50, 100, 500]

def _cv_alpha(training_years, ns_limit=10):
    """Validación temporal cruzada: entrena en i años, evalúa en el i+1-ésimo."""
    if len(training_years) < 2:
        return 10  # fallback al valor anterior si no hay suficientes cortes
    alpha_errors = {a: [] for a in ALPHA_CANDIDATES}
    for fold_idx in range(1, len(training_years)):
        val_year = training_years[fold_idx]
        train_years = training_years[:fold_idx]
        fold_train = [r for y in train_years for r in examples(y, ns_limit)]
        fold_val = examples(val_year, ns_limit)
        if not fold_train or not fold_val:
            continue
        X_tr = np.asarray([r['feature']['x'] for r in fold_train])
        y_tr = np.asarray([r['y'] - r['feature']['baseline'] for r in fold_train])
        X_val = np.asarray([r['feature']['x'] for r in fold_val])
        y_val = np.asarray([r['y'] for r in fold_val])
        base_val = np.asarray([r['feature']['baseline'] for r in fold_val])
        for a in ALPHA_CANDIDATES:
            pipe = make_pipeline(StandardScaler(), Ridge(alpha=a))
            pipe.fit(X_tr, y_tr)
            pred = np.clip(base_val + pipe.predict(X_val), 0, 100)
            alpha_errors[a].append(float(np.mean(np.abs(pred - y_val))))
    # Elige el alpha con menor MAE promedio en los folds de validación temporal
    scored = {a: np.mean(errs) for a, errs in alpha_errors.items() if errs}
    if not scored:
        return 10
    best = min(scored, key=scored.__getitem__)
    print(f'  [alpha CV] scores: { {a: f"{v:.3f}" for a, v in sorted(scored.items())} } → alpha={best}', flush=True)
    return best

def fit(before, ns_limit=10):
    available_years = sorted(y for y in [2015, 2018, 2021, 2024] if y < before)
    training = [r for year in available_years for r in examples(year, ns_limit)]
    assert training and all(r['year'] < before for r in training)
    # Búsqueda temporal de alpha solo si hay al menos dos cortes disponibles
    best_alpha = _cv_alpha(available_years, ns_limit)
    model = make_pipeline(StandardScaler(), Ridge(alpha=best_alpha))
    model.fit(
        np.asarray([r['feature']['x'] for r in training]),
        np.asarray([r['y'] - r['feature']['baseline'] for r in training])
    )
    return model, training, best_alpha

def predict(model, records):
    result = (
        np.asarray([r['feature']['baseline'] for r in records])
        + model.predict(np.asarray([r['feature']['x'] for r in records]))
    )
    return np.clip(result, 0, 100).tolist()

def blend_predict(model, records, blend_weight=0.25):
    """Mezcla conservadora: (1-w)*Ridge + w*referencia.

    Reduce el sesgo de subestimación cuando Ridge corrige demasiado.
    blend_weight=0 es Ridge puro; blend_weight=1 es referencia pura.
    El peso debe elegirse con datos ANTERIORES al objetivo, no después.
    """
    ridge_pred = np.asarray(predict(model, records))
    baseline = np.asarray([r['feature']['baseline'] for r in records])
    blended = (1 - blend_weight) * ridge_pred + blend_weight * baseline
    return np.clip(blended, 0, 100).tolist()

def metrics(records, pred, k=50):
    return metricas(
        [r['y'] for r in records], pred,
        [r['weight'] for r in records], [r['key'] for r in records], k
    )

def stable_catalog_states(target):
    states = sorted({r['entidad_ine'] for r in raw})
    years = sorted({r['ano'] for r in raw if r['ano'] <= target})
    return [s for s in states if all(
        {r['clave_municipio_ine'] for r in raw if r['ano'] == y and r['entidad_ine'] == s} ==
        {r['clave_municipio_ine'] for r in raw if r['ano'] == years[0] and r['entidad_ine'] == s}
        for y in years)]

def bootstrap_difference(records, pred):
    groups = defaultdict(list)
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
# Evaluación por corte temporal (blend comparativo incluido)
# ---------------------------------------------------------------------------
# blend_weight=0.25 se elige con criterio conservador sobre 2021; si en 2021
# la mezcla no mejora a Ridge, se documenta pero no se impone.
BLEND_WEIGHT = 0.25

checks = {}
predictions = []
state_metrics = []
alpha_log = {}

for target in [2021, 2024]:
    model, training, best_alpha = fit(target)
    test = examples(target)
    pred = predict(model, test)
    pred_blend = blend_predict(model, test, BLEND_WEIGHT)
    base = [r['feature']['baseline'] for r in test]
    checks[str(target)] = {
        'entrenamiento_anos': sorted({r['year'] for r in training}),
        'n_train': len(training),
        'alpha_elegido': best_alpha,
        'persistencia': metrics(test, base),
        'ridge': metrics(test, pred),
        'blend_conservador': metrics(test, pred_blend),
        'bootstrap': bootstrap_difference(test, pred),
    }
    alpha_log[str(target)] = best_alpha
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
            'ano': target, 'clave_municipio_ine': r['key'], 'entidad_ine': r['state'],
            'observado': r['y'], 'persistencia': b, 'ridge': p, 'blend': pb,
            'ultimo_ano_predictor': r['feature']['source_year'],
            'ano_mismo_tipo': r['feature']['same_year'], 'peso_observado': r['weight'],
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
        f'{target}: n={len(test)}, alpha={best_alpha}, '
        f'MAE base={m_base["mae"]:.3f} (sesgo={m_base["sesgo"]:+.2f}), '
        f'Ridge={m_ridge["mae"]:.3f} (sesgo={m_ridge["sesgo"]:+.2f}), '
        f'Blend={m_blend["mae"]:.3f} (sesgo={m_blend["sesgo"]:+.2f})',
        flush=True
    )

# Selección del modelo base: Ridge vs persistencia evaluado en 2021
selected = choose_model(checks['2021']['persistencia'], checks['2021']['ridge'])
# Selección del método final: si el blend mejora a Ridge en 2021, usar blend
blend_vs_ridge_2021 = choose_model(checks['2021']['ridge'], checks['2021']['blend_conservador'])
# blend_conservador se acepta si supera a Ridge con la misma regla de selección
selected_final = 'blend' if selected == 'ridge' and blend_vs_ridge_2021 == 'ridge' else selected

errors = [abs(r['observado'] - r[selected_final if selected_final != 'blend' else 'ridge'])
          for r in predictions if r['ano'] == 2021]
error90 = float(np.quantile(errors, .9))

sensitivities = []
for limit in [5, 10, 20]:
    model_s, _, alpha_s = fit(2021, limit)
    test_s = examples(2021, limit)
    sensitivities.append({
        'ns_max_pct': limit, 'alpha': alpha_s,
        'persistencia': metrics(test_s, [r['feature']['baseline'] for r in test_s]),
        'ridge': metrics(test_s, predict(model_s, test_s)),
    })

# Modelo final para proyección 2027
final_model, final_training, final_alpha = fit(2027)
final_stable_states = set(stable_catalog_states(2024))
rows = []
for key, h in sorted(histories.items()):
    latest = h[-1]
    feat = make_features(h, 2027)
    estimate = None
    baseline = None
    ridge = None
    blend = None
    contributions = []
    if feat:
        baseline = feat['baseline']
        ridge = predict(final_model, [{'feature': feat}])[0]
        blend = blend_predict(final_model, [{'feature': feat}], BLEND_WEIGHT)[0]
        # El método final puede ser ridge, blend o persistencia
        if selected_final == 'blend':
            estimate = blend
        elif selected_final == 'ridge':
            estimate = ridge
        else:
            estimate = baseline
        scaler, regressor = final_model.steps[0][1], final_model.steps[1][1]
        contributions = sorted(
            zip(FEATURE_NAMES, (scaler.transform([feat['x']])[0] * regressor.coef_).tolist()),
            key=lambda pair: -abs(pair[1])
        )[:3]
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
        'ln': latest['ln'], 'risk': estimate, 'baseline': baseline, 'ridge': ridge,
        'blend': blend, 'method': selected_final,
        'range_low': max(0, estimate - error90) if estimate is not None else None,
        'range_high': min(100, estimate + error90) if estimate is not None else None,
        'latest_ns': latest['no_especificados_pct'], 'latest_ns_low': ns_bounds[0],
        'latest_ns_high': ns_bounds[1], 'stable_catalog_state': state_stable,
        'flags': flags,
        'contributions': contributions if selected_final in ('ridge', 'blend') else [],
        'history': [
            {'year': r['ano'], 'risk': r['abstencion_pct'], 'ns': r['no_especificados_pct'], 'ln': r['ln']}
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
    'alpha_por_corte': alpha_log,
    'blend_weight': BLEND_WEIGHT,
    'selection_rule': '2021: MAE al menos 1% menor, MAE ponderado y precisión top50 no peores.',
    'selection_caveat': (
        '2021 se usa para seleccionar; no es una evaluación independiente posterior a selección. '
        '2024 es comprobación adicional presidencial, no valida 2027. '
        'Blend evaluado con misma regla antes de ver 2024.'
    ),
    'feature_names': FEATURE_NAMES,
    'ns_limit_pct': 10,
    'checks': checks,
    'sensitivities': sensitivities,
    'risk_thresholds': {
        'low': low, 'high': high,
        'definition': 'Tercios relativos de estimaciones válidas; no probabilidades de caer en abstención.',
    },
    'historical_error_p90_pp': error90,
    'range_definition': (
        'Estimación ± percentil 90 del error absoluto retrospectivo 2021. '
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
    ],
    'coefficients_standardized': [
        {'feature': n, 'coefficient': float(c)}
        for n, c in zip(FEATURE_NAMES, final_model.steps[1][1].coef_)
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
save_csv('proyeccion_exploratoria_2027.csv', [
    {k: v for k, v in r.items() if k not in ['history', 'flags', 'contributions']}
    for r in rows
])
print(
    f'Seleccion: {selected_final} (alpha={final_alpha}). '
    f'Estimables: {len(valid)}/{len(rows)}. Rango historico ±{error90:.2f} pp.',
    flush=True
)
