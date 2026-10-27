import importlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

def api():
    try:
        return importlib.import_module('core')
    except ModuleNotFoundError:
        raise AssertionError('Falta implementar core')

def row(year, rate, ns=0, key='01001'):
    return dict(ano=year, clave_municipio_ine=key, entidad_ine='01', municipio_nombre='A',
                ln=1000, sv=(100-rate)*10, nv=rate*10, ns=ns*10, no_especificados_pct=ns,
                abstencion_pct=rate, ln_18_29=250, ln_60_mas=200, ln_urbana=700, ln_rural=300,
                ln_edad_mayor_120=0)

class CoreTests(unittest.TestCase):

    # ------------------------------------------------------------------
    # make_features
    # ------------------------------------------------------------------
    def test_target_and_future_cannot_change_features(self):
        history = [row(2009, 40), row(2012, 30), row(2015, 50), row(2018, 35)]
        result = api().make_features(history, 2021)
        altered = api().make_features(history + [row(2021, 99), row(2024, 1)], 2021)
        self.assertEqual(result, altered)
        self.assertEqual(result['baseline'], 50)
        self.assertEqual(result['source_year'], 2018)

    def test_no_same_type_does_not_borrow_other_type(self):
        self.assertIsNone(api().make_features([row(2018, 35)], 2021))

    def test_bad_quality_lag_is_not_silently_imputed(self):
        self.assertIsNone(api().make_features([row(2015, 50, 20), row(2018, 35)], 2021))

    def test_missing_observed_rate_is_not_zero(self):
        r = row(2015, 50)
        r.update(sv=0, nv=0, abstencion_pct=None)
        self.assertIsNone(api().make_features([r, row(2018, 35)], 2021))

    def test_feature_vector_length_matches_feature_names(self):
        """El vector de features debe tener exactamente len(FEATURE_NAMES) elementos."""
        m = api()
        history = [row(2009, 40), row(2012, 30), row(2015, 50), row(2018, 35)]
        result = m.make_features(history, 2021)
        self.assertIsNotNone(result)
        self.assertEqual(len(result['x']), len(m.FEATURE_NAMES))

    def test_interaction_features_are_zero_for_presidential(self):
        """Para elecciones presidenciales las interacciones deben ser 0."""
        m = api()
        history = [row(2015, 40), row(2018, 50)]  # 2018%6=4 → presidencial
        result = m.make_features(history, 2024)   # 2024%6=4 → presidencial
        self.assertIsNotNone(result)
        self.assertEqual(result['x'][10], 0.0)
        self.assertEqual(result['x'][11], 0.0)

    def test_interaction_features_nonzero_for_intermedia(self):
        """Para elecciones intermedias las interacciones reflejan la abstención base."""
        m = api()
        is_int = m.is_intermedia
        history = [row(2015, 40), row(2018, 50)]
        target = 2021
        result = m.make_features(history, target)
        if result is not None:
            if is_int(target):
                self.assertNotEqual(result['x'][10], 0.0)
            else:
                self.assertEqual(result['x'][10], 0.0)

    # ------------------------------------------------------------------
    # metricas
    # ------------------------------------------------------------------
    def test_weighted_error_and_top_selection_are_hand_checked(self):
        m = api().metricas([0, 100], [10, 80], [9, 1], ['a', 'b'], k=1)
        self.assertEqual(m['mae'], 15)
        self.assertEqual(m['mae_ponderado'], 11)
        self.assertEqual(m['precision_top'], 1)
        m = api().metricas([90, 80, 20, 10], [90, 20, 80, 10], [1]*4, list('abcd'), k=2)
        self.assertEqual(m['precision_top'], 0.5)

    def test_metricas_includes_sesgo(self):
        """metricas debe incluir el campo sesgo (bias promedio pred - real)."""
        m = api().metricas([0, 100], [10, 80], [9, 1], ['a', 'b'], k=1)
        self.assertIn('sesgo', m)
        # pred=[10,80], real=[0,100] → sesgo = ((10-0)+(80-100))/2 = -5
        self.assertAlmostEqual(m['sesgo'], -5.0)

    def test_sesgo_positive_when_model_overestimates(self):
        """Sesgo positivo cuando el modelo sobreestima."""
        m = api().metricas([40, 50], [50, 60], [1, 1], ['a', 'b'])
        self.assertGreater(m['sesgo'], 0)

    def test_metricas_accepts_mixed_key_types_as_strings(self):
        """metricas no debe fallar con claves de tipo mixto (se convierten a str)."""
        # No debe lanzar TypeError aunque las claves sean enteros
        m = api().metricas([10, 20], [11, 19], [1, 1], [1001, 1002])
        self.assertIn('precision_top', m)

    # ------------------------------------------------------------------
    # choose_model — incluyendo cota de sesgo (fix bug #5)
    # ------------------------------------------------------------------
    def test_better_error_but_worse_priority_keeps_baseline(self):
        b = dict(mae=10, mae_ponderado=10, precision_top=.8)
        c = dict(mae=8, mae_ponderado=9, precision_top=.7)
        self.assertEqual(api().choose_model(b, c), 'persistencia')

    def test_model_requires_improvement_in_decision_and_error(self):
        b = dict(mae=10, mae_ponderado=10, precision_top=.8)
        c = dict(mae=8, mae_ponderado=9, precision_top=.8)
        self.assertEqual(api().choose_model(b, c), 'ridge')

    def test_choose_model_without_sesgo_is_backward_compatible(self):
        """Si los dicts no tienen 'sesgo', choose_model funciona como antes."""
        b = dict(mae=10, mae_ponderado=10, precision_top=.8)
        c = dict(mae=8, mae_ponderado=9, precision_top=.8)
        self.assertEqual(api().choose_model(b, c), 'ridge')

    def test_choose_model_rejects_candidate_with_large_sesgo_degradation(self):
        """Rechaza el candidato si su sesgo es mucho peor que el baseline."""
        # baseline sesgo = -1 (leve subestimación)
        # candidate sesgo = -8 (subestima mucho más → degradación = 7 pp > umbral de 3)
        b = dict(mae=10, mae_ponderado=10, precision_top=.8, sesgo=-1.0)
        c = dict(mae=8, mae_ponderado=9, precision_top=.8, sesgo=-8.0)
        self.assertEqual(api().choose_model(b, c), 'persistencia')

    def test_choose_model_accepts_candidate_within_sesgo_tolerance(self):
        """Acepta el candidato si la degradación de sesgo está dentro del umbral."""
        b = dict(mae=10, mae_ponderado=10, precision_top=.8, sesgo=-1.0)
        c = dict(mae=8, mae_ponderado=9, precision_top=.8, sesgo=-3.5)
        # degradación = -3.5 - (-1.0) = -2.5, dentro del umbral de -3.0
        self.assertEqual(api().choose_model(b, c), 'ridge')

    def test_choose_model_custom_sesgo_threshold(self):
        """El umbral de sesgo es configurable."""
        b = dict(mae=10, mae_ponderado=10, precision_top=.8, sesgo=-1.0)
        c = dict(mae=8, mae_ponderado=9, precision_top=.8, sesgo=-3.5)
        # Con umbral estricto de 1.0, -2.5 de degradación lo rechaza
        self.assertEqual(api().choose_model(b, c, max_sesgo_degradacion=1.0), 'persistencia')
        # Con umbral holgado de 5.0, lo acepta
        self.assertEqual(api().choose_model(b, c, max_sesgo_degradacion=5.0), 'ridge')

    # ------------------------------------------------------------------
    # missingness_bounds
    # ------------------------------------------------------------------
    def test_non_specified_bounds_are_not_forecast_intervals(self):
        self.assertEqual(api().missingness_bounds(60, 30, 10), (30, 40))
        self.assertEqual(api().missingness_bounds(60, 40, 0), (40, 40))

    # ------------------------------------------------------------------
    # scenario — validaciones ahora individuales con mensajes claros
    # ------------------------------------------------------------------
    def test_scenario_is_limited_by_capacity_electorate_and_response(self):
        items = [
            dict(key='a', risk=60, observed=1000),
            dict(key='b', risk=None, observed=1000),
            dict(key='c', risk=50, observed=20),
        ]
        s = api().scenario(items, 1, 100, 25)
        self.assertEqual([x['key'] for x in s['selected']], ['a'])
        self.assertEqual(s['additional'], 15)
        s = api().scenario(items, 10, 100, 100)
        self.assertEqual(s['served'], 120)
        self.assertEqual(s['additional'], 70)

    def test_zero_effect_and_zero_capacity_are_valid(self):
        items = [dict(key='a', risk=60, observed=1000)]
        self.assertEqual(api().scenario(items, 1, 100, 0)['additional'], 0)
        self.assertEqual(api().scenario(items, 0, 100, 25)['served'], 0)

    def test_non_finite_scenario_input_is_rejected(self):
        with self.assertRaises(ValueError):
            api().scenario([], 1, float('nan'), 25)

    def test_scenario_rejects_fractional_capacity(self):
        """capacity debe ser entero; 1.5 debe ser rechazado."""
        with self.assertRaises(ValueError):
            api().scenario([], 1.5, 100, 25)

    def test_scenario_rejects_negative_reach(self):
        """reach negativo debe ser rechazado."""
        with self.assertRaises(ValueError):
            api().scenario([], 1, -10, 25)

    def test_scenario_rejects_response_above_100(self):
        """response > 100 no tiene sentido y debe ser rechazado."""
        with self.assertRaises(ValueError):
            api().scenario([], 1, 100, 110)

if __name__ == '__main__':
    unittest.main()
