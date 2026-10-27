import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import core
import entrenamiento


def row(year, rate, ns=0, key='01001', sv=None, nv=None, ln=1000, entidad='01'):
    if sv is None:
        sv = (100 - rate) * ln / 100
    if nv is None:
        nv = rate * ln / 100
    return dict(ano=year, clave_municipio_ine=key, entidad_ine=entidad, municipio_nombre='A',
                ln=ln, sv=sv, nv=nv, ns=ns * ln / 100, no_especificados_pct=ns,
                abstencion_pct=rate, ln_18_29=ln * 0.25, ln_60_mas=ln * 0.2,
                ln_urbana=ln * 0.7, ln_rural=ln * 0.3, ln_edad_mayor_120=0)


class TransformacionesTests(unittest.TestCase):
    def test_logit_and_logistic_are_inverse(self):
        for rate in (1.0, 25.0, 50.0, 73.4, 99.0):
            self.assertAlmostEqual(entrenamiento.logistic(entrenamiento.logit(rate)), rate, places=6)

    def test_logit_saturates_instead_of_returning_infinity(self):
        self.assertTrue(math.isfinite(entrenamiento.logit(0.0)))
        self.assertTrue(math.isfinite(entrenamiento.logit(100.0)))
        self.assertLess(entrenamiento.logit(0.0), 0)

    def test_logistic_stays_bounded_for_extreme_values(self):
        # El contrato es quedar dentro de [0, 100]; en el extremo negativo
        # exp() subdesborda a 0 y la salida es 0.0, no un error ni un infinito.
        self.assertGreaterEqual(entrenamiento.logistic(-1e6), 0.0)
        self.assertLessEqual(entrenamiento.logistic(1e6), 100.0)
        self.assertAlmostEqual(entrenamiento.logistic(0.0), 50.0, places=9)

    def test_clip_rate_bounds(self):
        self.assertEqual(entrenamiento.clip_rate(-5), 0.0)
        self.assertEqual(entrenamiento.clip_rate(140), 100.0)


class EncogimientoYBlendTests(unittest.TestCase):
    def test_size_weight_interpolates_between_endpoints(self):
        self.assertAlmostEqual(entrenamiento.size_weight(1000, 0.8, 0.2), 0.8)
        self.assertAlmostEqual(entrenamiento.size_weight(500000, 0.8, 0.2), 0.2)
        medio = entrenamiento.size_weight(30000, 0.8, 0.2)
        self.assertLess(medio, 0.8)
        self.assertGreater(medio, 0.2)

    def test_size_weight_is_monotone_decreasing_when_small_weighs_more(self):
        pesos = [entrenamiento.size_weight(s, 0.9, 0.0) for s in (1000, 5000, 20000, 90000, 400000)]
        self.assertEqual(pesos, sorted(pesos, reverse=True))

    def test_pooled_baseline_without_strength_is_the_plain_baseline(self):
        self.assertAlmostEqual(entrenamiento.pooled_baseline(60.0, 1000, 40.0, 0), 60.0)

    def test_pooled_baseline_moves_small_municipalities_toward_the_state(self):
        pequeno = entrenamiento.pooled_baseline(60.0, 500, 40.0, 5000)
        grande = entrenamiento.pooled_baseline(60.0, 400000, 40.0, 5000)
        self.assertLess(pequeno, 60.0)
        self.assertGreater(pequeno, 40.0)
        self.assertGreater(grande, pequeno)
        self.assertGreater(grande, 59.0)

    def test_pooled_baseline_without_state_mean_is_the_baseline(self):
        self.assertAlmostEqual(entrenamiento.pooled_baseline(60.0, 10, None, 5000), 60.0)

    def test_state_year_means_weight_by_observed_participation(self):
        rows = [
            row(2018, 40, sv=100, nv=100, ln=200, key='a'),
            row(2018, 80, sv=100, nv=400, ln=0, key='b'),
            row(2021, 10, sv=10, nv=90, ln=100, key='c'),
        ]
        medias = entrenamiento.state_year_means(rows)
        self.assertAlmostEqual(medias[('01', 2018)], 48000.0 / 700.0, places=6)
        self.assertAlmostEqual(medias[('01', 2021)], 10.0, places=6)

    def test_state_year_means_ignore_rows_without_observable_rate(self):
        sin_datos = row(2018, 50, sv=0, nv=0, ln=0, key='x')
        sin_datos['abstencion_pct'] = None
        self.assertEqual(entrenamiento.state_year_means([sin_datos]), {})


class StubModelo:
    """Sustituto mínimo: permite probar el blend sin entrenar nada."""

    def __init__(self, reference, adjusted):
        self._reference = reference
        self._adjusted = adjusted

    def reference(self, records):
        return list(self._reference)

    def learner_only(self, records):
        return list(self._adjusted)


class BlendTests(unittest.TestCase):
    def test_pure_reference_weight_returns_the_reference(self):
        modelo = StubModelo([50.0], [70.0])
        records = [{'feature': {}, 'weight_source': 1000}]
        resultado = entrenamiento.blend_predictions(modelo, records, {'w_small': 1.0, 'w_large': 1.0})
        self.assertAlmostEqual(resultado[0], 50.0)

    def test_zero_weight_returns_the_learner(self):
        modelo = StubModelo([50.0], [70.0])
        records = [{'feature': {}, 'weight_source': 1000}]
        resultado = entrenamiento.blend_predictions(modelo, records, {'w_small': 0.0, 'w_large': 0.0})
        self.assertAlmostEqual(resultado[0], 70.0)

    def test_blend_leans_to_reference_for_small_and_to_learner_for_large(self):
        modelo = StubModelo([50.0, 50.0], [80.0, 80.0])
        records = [{'feature': {}, 'weight_source': 1000}, {'feature': {}, 'weight_source': 500000}]
        resultado = entrenamiento.blend_predictions(modelo, records, {'w_small': 0.9, 'w_large': 0.1})
        self.assertLess(resultado[0], resultado[1])
        self.assertLess(resultado[0], 60.0)
        self.assertGreater(resultado[1], 70.0)

    def test_blend_output_is_bounded(self):
        modelo = StubModelo([0.0], [-50.0])
        records = [{'feature': {}, 'weight_source': 1000}]
        resultado = entrenamiento.blend_predictions(modelo, records, {'w_small': 0.5, 'w_large': 0.5})
        self.assertGreaterEqual(resultado[0], 0.0)
        self.assertLessEqual(resultado[0], 100.0)


class IntervaloTests(unittest.TestCase):
    def test_conformal_interval_needs_enough_samples(self):
        self.assertIsNone(entrenamiento.conformal_interval([1.0, 2.0]))

    def test_conformal_interval_brackets_the_residuals(self):
        residuales = [-10.0, -5.0, 0.0, 5.0, 10.0, -3.0, 3.0, 7.0, -7.0, 1.0]
        bajo, alto = entrenamiento.conformal_interval(residuales, coverage=0.9)
        self.assertLessEqual(bajo, 0.0)
        self.assertGreaterEqual(alto, 0.0)
        cobertura = entrenamiento.empirical_coverage(residuales, bajo, alto)
        self.assertGreaterEqual(cobertura, 0.8)

    def test_empirical_coverage_of_empty_set_is_none(self):
        self.assertIsNone(entrenamiento.empirical_coverage([], -1, 1))


class GuardaSesgoTests(unittest.TestCase):
    """Regresión del bug: la guarda restaba sesgos con signo y rechazaba al
    candidato que corregía la sobreestimación de la referencia (2.5 puntos de
    MAE en 2021 quedaban sin usar)."""

    PERSISTENCIA_2021 = dict(
        mae=12.115857378526517, mae_ponderado=8.052371822830299,
        precision_top=0.32, sesgo=7.866000622629297, spearman=0.4848773821411889,
    )
    APRENDIZ_2021 = dict(
        mae=8.897042355030653, mae_ponderado=5.2981724834888615,
        precision_top=0.42, sesgo=3.724626351068955, spearman=0.6301971665477217,
    )

    def test_candidate_that_reduces_bias_is_accepted(self):
        self.assertTrue(core.choose_candidate(self.PERSISTENCIA_2021, self.APRENDIZ_2021))
        self.assertEqual(core.choose_model(self.PERSISTENCIA_2021, self.APRENDIZ_2021), 'ridge')

    def test_candidate_with_much_larger_absolute_bias_is_rejected(self):
        referencia = dict(mae=5.64, mae_ponderado=3.54, precision_top=0.54, sesgo=-4.31, spearman=0.83)
        candidato = dict(mae=4.0, mae_ponderado=3.30, precision_top=0.60, sesgo=-8.69, spearman=0.84)
        self.assertFalse(core.choose_candidate(referencia, candidato))

    def test_bias_inside_the_tolerance_is_accepted(self):
        referencia = dict(mae=5.64, mae_ponderado=3.54, precision_top=0.54, sesgo=-4.31, spearman=0.83)
        candidato = dict(mae=4.0, mae_ponderado=3.30, precision_top=0.60, sesgo=-6.0, spearman=0.84)
        self.assertTrue(core.choose_candidate(referencia, candidato))

    def test_ranking_degradation_rejects_an_otherwise_better_candidate(self):
        referencia = dict(mae=12.0, mae_ponderado=8.0, precision_top=0.32, sesgo=7.8, spearman=0.60)
        candidato = dict(mae=9.0, mae_ponderado=6.0, precision_top=0.40, sesgo=4.0, spearman=0.40)
        self.assertFalse(core.choose_candidate(referencia, candidato))

    def test_ranking_guard_is_tolerant_to_noise(self):
        referencia = dict(mae=12.0, mae_ponderado=8.0, precision_top=0.32, sesgo=7.8, spearman=0.60)
        candidato = dict(mae=9.0, mae_ponderado=6.0, precision_top=0.40, sesgo=4.0, spearman=0.59)
        self.assertTrue(core.choose_candidate(referencia, candidato))


class MetricasTests(unittest.TestCase):
    def test_metricas_reports_spearman(self):
        m = core.metricas([10, 20, 30, 40], [11, 21, 31, 41], [1] * 4, list('abcd'))
        self.assertAlmostEqual(m['spearman'], 1.0, places=6)

    def test_metricas_reports_inverse_spearman(self):
        m = core.metricas([10, 20, 30, 40], [41, 31, 21, 11], [1] * 4, list('abcd'))
        self.assertAlmostEqual(m['spearman'], -1.0, places=6)

    def test_spearman_is_none_without_variance(self):
        self.assertIsNone(core.spearman([10, 10, 10], [1, 2, 3]))


class CovariablesTests(unittest.TestCase):
    def test_feature_names_align_with_the_vector(self):
        historia = [row(2009, 40), row(2012, 30), row(2015, 50), row(2018, 35)]
        resultado = core.make_features(historia, 2021)
        self.assertEqual(len(resultado['x']), len(core.FEATURE_NAMES))
        self.assertEqual(len(core.feature_names()), len(resultado['x']))

    def test_projection_renames_only_the_demographic_positions(self):
        nombres = core.feature_names(projection=True)
        self.assertEqual(nombres[:4], core.feature_names()[:4])
        self.assertEqual(nombres[6:], core.feature_names()[6:])
        self.assertNotEqual(nombres[4], core.feature_names()[4])
        self.assertEqual(nombres[4], 'prop_18_29_proy')
        self.assertEqual(nombres[5], 'prop_60_mas_proy')

    def test_conapo_covariates_use_the_source_year_and_flag_availability(self):
        historia = [row(2015, 50, ln=1000), row(2018, 35, ln=1100)]
        conapo = {'01001': {
            2015: {'POB_TOTAL': 2000.0, 'POB_012_29': 500.0, 'POB_60_mm': 300.0},
            2018: {'POB_TOTAL': 2200.0, 'POB_012_29': 550.0, 'POB_60_mm': 330.0},
        }}
        resultado = core.make_features(historia, 2021, 10, conapo)
        self.assertFalse(resultado['conapo_fallback'])
        self.assertAlmostEqual(resultado['x'][16], 550.0 / 2200.0, places=9)
        self.assertAlmostEqual(resultado['x'][17], 330.0 / 2200.0, places=9)
        self.assertAlmostEqual(resultado['x'][18], math.log(2200.0 / 2000.0), places=9)

    def test_growth_between_antecedents_is_always_available(self):
        historia = [row(2015, 50, ln=1000), row(2018, 35, ln=1250)]
        resultado = core.make_features(historia, 2021)
        self.assertAlmostEqual(resultado['x'][15], math.log(1250.0 / 1000.0), places=9)

    def test_missing_conapo_is_flagged_and_falls_back_to_ccpc(self):
        historia = [row(2015, 50), row(2018, 35)]
        resultado = core.make_features(historia, 2021, 10, {'99999': {2018: {'POB_TOTAL': 1.0}}})
        self.assertTrue(resultado['conapo_fallback'])
        self.assertAlmostEqual(resultado['x'][16], resultado['x'][4], places=9)

    def test_covariates_do_not_change_eligibility(self):
        historia = [row(2015, 50), row(2018, 35)]
        self.assertIsNotNone(core.make_features(historia, 2021))
        self.assertIsNotNone(core.make_features(historia, 2021, 10, {'01001': {2018: {'POB_TOTAL': 100.0}}}))


class AjusteTests(unittest.TestCase):
    def _ejemplos(self, count=60, year=2021):
        ejemplos = []
        for index in range(count):
            rate = 30.0 + (index % 20)
            feature = {
                'x': [float(index % 7), rate / 100.0] + [0.0] * (len(core.FEATURE_NAMES) - 2),
                'baseline': 40.0 + (index % 10),
                'source_year': 2018,
                'same_year': 2015,
                'source_size': 5000.0 + index * 1000,
            }
            ejemplos.append(dict(key=f'{index:05d}', year=year, feature=feature, y=rate,
                                 weight=1000.0, state='01', weight_source=feature['source_size']))
        return ejemplos

    def test_fit_config_learns_a_residual_and_predicts_in_range(self):
        entrenamiento_ = self._ejemplos()
        config = {'k': 0, 'family': 'ridge', 'alpha': 10, 'space': 'pp', 'weighted': False,
                  'w_small': 0.0, 'w_large': 0.0}
        modelo = entrenamiento.fit_config(config, entrenamiento_, {})
        self.assertIsNotNone(modelo.learner)
        predicciones = modelo.learner_only(entrenamiento_)
        self.assertEqual(len(predicciones), len(entrenamiento_))
        self.assertTrue(all(0.0 <= p <= 100.0 for p in predicciones))

    def test_logit_space_predictions_are_bounded(self):
        entrenamiento_ = self._ejemplos()
        config = {'k': 0, 'family': 'ridge', 'alpha': 10, 'space': 'logit', 'weighted': False,
                  'w_small': 0.0, 'w_large': 0.0}
        modelo = entrenamiento.fit_config(config, entrenamiento_, {})
        predicciones = modelo.learner_only(entrenamiento_)
        self.assertTrue(all(0.0 <= p <= 100.0 for p in predicciones))

    def test_weighted_fit_accepts_sample_weights(self):
        entrenamiento_ = self._ejemplos()
        config = {'k': 0, 'family': 'ridge', 'alpha': 10, 'space': 'pp', 'weighted': True,
                  'w_small': 0.0, 'w_large': 0.0}
        modelo = entrenamiento.fit_config(config, entrenamiento_, {})
        self.assertIsNotNone(modelo.learner)

    def test_pooling_changes_only_small_municipalities(self):
        entrenamiento_ = self._ejemplos()
        config = {'k': 1500, 'family': 'ridge', 'alpha': 10, 'space': 'pp', 'weighted': False,
                  'w_small': 1.0, 'w_large': 1.0}
        modelo = entrenamiento.fit_config(config, entrenamiento_, {('01', 2018): 50.0})
        chico = dict(entrenamiento_[0], weight_source=100.0)
        grande = dict(entrenamiento_[0], weight_source=1_000_000.0)
        self.assertNotAlmostEqual(modelo.base(chico), modelo.base(grande), places=3)
        self.assertLess(abs(modelo.base(grande) - entrenamiento_[0]['feature']['baseline']), 0.1)

    def test_search_without_folds_returns_the_conservative_config(self):
        config, blend, report = entrenamiento.search({2015: self._ejemplos()}, [2015], {})
        self.assertEqual(config['family'], 'ridge')
        self.assertEqual(config['k'], 0)
        self.assertEqual(report['pliegues'], 0)
        self.assertIn('motivo', report)

    def test_temporal_folds_never_validate_on_a_year_used_for_training(self):
        por_ano = {
            2015: self._ejemplos(20, 2015),
            2018: self._ejemplos(20, 2018),
            2021: self._ejemplos(20, 2021),
        }
        folds = entrenamiento.temporal_folds(por_ano, [2015, 2018, 2021])
        self.assertEqual(len(folds), 2)
        for train, validation in folds:
            self.assertTrue(all(r['year'] < validation[0]['year'] for r in train))


if __name__ == '__main__':
    unittest.main()
