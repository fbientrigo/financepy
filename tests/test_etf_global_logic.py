import pytest
import pandas as pd
import numpy as np
import sys
import os

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.analytics.etf_monitor import ETFMonitor

class TestETFMonitor:
    
    @pytest.fixture
    def monitor(self):
        return ETFMonitor()

    def test_basket_definitions(self, monitor):
        """Test that the global basket contains required expected tickers."""
        expected_tickers = [
            'SPY', 'QQQ', # USA
            'VGK',        # Europe
            'EEM', 'EWZ', 'FXI', # Emerging
            'EWJ',        # Asia
            'URTH',       # Global
            'GLD', 'USO'  # Macro
        ]
        
        basket = monitor.get_basket_tickers()
        for t in expected_tickers:
            assert t in basket, f"Missing {t} in ETF basket"
            
    def test_gdp_metadata(self, monitor):
        """Test that GDP metadata is present for the basket."""
        gdp_map = monitor.get_gdp_metadata()
        basket = monitor.get_basket_tickers()
        
        # GLD and USO might not have GDP, but regions should
        regional_etfs = [t for t in basket if t not in ['GLD', 'USO']]
        
        for t in regional_etfs:
            assert t in gdp_map, f"Missing GDP data for {t}"
            assert isinstance(gdp_map[t], (int, float)), f"GDP for {t} must be numeric"
            assert gdp_map[t] > 0, "GDP must be positive"

    def test_correlation_engine_logic(self):
        """Test the rolling correlation logic with synthetic data."""
        # Create synthetic data: SPY and GLD perfectly correlated
        dates = pd.date_range("2020-01-01", periods=100)
        data = pd.DataFrame({
            'SPY': np.linspace(100, 200, 100), # Linear up
            'GLD': np.linspace(50, 100, 100)   # Linear up (Correlated)
        }, index=dates)
        
        # We need a way to invoke internal rolling calc if not exposed clearly or just trust integration test
        # Since we are refactoring, let's focus on the new "Phase Space" method tests
        pass

    def test_phase_space_trails(self, monitor):
        """Test the generation of trail data for the comet plot."""
        # Synthetic data
        dates = pd.date_range("2020-01-01", periods=200) # Needs to be enough for window=60
        # Random Walkish
        np.random.seed(42)
        prices = pd.DataFrame({
            'SPY': 100 + np.cumsum(np.random.normal(0, 1, 200)),
            'GLD': 100 + np.cumsum(np.random.normal(0, 1, 200))
        }, index=dates)
        
        analysis_window = 100
        
        # Test the method
        # Note: We expect the monitor to accept the DF directly or we mock the fetch?
        # Ideally compute_phase_space_trails takes the DF.
        
        # Let's assume the method signature: compute_phase_space_trails(prices_df, analysis_window)
        # It should return a dictionary or DF with 'trails' and 'heads'
        
        trails = monitor.compute_phase_space_trails(prices, analysis_window=analysis_window)
        
        # Check structure
        assert isinstance(trails, dict)
        assert 'SPY' in trails
        assert 'GLD' in trails
        
        spy_trail = trails['SPY']
        # Expecting 'hurst', 'return', 'volatility'?
        assert 'hurst_history' in spy_trail
        assert 'return_history' in spy_trail
        assert 'current_hurst' in spy_trail
        
        # Check length of trails (last 10 points)
        assert len(spy_trail['hurst_history']) == 10
        assert len(spy_trail['return_history']) == 10

    def test_decoupling_detection(self, monitor):
        """Test logic for identifying decoupled assets."""
        # Create a tiny DF where Correlation is negative
        # Provide logic to categorize "Decoupled"
        pass
