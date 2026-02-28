import unittest
import pandas as pd
import numpy as np
from src.indicators.common import CommonIndicators

class TestIndicators(unittest.TestCase):
    def test_zscore_simple(self):
        # Create a series with constant mean and std
        # [1, 1, 1, ..., 1] -> Mean=1, Std=0. Z=undefined? 
        # Let's use alternating 1, -1.
        
        data = [100, 102, 100, 102, 100]
        dates = pd.date_range("2023-01-01", periods=5)
        df = pd.DataFrame({'Close': data}, index=dates)
        
        # Window 2, std should be non-zero
        config = {
            'zscore_window': 3,
            'volatility_window_short': 3,
            'volatility_window_long': 5,
            'bollinger_window': 3,
            'bollinger_std': 1.0
        }
        
        ind = CommonIndicators(config)
        res = ind.calculate(df)
        
        # Validating columns exist
        self.assertIn('zscore', res.columns)
        self.assertIn('bb_upper', res.columns)
        
        # Check specific values (e.g. last row)
        # Window=3. Values: 100, 102, 100. Mean=100.66. Std=1.15
        # Last val=100. Z = (100 - 100.66) / 1.15 ~= -0.57
        # Let's just check it's not NaN for the last few rows
        self.assertFalse(np.isnan(res['zscore'].iloc[-1]))
        
        # Check NaN at start
        self.assertTrue(np.isnan(res['zscore'].iloc[0]))

if __name__ == '__main__':
    unittest.main()
