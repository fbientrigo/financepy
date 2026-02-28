import unittest
import pandas as pd
import numpy as np
from src.viz.panels_system import panel_regime, panel_risk, panel_market_mode
from src.viz.panels_corr import panel_correlation_heatmap
import plotly.graph_objects as go

class TestVizPanels(unittest.TestCase):
    def setUp(self):
        # Create dummy data
        dates = pd.date_range("2023-01-01", periods=20)
        self.df = pd.DataFrame({
            'Close': np.random.rand(20) * 100,
            'regime_label': ['TREND']*10 + ['MEAN_REVERT']*10,
            'vol_ewma': np.random.rand(20),
            'risk_off_flag': [False]*19 + [True]
        }, index=dates)
        
    def test_regime_panel(self):
        fig = panel_regime(self.df, "TEST")
        self.assertIsInstance(fig, go.Figure)
        
    def test_risk_panel(self):
        fig = panel_risk(self.df)
        self.assertIsInstance(fig, go.Figure)
        
    def test_market_mode_panel(self):
        s = pd.Series(np.random.rand(20), index=self.df.index)
        fig = panel_market_mode(s)
        self.assertIsInstance(fig, go.Figure)
        
    def test_corr_panel(self):
        # returns matrix
        df_ret = pd.DataFrame({
            'A': np.random.randn(20),
            'B': np.random.randn(20)
        }, index=self.df.index)
        fig = panel_correlation_heatmap(df_ret, window=10)
        self.assertIsInstance(fig, go.Figure)

if __name__ == '__main__':
    unittest.main()
