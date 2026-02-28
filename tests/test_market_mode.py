import unittest
import pandas as pd
import numpy as np
from src.indicators.market_mode import compute_lambda1_norm

class TestMarketMode(unittest.TestCase):
    def test_market_mode_high_correlation(self):
        # Create perfectly correlated assets
        dates = pd.date_range("2023-01-01", periods=100)
        base = np.random.randn(100)
        
        data = {
            'A': base + np.random.normal(0, 0.01, 100),
            'B': base + np.random.normal(0, 0.01, 100),
            'C': base + np.random.normal(0, 0.01, 100)
        }
        df = pd.DataFrame(data, index=dates)
        
        # Window=20
        lambda1 = compute_lambda1_norm(df, window=20, min_assets=3)
        
        # Last value should be near 1.0 (since normalized)
        # Max eigenvalue of 3x3 matrix of 1s is 3. Normalized -> 1.
        val = lambda1.iloc[-1]
        self.assertTrue(val > 0.9, f"Expected Lambda1 > 0.9 for correlated, got {val}")

    def test_market_mode_uncorrelated(self):
        # Random assets
        dates = pd.date_range("2023-01-01", periods=500)
        data = {
            'A': np.random.randn(500),
            'B': np.random.randn(500),
            'C': np.random.randn(500),
            'D': np.random.randn(500),
            'E': np.random.randn(500)
        }
        df = pd.DataFrame(data, index=dates)
        
        lambda1 = compute_lambda1_norm(df, window=50, min_assets=5)
        
        # For random matrix (Marchenko-Pastur), lambda_max is small but > 1/N.
        # 5 assets, random. max eigen value roughly 1 + 2sqrt(N/T)...
        # Just assert it is significantly less than 0.9
        val = lambda1.iloc[-1]
        self.assertTrue(val < 0.6, f"Expected Lambda1 low for random, got {val}")

if __name__ == '__main__':
    unittest.main()
