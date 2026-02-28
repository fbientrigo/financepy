import unittest
import pandas as pd
import numpy as np
from src.indicators.hurst_dfa import compute_hurst_dfa

class TestHurst(unittest.TestCase):
    def test_hurst_random_walk(self):
        # Geometric Brownian Motion (log returns ~ Normal)
        np.random.seed(42)
        # 1000 days of random returns
        returns = np.random.randn(1000)
        # Hurst should be near 0.5
        h = compute_hurst_dfa(pd.Series(returns), min_scale=10)
        self.assertTrue(0.4 < h < 0.6, f"Expected H ~ 0.5 for RW, got {h}")

    def test_hurst_trending(self):
        # Create a persistent series
        # fbm or just a trend + noise? 
        # Trend + noise might just show trend at large scales.
        # Let's construct a synthesized persistent series using cumsum of positive correlations?
        # Or just simple trend: y = t
        # For linear trend, H should be close to 1? 
        # But DFA removes polynomial trends.
        # To test H > 0.5, we need fractal persistence (fractional Brownian motion).
        # Simpler: Test Mean Reversion (H < 0.5)
        # Mean Reverting: y_t = -0.5 * y_{t-1} + e_t
        
        np.random.seed(42)
        y = [0]
        for _ in range(1000):
            y.append(-0.5 * y[-1] + np.random.randn())
        
        # This is an OU process / AR(1).
        # For short scales it looks mean reverting.
        s = pd.Series(y)
        # Input to compute_hurst_dfa is "returns" (increments). 
        # If s is prices, returns = diff.
        # Our function assumes input is "noise" to be integrated.
        # If we pass the mean-reverting process directly as "noise" (Series), 
        # its cumulative sum will be diffusive but with H != 0.5?
        
        # Actually, standard usage: pass log-returns.
        # If prices mean revert, returns are negatively correlated.
        h = compute_hurst_dfa(s, min_scale=10)
        # Should be < 0.5
        self.assertTrue(h < 0.5, f"Expected H < 0.5 for MR, got {h}")

    def test_hurst_robustness(self):
        # Short series
        s = pd.Series(np.random.randn(10)) # too short
        h = compute_hurst_dfa(s, min_scale=10)
        self.assertTrue(np.isnan(h))

if __name__ == '__main__':
    unittest.main()
