"""
tests/test_optimization.py
--------------------------
TDD - Tests for Portfolio Optimization Engine
"""

import unittest
import pandas as pd
import numpy as np
from src.optimization.strategies.mc_sharpe import MonteCarloSharpeOptimizer

class TestMonteCarloOptimizer(unittest.TestCase):
    
    def setUp(self):
        # Create a dummy DataFrame of prices for 3 assets over 100 days
        dates = pd.date_range("2023-01-01", periods=100)
        np.random.seed(42)
        # Generate random walk prices
        prices_a = np.cumprod(1 + np.random.normal(0.001, 0.02, 100)) * 100
        prices_b = np.cumprod(1 + np.random.normal(0.0005, 0.01, 100)) * 50
        prices_c = np.cumprod(1 + np.random.normal(0.002, 0.03, 100)) * 10
        
        self.prices_df = pd.DataFrame({
            "ASSET_A": prices_a,
            "ASSET_B": prices_b,
            "ASSET_C": prices_c
        }, index=dates)

    def test_mc_optimizer_returns_valid_weights(self):
        """
        Verify that the generator indeed produces weights that sum to 1.0
        and returns a valid dictionary mapping tickers to weights.
        """
        # Given an optimizer with a small number of simulations for speed
        optimizer = MonteCarloSharpeOptimizer(num_simulations=100, risk_free_rate=0.04)
        
        # When optimizing
        weights = optimizer.optimize(self.prices_df)
        
        # Then it returns a dictionary format
        self.assertIsInstance(weights, dict)
        
        # It contains all the tickers from the input dataframe
        for ticker in self.prices_df.columns:
            self.assertIn(ticker, weights)
            
        # The weights must sum to 1.0 (allowing for floating point precision)
        total_weight = sum(weights.values())
        self.assertAlmostEqual(total_weight, 1.0, places=5)
        
        # All weights should be non-negative (long-only strategy by default for basic MC)
        for w in weights.values():
            self.assertTrue(w >= 0.0)

    def test_mc_optimizer_handles_different_risk_free_rates(self):
        """Verify that it runs with different risk free parametrizations."""
        opt1 = MonteCarloSharpeOptimizer(num_simulations=50, risk_free_rate=0.0)
        opt2 = MonteCarloSharpeOptimizer(num_simulations=50, risk_free_rate=0.05)
        
        # Should not crash and might yield different weights
        w1 = opt1.optimize(self.prices_df)
        w2 = opt2.optimize(self.prices_df)
        
        self.assertAlmostEqual(sum(w1.values()), 1.0, places=5)
        self.assertAlmostEqual(sum(w2.values()), 1.0, places=5)

if __name__ == "__main__":
    unittest.main()
