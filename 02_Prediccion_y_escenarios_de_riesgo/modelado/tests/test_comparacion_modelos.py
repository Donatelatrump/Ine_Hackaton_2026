"""Contratos de selección que evitan decisiones basadas en redondeos o sesgo con signo."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from comparar_modelos import choose


def score(mae,weighted,precision=.4,seconds=1):
    return {'mean_mae':mae,'mean_weighted_mae':weighted,'mean_precision_top50':precision,'mean_fit_seconds':seconds}


class SelectionTests(unittest.TestCase):
    def test_lower_weighted_error_breaks_practical_mae_tie(self):
        self.assertEqual(choose({'lightgbm':score(6.8304,4.8385),'hgb':score(6.8360,4.6684)}),'hgb')

    def test_more_than_tolerance_cannot_win_on_speed_or_weighted_error(self):
        self.assertEqual(choose({'a':score(6,5,seconds=1),'b':score(6.06,1,seconds=.001)}),'a')

    def test_precision_then_runtime_break_remaining_ties(self):
        self.assertEqual(choose({'a':score(6,5,.4,.001),'b':score(6,5,.44,1)}),'b')
        self.assertEqual(choose({'a':score(6,5,.4,.001),'b':score(6,5,.4,1)}),'a')

    def test_bias_with_sign_does_not_reject_absolute_bias_improvement(self):
        values={'a':{**score(6,5), 'bias':3},'b':{**score(7,6), 'bias':8}}
        self.assertEqual(choose(values),'a')


if __name__=='__main__':unittest.main()
