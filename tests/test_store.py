import unittest
import pandas as pd
import shutil
import tempfile
from pathlib import Path
from src.store import DataStore

class TestDataStore(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.store = DataStore(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_save_and_load(self):
        df = pd.DataFrame({
            'Close': [100, 101, 102]
        }, index=pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']))
        
        self.store.save("TEST", df)
        loaded = self.store.load("TEST")
        
        pd.testing.assert_frame_equal(df, loaded)

    def test_incremental_merge(self):
        # Day 1 data
        df1 = pd.DataFrame({
            'Close': [100, 101]
        }, index=pd.to_datetime(['2023-01-01', '2023-01-02']))
        self.store.save("TEST", df1)
        
        # Day 2 update (overlapping Day 2 + new Day 3)
        df2 = pd.DataFrame({
            'Close': [101, 105]
        }, index=pd.to_datetime(['2023-01-02', '2023-01-03']))
        
        self.store.save("TEST", df2, merge=True)
        
        loaded = self.store.load("TEST")
        
        expected = pd.DataFrame({
            'Close': [100, 101, 105]
        }, index=pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']))
        
        pd.testing.assert_frame_equal(loaded, expected)

if __name__ == '__main__':
    unittest.main()
