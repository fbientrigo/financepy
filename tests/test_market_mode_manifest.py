import unittest
import pandas as pd
import numpy as np
from src.indicators.market_mode import compute_market_mode_details

class TestMarketModeTransparency(unittest.TestCase):
    def test_compute_details(self):
        # Create synthetic returns
        date_rng = pd.date_range("2023-01-01", periods=100)
        
        # Highly correlated
        r1 = np.random.normal(0, 0.01, 100)
        r2 = r1 + np.random.normal(0, 0.001, 100)
        r3 = r1 + np.random.normal(0, 0.001, 100)
        # Uncorrelated
        r4 = np.random.normal(0, 0.01, 100)
        
        df = pd.DataFrame({
            'A': r1, 'B': r2, 'C': r3, 'D': r4
        }, index=date_rng)
        
        # Missing data in D (last 10 days)
        df.loc[date_rng[-10]:, 'D'] = np.nan
        
        target = date_rng[50] # Day 50
        
        details = compute_market_mode_details(df, target, window=20, min_assets=2)
        
        # Check keys
        self.assertIn('meta', details)
        self.assertIn('metrics', details)
        self.assertIn('assets', details)
        self.assertIn('eigenvalues', details)
        self.assertIn('eigenvector_1', details)
        
        # Check Meta
        self.assertEqual(details['meta']['window_days'], 20)
        self.assertEqual(details['meta']['n_obs_window'], 20)
        self.assertEqual(details['meta']['n_assets_effective'], 4)
        
        # Check Assets
        assets = { item['ticker']: item for item in details['assets'] }
        self.assertTrue(assets['A']['used'])
        self.assertTrue(assets['D']['used'])
        self.assertEqual(assets['D']['missing_pct'], 0.0) # at day 50, D is full
        
        # Check Eigenvalues (Top 5)
        eigs = details['eigenvalues']
        self.assertTrue(len(eigs) <= 5)
        self.assertGreater(eigs[0]['value'], eigs[1]['value']) # Sorted
        
        # Check Eigenvector
        vecs = details['eigenvector_1']
        self.assertEqual(len(vecs), 4)
        weights = { item['ticker']: item['weight'] for item in vecs }
        
        # A, B, C should have similar weights (correlated)
        # W_A = weights['A']
        # W_B = weights['B']
        # self.assertAlmostEqual(abs(W_A), abs(W_B), delta=0.2)
        
    def test_missing_asset_dropped(self):
        date_rng = pd.date_range("2023-01-01", periods=50)
        df = pd.DataFrame(np.random.randn(50, 4), columns=['A','B','C','D'], index=date_rng)
        
        # D is missing 80% of data in window
        df.iloc[-18:, 3] = np.nan # D column
        
        target = date_rng[-1] 
        details = compute_market_mode_details(df, target, window=20, min_assets=2)
        
        assets = { item['ticker']: item for item in details['assets'] }
        self.assertFalse(assets['D']['used'])
        self.assertIn("Too many NaNs", assets['D']['reason'])
        self.assertEqual(details['meta']['n_assets_effective'], 3)
        
        # Eigenvector should NOT contain D
        vecs = details['eigenvector_1']
        found_d = any(v['ticker'] == 'D' for v in vecs)
        self.assertFalse(found_d)

if __name__ == '__main__':
    unittest.main()
