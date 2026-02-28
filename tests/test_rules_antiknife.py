import unittest
import pandas as pd
import numpy as np
from src.signals.basic import BasicSignals

class TestRulesAntiKnife(unittest.TestCase):
    def setUp(self):
        # Default policy
        self.params = {'signal_policy': {'risk_off_action': 'degrade'}}
        self.signals = BasicSignals(self.params)

    def test_buy_alert_trigger(self):
        # Verify signal triggers when Z < -2.5 (or -2.0 per implementation)
        # Previous implementation was Z < -2.0 = BUY_ALERT
        
        dates = pd.date_range("2023-01-01", periods=5)
        # Create scenario: Z goes 0 -> -1 -> -2.1 -> -2.6 -> 0
        z_vals = [0.0, -1.0, -2.1, -2.6, 0.0]
        df = pd.DataFrame({'zscore': z_vals}, index=dates)
        
        res = self.signals.generate(df)
        
        # -2.1 -> BUY_ALERT
        self.assertEqual(res.iloc[2]['signal'], 'BUY_ALERT')
        # -2.6 -> BUY_ALERT
        self.assertEqual(res.iloc[3]['signal'], 'BUY_ALERT')
        # 0 -> NONE
        self.assertEqual(res.iloc[4]['signal'], 'NONE')

    def test_risk_off_suppression(self):
        # If risk_off_flag is True, confidence should be degraded
        dates = pd.date_range("2023-01-01", periods=1)
        df = pd.DataFrame({
            'zscore': [-3.0], # Strong buy
            'risk_off_flag': [True]
        }, index=dates)
        
        res = self.signals.generate(df)
        
        # Should be BUY_ALERT but low confidence
        self.assertEqual(res.iloc[0]['signal'], 'BUY_ALERT')
        
        # Base confidence for |3| is 3/4 = 0.75.
        # Degraded by 0.5 -> 0.375
        self.assertAlmostEqual(res.iloc[0]['confidence'], 0.375)

    def test_regime_suppression(self):
        # If TREND regime, Mean Reversion buy should be degraded
        dates = pd.date_range("2023-01-01", periods=1)
        df = pd.DataFrame({
            'zscore': [-3.0], 
            'regime_label': ['TREND']
        }, index=dates)
        
        res = self.signals.generate(df)
        
        # Base 0.75 -> Trend Degrade (0.5) -> 0.375
        self.assertAlmostEqual(res.iloc[0]['confidence'], 0.375)
        
    def test_regime_boost(self):
        # If MEAN_REVERT regime, Mean Reversion buy should be boosted
        dates = pd.date_range("2023-01-01", periods=1)
        df = pd.DataFrame({
            'zscore': [-3.0], 
            'regime_label': ['MEAN_REVERT']
        }, index=dates)
        
        res = self.signals.generate(df)
        
        # Base 0.75 -> Boost (1.2) -> 0.9
        self.assertAlmostEqual(res.iloc[0]['confidence'], 0.9)

if __name__ == '__main__':
    unittest.main()
