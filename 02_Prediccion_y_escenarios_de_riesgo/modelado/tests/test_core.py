import importlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

def api():
    try:return importlib.import_module('core')
    except ModuleNotFoundError:raise AssertionError('Falta implementar core')

def row(year,rate,ns=0,key='01001'):
    return dict(ano=year,clave_municipio_ine=key,entidad_ine='01',municipio_nombre='A',
      ln=1000,sv=(100-rate)*10,nv=rate*10,ns=ns*10,no_especificados_pct=ns,
      abstencion_pct=rate,ln_18_29=250,ln_60_mas=200,ln_urbana=700,ln_rural=300,
      ln_edad_mayor_120=0)

class CoreTests(unittest.TestCase):
    def test_target_and_future_cannot_change_features(self):
        history=[row(2009,40),row(2012,30),row(2015,50),row(2018,35)]
        result=api().make_features(history,2021)
        altered=api().make_features(history+[row(2021,99),row(2024,1)],2021)
        self.assertEqual(result,altered)
        self.assertEqual(result['baseline'],50)
        self.assertEqual(result['source_year'],2018)
    def test_no_same_type_does_not_borrow_other_type(self):
        self.assertIsNone(api().make_features([row(2018,35)],2021))
    def test_bad_quality_lag_is_not_silently_imputed(self):
        self.assertIsNone(api().make_features([row(2015,50,20),row(2018,35)],2021))
    def test_missing_observed_rate_is_not_zero(self):
        r=row(2015,50);r.update(sv=0,nv=0,abstencion_pct=None)
        self.assertIsNone(api().make_features([r,row(2018,35)],2021))
    def test_weighted_error_and_top_selection_are_hand_checked(self):
        m=api().metricas([0,100],[10,80],[9,1],['a','b'],k=1)
        self.assertEqual(m['mae'],15)
        self.assertEqual(m['mae_ponderado'],11)
        self.assertEqual(m['precision_top'],1)
        m=api().metricas([90,80,20,10],[90,20,80,10],[1]*4,list('abcd'),k=2)
        self.assertEqual(m['precision_top'],0.5)
    def test_better_error_but_worse_priority_keeps_baseline(self):
        b=dict(mae=10,mae_ponderado=10,precision_top=.8)
        c=dict(mae=8,mae_ponderado=9,precision_top=.7)
        self.assertEqual(api().choose_model(b,c),'persistencia')
    def test_model_requires_improvement_in_decision_and_error(self):
        b=dict(mae=10,mae_ponderado=10,precision_top=.8)
        c=dict(mae=8,mae_ponderado=9,precision_top=.8)
        self.assertEqual(api().choose_model(b,c),'ridge')
    def test_non_specified_bounds_are_not_forecast_intervals(self):
        self.assertEqual(api().missingness_bounds(60,30,10),(30,40))
        self.assertEqual(api().missingness_bounds(60,40,0),(40,40))
    def test_scenario_is_limited_by_capacity_electorate_and_response(self):
        items=[dict(key='a',risk=60,observed=1000),dict(key='b',risk=None,observed=1000),dict(key='c',risk=50,observed=20)]
        s=api().scenario(items,1,100,25)
        self.assertEqual([x['key'] for x in s['selected']],['a'])
        self.assertEqual(s['additional'],15)
        s=api().scenario(items,10,100,100)
        self.assertEqual(s['served'],120)
        self.assertEqual(s['additional'],70)
    def test_zero_effect_and_zero_capacity_are_valid(self):
        items=[dict(key='a',risk=60,observed=1000)]
        self.assertEqual(api().scenario(items,1,100,0)['additional'],0)
        self.assertEqual(api().scenario(items,0,100,25)['served'],0)
    def test_non_finite_scenario_input_is_rejected(self):
        with self.assertRaises(ValueError):api().scenario([],1,float('nan'),25)

if __name__=='__main__':unittest.main()
