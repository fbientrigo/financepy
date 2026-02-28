import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.indicators.advanced import AdvancedIndicators

class TestAdvancedIndicatorsFix(unittest.TestCase):
    @patch('src.indicators.advanced.rolling_hurst_dfa')
    @patch('src.indicators.advanced.prepare_log_returns')
    def test_calculate_uses_sanitizer(self, mock_prepare, mock_rolling):
        # Setup
        config = {'hurst': {'window': 10, 'min_scale': 4}, 'ewma_vol': {'span': 10}}
        adv = AdvancedIndicators(config)
        
        # Data
        df = pd.DataFrame({
            'Close': [100, 101, 102, 101, 100],
            'ret_1d': [0.01, 0.01, -0.01, -0.01, 0.0] # Dummy
        })
        
        # Mock returns
        mock_prepare.return_value = pd.Series([0.01, 0.01, -0.01, -0.01, 0.0])
        mock_rolling.return_value = pd.Series([0.5, 0.5, 0.5, 0.5, 0.5])
        
        # Execute
        result = adv.calculate(df)
        
        # Verify prepare_log_returns was called with Close
        mock_prepare.assert_called_once()
        # Verify rolling_hurst_dfa was called with the result of sanitization
        mock_rolling.assert_called_once()
        
        print("SUCCESS: AdvancedIndicators uses prepare_log_returns on Close price!")

if __name__ == '__main__':
    unittest.main()
