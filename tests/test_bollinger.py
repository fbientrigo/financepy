import unittest
import pandas as pd
import numpy as np
from src.indicators.common import CommonIndicators

class TestBollinger(unittest.TestCase):
    def setUp(self):
        self.config = {
            'bollinger_window': 20,
            'bollinger_std': 2.0
        }
        self.indicator = CommonIndicators(self.config)

    def test_bollinger_constant(self):
        # Constant price -> MB=Price, Std=0 -> Upper=Lower=Price
        dates = pd.date_range("2023-01-01", periods=50)
        df = pd.DataFrame({'Close': [100.0] * 50}, index=dates)
        
        res = self.indicator.calculate(df)
        
        # Check mid band
        self.assertTrue(np.allclose(res['bb_mid'].dropna(), 100.0))
        # Check upper/lower
        self.assertTrue(np.allclose(res['bb_upper'].dropna(), 100.0))
        self.assertTrue(np.allclose(res['bb_lower'].dropna(), 100.0))
        # Check Z-score (0/0 handling?)
        # Implementation has: (close - mb) / (std.replace(0, np.nan))
        # So Z should be NaN
        self.assertTrue(res['zscore'].dropna().empty, "Z-score should be NaN for constant price (std=0)")

    def test_bollinger_linear(self):
        # Linear trend: 1, 2, 3...
        dates = pd.date_range("2023-01-01", periods=50)
        prices = np.arange(1, 51, dtype=float)
        df = pd.DataFrame({'Close': prices}, index=dates)
        
        res = self.indicator.calculate(df)
        
        # Check columns exist
        for col in ['bb_mid', 'bb_upper', 'bb_lower', 'zscore']:
            self.assertIn(col, res.columns)
            
        # Check validity (no infs)
        self.assertFalse(np.isinf(res['bb_upper']).any())
        self.assertFalse(np.isinf(res['zscore']).any())
        
        # Check Last value
        # MA(20) of linear trend is lagged.
        # Mean of 31..50 is 40.5
        last_ma = res['bb_mid'].iloc[-1]
        self.assertAlmostEqual(last_ma, 40.5)

if __name__ == '__main__':
    unittest.main()
