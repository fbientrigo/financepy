import pytest
import pandas as pd
import numpy as np
import sys
import os

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Expecting the module to be created here
from src.analytics.phase_space import compute_phase_space_trails

class TestPhaseSpaceEngine:
    
    def test_compute_trails_structure(self):
        """Test that the function returns the correct dictionary structure."""
        # Synthetic Data
        dates = pd.date_range("2020-01-01", periods=200)
        prices = pd.DataFrame({
            'AssetA': 100 + np.cumsum(np.random.normal(0, 1, 200)),
            'AssetB': 50 + np.cumsum(np.random.normal(0, 0.5, 200))
        }, index=dates)
        
        trails = compute_phase_space_trails(prices, analysis_window=100, hurst_window=30)
        
        assert isinstance(trails, dict)
        assert 'AssetA' in trails
        assert 'AssetB' in trails
        
        # Check content keys
        keys = ['hurst_history', 'return_history', 'current_hurst', 'current_return', 'current_vol']
        for k in keys:
            assert k in trails['AssetA']
            
    def test_trail_length(self):
        """Test that history length is correct (default 10)."""
        dates = pd.date_range("2020-01-01", periods=200)
        prices = pd.DataFrame({'A': np.arange(200)}, index=dates)
        
        trails = compute_phase_space_trails(prices, analysis_window=100, hurst_window=20)
        
        trail_len = len(trails['A']['hurst_history'])
        assert trail_len == 10, f"Expected trail length 10, got {trail_len}"
        
    def test_insufficient_data_handling(self):
        """Test that assets with insufficient history are skipped."""
        dates = pd.date_range("2020-01-01", periods=50) # Too short for 60d window
        prices = pd.DataFrame({'Short': np.arange(50)}, index=dates)
        
        trails = compute_phase_space_trails(prices, analysis_window=50, hurst_window=60)
        
        assert 'Short' not in trails
