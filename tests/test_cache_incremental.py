import unittest
import pandas as pd
import shutil
import os
from pathlib import Path
from src.store import DataStore

class TestCacheIncremental(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_data_cache"
        self.store = DataStore(self.test_dir)
        os.makedirs(self.test_dir, exist_ok=True)
        
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_save_load(self):
        # Create dummy data
        dates = pd.date_range("2023-01-01", periods=5)
        df = pd.DataFrame({'Close': [100, 101, 102, 103, 104]}, index=dates)
        
        ticker = "TEST_TICKER"
        self.store.save(ticker, df)
        
        # Load back
        loaded = self.store.load(ticker)
        # Parquet does not preserve index freq. Check content.
        pd.testing.assert_frame_equal(df.reset_index(drop=True), loaded.reset_index(drop=True))
        
    def test_incremental_update_logic(self):
        # Simulate: We fetch new data and want to verify what we would store.
        # Note: DataStore currently just overwrites ("save"). 
        # The intelligent merge logic is usually in DataLoader or explicit merge.
        # But let's check if saving overwrites correctly.
        
        ticker = "TEST_INC"
        dates1 = pd.date_range("2023-01-01", periods=3)
        df1 = pd.DataFrame({'Close': [10, 11, 12]}, index=dates1)
        self.store.save(ticker, df1)
        
        dates2 = pd.date_range("2023-01-04", periods=2)
        df2 = pd.DataFrame({'Close': [13, 14]}, index=dates2)
        
        # If we "append" manually (as DataLoader would do logically):
        combined = pd.concat([df1, df2])
        self.store.save(ticker, combined)
        
        loaded = self.store.load(ticker)
        self.assertEqual(len(loaded), 5)
        self.assertEqual(loaded.iloc[-1]['Close'], 14)
        
    def test_get_last_date(self):
        dates = pd.date_range("2023-01-01", periods=5)
        df = pd.DataFrame({'Close': [1]*5}, index=dates)
        self.store.save("TEST_DATE", df)
        
        last = self.store.get_last_date("TEST_DATE")
        self.assertEqual(last, dates[-1])

if __name__ == '__main__':
    unittest.main()
