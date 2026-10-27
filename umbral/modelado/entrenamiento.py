"""Aprendizaje del ajuste municipal a la referencia.

Cada decisión —espacio de trabajo, pesos, encogimiento jerárquico, familia del
modelo y blend— se elige con validación temporal sobre años ANTERIORES al corte
evaluado. Ninguna función de este módulo consulta el año objetivo: recibe
ejemplos ya construidos con datos previos.

Mejoras implementadas aquí:
  #2  blend dependiente del tamaño del municipio, no un peso global constante.
  #3  ajuste en espacio logit cuando la validación temporal lo prefiere, con
      salida acotada de forma natural (sin recortes en 0/100).
  #4  mínimos cuadrados ponderados por SV+NV del antecedente.
  #5  encogimiento jerárquico del antecedente hacia la media de su entidad.
  #6  validación temporal sobre todos los pliegues disponibles.
  #9  intervalos conformales por cuantiles del residual con signo.
  #10 alternativa de familia (histogram gradient boosting) elegida por CV.
"""
import math

from core import quantile

# ---------------------------------------------------------------------------
# Transformaciones de la tasa
# ---------------------------------------------------------------------------

def logit(rate_pp, eps=0.1):
    """Log-odds de una tasa en puntos porcentuales, saturada en los extremos."""
    q = min(max(float(rate_pp), eps), 100.0 - eps) / 100.0
    return math.log(q / (1.0 - q))


def logistic(value):
    """Inversa de logit, devuelve puntos porcentuales en (0, 100)."""
    value = float(value)
    if value >= 0:
        return 100.0 / (1.0 + math.exp(-value))
    z = math.exp(value)
    return 100.0 * z / (1.0 + z)


def clip_rate(value):
    return min(100.0, max(0.0, float(value)))


# ---------------------------------------------------------------------------
# Encogimiento jerárquico y blend por tamaño
# ---------------------------------------------------------------------------

# Rango de tamaño (SV+NV del antecedente) sobre el que se interpola el peso.
SIZE_FLOOR, SIZE_CEIL = 3000.0, 300000.0


def size_weight(size, w_small, w_large):
    """Peso (0..1) sobre la referencia, interpolado en el tamaño del municipio.

    Municipios chicos pesan hacia `w_small` y grandes hacia `w_large`, porque el
    error del modelo se concentra en los chicos.
    """
    if size is None or float(size) <= 0:
        return float(w_small)
    t = (math.log10(max(float(size), 1.0)) - math.log10(SIZE_FLOOR)) / (
        math.log10(SIZE_CEIL) - math.log10(SIZE_FLOOR)
    )
    t = min(1.0, max(0.0, t))
    return float(w_small) + (float(w_large) - float(w_small)) * t


def pooled_baseline(base, size, state_mean, k):
    """Encogimiento empírico-bayesiano del antecedente hacia su entidad.

    k es la fuerza de encogimiento en unidades de SV+NV: k=0 no encoge.
    """
    if k is None or k <= 0 or state_mean is None:
        return float(base)
    n = max(0.0, float(size or 0))
    return (n * float(base) + float(k) * float(state_mean)) / (n + float(k))


def state_year_means(rows):
    """Media de abstención por (entidad, año), ponderada por SV+NV observados.

    Se calcula sobre TODAS las filas con participación observable, no solo las
    elegibles para un corte, para no condicionar la media al objetivo.
    """
    acc = {}
    for row in rows:
        rate = row.get('abstencion_pct')
        if rate is None or not math.isfinite(float(rate)):
            continue
        weight = float(row.get('sv') or 0) + float(row.get('nv') or 0)
        if weight <= 0:
            continue
        key = (row.get('entidad_ine'), int(row['ano']))
        total, peso = acc.get(key, (0.0, 0.0))
        acc[key] = (total + float(rate) * weight, peso + weight)
    return {key: total / peso for key, (total, peso) in acc.items() if peso > 0}


def record_size(record):
    """Tamaño del municipio en el antecedente (SV+NV), con respaldo en la feature."""
    size = record.get('weight_source')
    if size is None:
        size = record.get('feature', {}).get('source_size')
    return float(size or 0.0)


# ---------------------------------------------------------------------------
# Aprendiz
# ---------------------------------------------------------------------------

def build_learner(family, alpha):
    if family == 'hgb':
        from sklearn.ensemble import HistGradientBoostingRegressor
        return HistGradientBoostingRegressor(
            max_iter=150, learning_rate=0.06, max_leaf_nodes=15,
            l2_regularization=1.0, min_samples_leaf=20, random_state=0,
        )
    from sklearn.linear_model import Ridge
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    return make_pipeline(StandardScaler(), Ridge(alpha=alpha))


DEFAULT_CONFIG = {
    'k': 0, 'family': 'ridge', 'alpha': 500, 'space': 'pp',
    'weighted': False, 'w_small': 0.5, 'w_large': 0.5,
}


class Modelo:
    """Ajuste aprendido sobre la referencia, con pooling y blend configurables.

    La referencia encogida (`base`) se recalcula en inferencia a partir del
    registro, de modo que el mismo objeto sirve para cualquier corte.
    """

    def __init__(self, config, state_means, learner=None):
        self.config = dict(config)
        self.state_means = state_means or {}
        self.learner = learner

    def base(self, record):
        feature = record['feature']
        mean = self.state_means.get((record.get('state'), feature['source_year']))
        return pooled_baseline(
            feature['baseline'], record_size(record), mean, self.config.get('k', 0)
        )

    def reference(self, records):
        return [self.base(r) for r in records]

    def learner_only(self, records):
        base = self.reference(records)
        if self.learner is None or not records:
            return base
        raw = self.learner.predict([r['feature']['x'] for r in records])
        if self.config.get('space') == 'logit':
            return [logistic(logit(b) + float(d)) for b, d in zip(base, raw)]
        return [clip_rate(b + float(d)) for b, d in zip(base, raw)]

    def predict(self, records, blend=None):
        return blend_predictions(self, records, blend)


def fit_config(config, train, state_means):
    """Ajusta el aprendiz al residual (o al logit del residual) de la referencia."""
    modelo = Modelo(config, state_means)
    if not train:
        return modelo
    base = modelo.reference(train)
    y = [r['y'] for r in train]
    if config.get('space') == 'logit':
        target = [logit(v) - logit(b) for v, b in zip(y, base)]
    else:
        target = [float(v) - b for v, b in zip(y, base)]
    learner = build_learner(config['family'], config.get('alpha'))
    matrix = [r['feature']['x'] for r in train]
    if config.get('weighted'):
        weights = [record_size(r) or 1.0 for r in train]
        if config['family'] == 'hgb':
            learner.fit(matrix, target, sample_weight=weights)
        else:
            learner.fit(matrix, target, ridge__sample_weight=weights)
    else:
        learner.fit(matrix, target)
    modelo.learner = learner
    return modelo


def blend_predictions(modelo, records, blend):
    """(1-w)·aprendiz + w·referencia, con w interpolado por tamaño."""
    blend = blend or {}
    w_small = blend.get('w_small', 0.5)
    w_large = blend.get('w_large', w_small)
    learner = modelo.learner_only(records)
    out = []
    for record, base, adjusted in zip(records, modelo.reference(records), learner):
        w = size_weight(record_size(record), w_small, w_large)
        out.append(clip_rate((1.0 - w) * adjusted + w * base))
    return out


# ---------------------------------------------------------------------------
# Búsqueda por validación temporal
# ---------------------------------------------------------------------------

K_CANDIDATES = [0, 800, 2500]
ALPHA_CANDIDATES = [10, 100, 500]
BLEND_CANDIDATES = [
    (0.2, 0.0), (0.5, 0.0), (0.8, 0.0),
    (0.2, 0.3), (0.5, 0.3), (0.8, 0.3),
    (0.5, 0.6), (0.8, 0.6), (1.0, 1.0),
]


def candidate_configs():
    configs = []
    for k in K_CANDIDATES:
        for space in ('pp', 'logit'):
            for weighted in (False, True):
                for alpha in ALPHA_CANDIDATES:
                    configs.append({
                        'k': k, 'family': 'ridge', 'alpha': alpha,
                        'space': space, 'weighted': weighted,
                    })
                configs.append({
                    'k': k, 'family': 'hgb', 'alpha': None,
                    'space': space, 'weighted': weighted,
                })
    return configs


def temporal_folds(examples_by_year, training_years):
    """Pliegues (entrenamiento, validación) con validación siempre posterior."""
    folds = []
    for index in range(1, len(training_years)):
        validation_year = training_years[index]
        train = [r for year in training_years[:index] for r in examples_by_year.get(year, [])]
        validation = examples_by_year.get(validation_year, [])
        if train and validation:
            folds.append((train, validation))
    return folds


def _best_blend_for(config, folds, state_means):
    fitted = [(fit_config(config, train, state_means), validation) for train, validation in folds]
    best = (None, float('inf'))
    for w_small, w_large in BLEND_CANDIDATES:
        blend = {'w_small': w_small, 'w_large': w_large}
        total, count = 0.0, 0
        for modelo, validation in fitted:
            for record, prediction in zip(validation, blend_predictions(modelo, validation, blend)):
                total += abs(record['y'] - prediction)
                count += 1
        mae = total / count if count else float('inf')
        if mae < best[1]:
            best = (blend, mae)
    return best[0], best[1]


def search(examples_by_year, training_years, state_means):
    """Devuelve (config, blend, informe) elegidos solo con años de entrenamiento."""
    folds = temporal_folds(examples_by_year, training_years)
    report = {'pliegues': len(folds), 'entrenamiento': list(training_years)}
    if len(folds) < 2:
        report['motivo'] = (
            'Menos de dos pliegues temporales: se usa la configuración conservadora '
            'y el corte queda como comprobación, no como selección.'
        )
        return dict(DEFAULT_CONFIG), {'w_small': 0.5, 'w_large': 0.5}, report
    scored = []
    for config in candidate_configs():
        blend, mae = _best_blend_for(config, folds, state_means)
        scored.append((mae, config, blend))
    scored.sort(key=lambda item: item[0])
    best_mae, best_config, best_blend = scored[0]
    report['mae_cv'] = best_mae
    report['mejores'] = [
        {
            'mae_cv': round(mae, 4), 'k': config['k'], 'family': config['family'],
            'space': config['space'], 'weighted': config['weighted'],
            'alpha': config['alpha'], 'w_small': blend['w_small'], 'w_large': blend['w_large'],
        }
        for mae, config, blend in scored[:5]
    ]
    chosen = dict(best_config)
    chosen['w_small'] = best_blend['w_small']
    chosen['w_large'] = best_blend['w_large']
    return chosen, best_blend, report


# ---------------------------------------------------------------------------
# Intervalos conformales
# ---------------------------------------------------------------------------

def conformal_interval(residuals, coverage=0.90):
    """Intervalo por cuantiles del residual con signo (estilo split-conformal).

    Supone intercambiabilidad entre el corte de calibración y el objetivo, que
    entre elecciones distintas no está garantizada; el intervalo es una
    referencia empírica, no una promesa de cobertura.
    """
    if len(residuals) < 5:
        return None
    alpha = 1.0 - coverage
    return quantile(residuals, alpha / 2), quantile(residuals, 1 - alpha / 2)


def empirical_coverage(residuals, low, high):
    if not residuals:
        return None
    return sum(1 for value in residuals if low <= value <= high) / len(residuals)
