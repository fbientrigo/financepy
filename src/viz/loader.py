import pandas as pd
import yaml
from pathlib import Path
from src.store import DataStore
from src.indicators.registry import IndicatorRegistry
from src.indicators.common import CommonIndicators
from src.indicators.advanced import AdvancedIndicators
from src.indicators.market_mode import compute_lambda1_norm
import numpy as np

class DashboardLoader:
    def __init__(self, config_path: str = "configs/config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.store = DataStore(self.config['paths']['data_cache'])
        if 'universes' in self.config:
            self.tickers = []
            for group in self.config['universes'].values():
                if isinstance(group, list):
                    self.tickers.extend(group)
        else:
             self.tickers = self.config.get('tickers', [])
        self.params = self.config['parameters']

    def load_ticker(self, ticker: str) -> pd.DataFrame:
        """
        Loads raw data for a ticker and enriches it with indicators.
        On-the-fly calculation ensures consistency with pipeline.
        """
        df = self.store.load(ticker)
        if df is None:
            return pd.DataFrame() # Return empty if not found
            
        # Apply Indicators
        registry = IndicatorRegistry()
        registry.register(CommonIndicators(self.params))
        registry.register(AdvancedIndicators(self.params))
        
        df_enriched = registry.apply_all(df)
        return df_enriched

    def get_available_tickers(self):
        """Returns list of tickers present in cache"""
        # Instead of just config tickers, check what's actually in cache?
        # Robustness: prefer config tickers but filter by existence.
        available = []
        for t in self.tickers:
            if self.store.load(t) is not None:
                available.append(t)
        return available

    def load_universe_returns(self) -> pd.DataFrame:
        """
        Loads returns for all available tickers.
        Returns DataFrame (index=Date, columns=Tickers).
        """
        tickers = self.get_available_tickers()
        returns_map = {}
        for t in tickers:
            df = self.store.load(t)
            if df is not None and not df.empty and 'Close' in df.columns:
                # Log returns
                returns_map[t] = np.log(df['Close'] / df['Close'].shift(1))
        
        if not returns_map:
            return pd.DataFrame()
            
        universe_df = pd.DataFrame(returns_map)
        return universe_df

    def compute_global_market_mode(self, universe_returns: pd.DataFrame = None) -> pd.Series:
        """
        Computes Market Mode (Lambda1). 
        If universe_returns is None, loads it.
        """
        if universe_returns is None:
            universe_returns = self.load_universe_returns()
            
        if universe_returns.empty:
            return pd.Series(dtype=float)
            
        mm_cfg = self.params.get('market_mode', {})
        lambda1 = compute_lambda1_norm(
            universe_returns, 
            window=mm_cfg.get('window', 20), 
            min_assets=mm_cfg.get('min_assets', 3)
        )
        return lambda1
