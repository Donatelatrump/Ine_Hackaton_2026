import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ampliacion

class AdditionalTests(unittest.TestCase):
    def test_spearman_ties_and_reverse(self):
        self.assertAlmostEqual(ampliacion.spearman([1, 1, 3], [2, 2, 6]), 1)
        self.assertAlmostEqual(ampliacion.spearman([1, 2, 3], [3, 2, 1]), -1)
        self.assertIsNone(ampliacion.spearman([1, 1], [2, 3]))

    def test_red_threshold_is_frozen_and_empty_predictions_are_explicit(self):
        m = ampliacion.classification_metrics([10, 60, 80], [15, 55, 75], 50)
        self.assertEqual(m['rojos_predichos'], 2)
        self.assertEqual(m['precision_rojo'], 1)
        self.assertEqual(m['recobrado_rojo'], 1)
        self.assertIsNone(ampliacion.classification_metrics([10, 60], [0, 0], 50)['precision_rojo'])

    def test_classification_metrics_empty_observed_reds(self):
        """Si no hay observados por encima del umbral, recobrado_rojo debe ser None."""
        m = ampliacion.classification_metrics([10, 20], [55, 10], 50)
        self.assertEqual(m['rojos_observados'], 0)
        self.assertEqual(m['rojos_predichos'], 1)
        self.assertEqual(m['verdaderos_positivos'], 0)
        self.assertIsNone(m['recobrado_rojo'])
        self.assertEqual(m['precision_rojo'], 0.0)

    def test_ns_exclusion_is_specific(self):
        h = [
            {'ano': 2021, 'sv': 50, 'nv': 50, 'ln': 100, 'abstencion_pct': 50, 'no_especificados_pct': 12},
            {'ano': 2024, 'sv': 50, 'nv': 50, 'ln': 100, 'abstencion_pct': 50, 'no_especificados_pct': 15},
        ]
        reasons = ampliacion.exclusion_reasons(h, 2027, 10)
        self.assertTrue(any('2024' in r for r in reasons))
        self.assertTrue(any('2021' in r for r in reasons))

    def test_exclusion_reasons_no_participation_or_nan(self):
        """Historial con participación cero o NaN en abstención."""
        h = [
            {'ano': 2021, 'sv': 0, 'nv': 0, 'ln': 100, 'abstencion_pct': None, 'no_especificados_pct': 0},
            {'ano': 2024, 'sv': 50, 'nv': 50, 'ln': 100, 'abstencion_pct': float('nan'), 'no_especificados_pct': 0},
        ]
        reasons = ampliacion.exclusion_reasons(h, 2027, 10)
        self.assertTrue(any('2024' in r and 'sin participación observable' in r for r in reasons))
        self.assertTrue(any('2021' in r and 'sin participación observable' in r for r in reasons))

    def test_size_bins_are_prior_observed_population(self):
        self.assertEqual(ampliacion.size_bin(9999), 'menos_10000')
        self.assertEqual(ampliacion.size_bin(10000), '10000_99999')
        self.assertEqual(ampliacion.size_bin(100000), '100000_mas')

if __name__ == '__main__':
    unittest.main()
