import unittest
import pandas as pd
import numpy as np
from src.analytics.risk_off import compute_risk_off

class TestRiskOff(unittest.TestCase):
    def test_risk_off_high_vol(self):
        dates = pd.date_range("2023-01-01", periods=100)
        vol = pd.Series(np.linspace(0.1, 0.5, 100), index=dates) # Increasing vol
        lambda1 = pd.Series(np.zeros(100) + 0.2, index=dates) # Low correlation
        
        # Threshold at 90%
        # With linspace, top 10% are risk off.
        flag = compute_risk_off(vol, lambda1, lookback=100, pctl=0.90)
        
        self.assertTrue(flag.iloc[-1], "Should be risk off due to high vol")
        self.assertFalse(flag.iloc[0], "Should be risk on initially")

    def test_risk_off_high_lambda(self):
        dates = pd.date_range("2023-01-01", periods=100)
        vol = pd.Series(np.zeros(100) + 0.1, index=dates) # Low vol
        lambda1 = pd.Series(np.linspace(0.1, 0.9, 100), index=dates) # Increasing corr
        
        flag = compute_risk_off(vol, lambda1, lookback=100, pctl=0.90)
        
        self.assertTrue(flag.iloc[-1], "Should be risk off due to high lambda")

if __name__ == '__main__':
    unittest.main()
