import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
import datetime
import os
import shutil
from run_daily import run_pipeline

class TestPipelineSmoke(unittest.TestCase):
    def setUp(self):
        # Create a temp config/output dir
        self.test_reports = "test_reports"
        self.test_cache = "test_cache"
        os.makedirs(self.test_reports, exist_ok=True)
        os.makedirs(self.test_cache, exist_ok=True)
        
        # Create dummy config
        with open("test_config.yaml", 'w') as f:
            f.write(f"""
tickers:
  - FAKE1
  - FAKE2
parameters:
  zscore_window: 10
  volatility_window_short: 10
  volatility_window_long: 20
  bollinger_window: 10
  bollinger_std: 2.0
  lookback_days: 50
  hurst:
    window: 20
    min_scale: 4
  ewma_vol:
    span: 10
  market_mode:
    window: 10
    min_assets: 2
  risk_off:
    lookback: 20
    percentile_threshold: 0.90
paths:
  data_cache: "{self.test_cache}"
  reports: "{self.test_reports}"
            """)

    def tearDown(self):
        if os.path.exists(self.test_reports):
            shutil.rmtree(self.test_reports)
        if os.path.exists(self.test_cache):
            shutil.rmtree(self.test_cache)
        if os.path.exists("test_config.yaml"):
            os.remove("test_config.yaml")

    @patch('src.data.DataLoader.fetch_and_store')
    @patch('src.store.DataStore.load')
    def test_run_daily_smoke(self, mock_load, mock_fetch):
        # Mock fetch to return success
        mock_fetch.return_value = (2, [])
        
        # Mock load to return random data
        dates = pd.date_range("2023-01-01", periods=100)
        df = pd.DataFrame({
            'Close': np.random.uniform(100, 200, 100),
            'Volume': np.random.randint(1000, 10000, 100)
        }, index=dates)
        
        # Make one ticker highly correlated to another? 
        # mock_load is called for each ticker.
        # We can use side_effect to return different DFs based on ticker
        mock_load.side_effect = lambda ticker: df.copy()
        
        # Run pipeline
        target_date = dates[-1].date()
        report_path = run_pipeline(target_date, "test_config.yaml")
        
        # Check output
        self.assertTrue(os.path.exists(report_path))
        
        # Read report content
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        self.assertIn("Daily Market Summary", content)
        self.assertIn("FAKE1", content)
        # Check if new sections exist
        self.assertIn("Régimen y Riesgo Sistémico", content)

if __name__ == '__main__':
    unittest.main()
