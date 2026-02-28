import unittest
import sys
import os

class TestDashboardImport(unittest.TestCase):
    def test_import(self):
        # Add root to sys.path
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        sys.path.append(root)
        
        # Try importing the dashboard modules
        try:
            import src.viz.loader
            import src.viz.panels
            # We don't import app.dashboard because it runs streamlit commands on import (script style)
            # But we can verify the support modules exist and are valid python
        except ImportError as e:
            self.fail(f"Import failed: {e}")

if __name__ == '__main__':
    unittest.main()
