import unittest, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import ampliacion

class AdditionalTests(unittest.TestCase):
    def test_spearman_ties_and_reverse(self):
        self.assertAlmostEqual(ampliacion.spearman([1,1,3],[2,2,6]),1)
        self.assertAlmostEqual(ampliacion.spearman([1,2,3],[3,2,1]),-1)
        self.assertIsNone(ampliacion.spearman([1,1],[2,3]))
    def test_red_threshold_is_frozen_and_empty_predictions_are_explicit(self):
        m=ampliacion.classification_metrics([10,60,80],[15,55,75],50)
        self.assertEqual(m['rojos_predichos'],2)
        self.assertEqual(m['precision_rojo'],1)
        self.assertEqual(m['recobrado_rojo'],1)
        self.assertIsNone(ampliacion.classification_metrics([10,60],[0,0],50)['precision_rojo'])
    def test_ns_exclusion_is_specific(self):
        h=[{'ano':2021,'sv':50,'nv':50,'ln':100,'abstencion_pct':50,'no_especificados_pct':12},
           {'ano':2024,'sv':50,'nv':50,'ln':100,'abstencion_pct':50,'no_especificados_pct':15}]
        reasons=ampliacion.exclusion_reasons(h,2027,10)
        self.assertTrue(any('2024' in r for r in reasons))
        self.assertTrue(any('2021' in r for r in reasons))
    def test_size_bins_are_prior_observed_population(self):
        self.assertEqual(ampliacion.size_bin(9999),'menos_10000')
        self.assertEqual(ampliacion.size_bin(10000),'10000_99999')
        self.assertEqual(ampliacion.size_bin(100000),'100000_mas')

if __name__=='__main__':unittest.main()
