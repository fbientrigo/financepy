import unittest
import json
import datetime
import os
import shutil
from src.transparency.manifest import ManifestManager

class TestManifest(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_manifests"
        self.mgr = ManifestManager(self.test_dir)
        
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    def test_collect_and_save(self):
        config = {"parameters": {"foo": "bar"}, "paths": {"data_cache": "cache"}}
        tickers = ["ABC", "DEF"]
        run_date = datetime.date(2023, 1, 1)
        
        info = self.mgr.collect_run_info(config, tickers, run_date, errors=["Err1"])
        
        self.assertEqual(info['meta']['run_date'], '2023-01-01')
        self.assertEqual(info['inputs']['tickers_count'], 2)
        self.assertEqual(info['quality']['errors_count'], 1)
        
        saved_path = self.mgr.save_manifest(info, run_date)
        
        self.assertTrue(saved_path.exists())
        
        # Load back
        with open(saved_path, 'r') as f:
            loaded = json.load(f)
            
        self.assertEqual(loaded['parameters']['foo'], 'bar')
        
    def test_load(self):
        run_date = datetime.date(2023, 1, 2)
        # Verify empty
        res = self.mgr.load_manifest(run_date)
        self.assertEqual(res, {})

if __name__ == '__main__':
    unittest.main()
