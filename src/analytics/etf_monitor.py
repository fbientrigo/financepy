import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from ..indicators.hurst_dfa import compute_hurst_dfa, rolling_hurst_dfa, prepare_log_returns
from ..analytics.phase_space import compute_phase_space_trails
from ..data import DataLoader
from ..store import DataStore
import os

class ETFMonitor:
    """
    Backend logic for the Global ETF & Macro-Correlation Module.
    Handles data definitions, fetching (using DataLoader), 
    and specialized analytics (Hurst, Correlation Decoupling, Phase Space).
    """
    
    # 1. Universe Definition (Immutable)
    GLOBAL_ETFS = {
        'SPY': 'USA (S&P 500)',
        'QQQ': 'USA (Nasdaq)',
        'VGK': 'Europe (FTSE)',
        'EEM': 'Emerging Markets',
        'EWZ': 'Brazil',
        'FXI': 'China',
        'EWJ': 'Japan',
        'URTH': 'Global (MSCI World)',
    }
    
    MACRO_ANCHORS = {
        'GLD': 'Gold',
        'USO': 'Oil'
    }
    
    # 2. Macro Metadata (Static GDP Per Capita)
    GDP_METADATA = {
        'SPY': 76000,   'QQQ': 76000,   'VGK': 40000,
        'EEM': 6000,    'EWZ': 9000,    'FXI': 12500,
        'EWJ': 34000,   'URTH': 15000,  'GLD': 0, 'USO': 0
    }

    def __init__(self, cache_dir: str = "data_cache"):
        # Use existing infrastructure
        self.store = DataStore(cache_dir)
        self.loader = DataLoader(self.store)

    def get_basket_tickers(self) -> List[str]:
        return list(self.GLOBAL_ETFS.keys()) + list(self.MACRO_ANCHORS.keys())

    def get_gdp_metadata(self) -> Dict[str, float]:
        return self.GDP_METADATA

    def fetch_data(self, start_date: str, end_date: str = None) -> pd.DataFrame:
        """
        Fetches combined Close prices using DataLoader.
        """
        tickers = self.get_basket_tickers()
        
        target_date = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else datetime.today().date()
        
        # 1. Update Cache
        self.loader.fetch_and_store(tickers, target_date=target_date)
        
        # 2. Load Combined
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        data = self.loader.load_combined_prices(tickers, start_date=start_dt)
        
        return data.ffill().dropna()

    def compute_phase_space_trails(self, prices: pd.DataFrame, analysis_window: int = 252) -> Dict:
        """
        Computes the Phase Space Trails (Comet Plot Data).
        Wraps the shared implementation and adds Region metadata.
        """
        # Call Shared Engine
        results = compute_phase_space_trails(prices, analysis_window=analysis_window, hurst_window=60)
        
        # Enrich with Region
        for ticker, data in results.items():
            results[ticker]['region'] = self.GLOBAL_ETFS.get(ticker, 'Macro')
            
        return results

    def compute_analytics(self, prices: pd.DataFrame, window_corr: int = 60) -> dict:
        """
        Computes all required metrics:
        1. Hurst Exponent (Static / Recent)
        2. Volatility (Annualized)
        3. Rolling Correlations vs GLD/USO
        """
        results = {}
        
        # 1. Log Returns
        # We need to compute log returns for the correlation implementation
        # and simple stationarity for Hurst.
        log_rets = prepare_log_returns(prices)
        
        # 2. Main Metrics (Hurst, Vol)
        # Calculate on the full window provided? Or just recent snapshot?
        # Requirement: "Header: Top 3 Hurst", "Scatter: Hurst vs GDP".
        # This implies a single scalar H per asset for the Scatter/Header.
        # Let's iterate tickers.
        
        summary_stats = []
        
        for ticker in prices.columns:
            # Series
            series = log_rets[ticker].dropna()
            
            if len(series) < 100: # Min data check
                continue
                
            # A. Hurst
            h = compute_hurst_dfa(series, min_scale=10)
            
            # B. Volatility (Annualized)
            vol = series.std() * np.sqrt(252)
            
            gdp = self.GDP_METADATA.get(ticker, 0)
            
            summary_stats.append({
                'Ticker': ticker,
                'Hurst': h,
                'Volatility': vol,
                'GDP': gdp,
                'Region': self.GLOBAL_ETFS.get(ticker, 'Macro')
            })
            
        results['summary'] = pd.DataFrame(summary_stats).set_index('Ticker')
        
        # 3. Rolling Correlations
        # Calculate Rolling Correlation of ALL vs GLD and USO
        # Window: 60 days
        
        correlations = {}
        
        # We need the ROLLIG correlation series for the Drill Down.
        # And maybe the current correlation for the Heatmap? 
        # No, Heatmap is usually Cross-Corr of the WHOLE period or recent window.
        # Prompt: "Heapmap: Correlación cruzada... Rolling Correlation: ... de cada ETF vs GLD/USO"
        
        # Let's compute the full rolling correlation dataframe for the Drill Down
        for anchor in ['GLD', 'USO']:
            if anchor not in log_rets.columns:
                continue
                
            anchor_ret = log_rets[anchor]
            
            # Compute rolling corr for every other col against anchor
            # pairwise
            
            corr_df = log_rets.rolling(window=window_corr).corr(anchor_ret)
            # This returns a DataFrame where each col is Corr(Col, Anchor)
            
            correlations[anchor] = corr_df
            
        results['rolling_corr'] = correlations
        
        # 4. Cross Correlation Matrix (All vs All) - Recent Window (e.g. last 60d or full)
        # Using full provided period for the heatmap can vary, let's use full
        results['corr_matrix'] = log_rets.corr()
        
        return results

    def check_decoupling(self, current_corr: float, threshold: float = 0.2) -> str:
        """
        Classifies the correlation state.
        """
        if current_corr < 0:
            return "Decoupled (Inverse)"
        elif current_corr < threshold:
            return "Decoupled (Uncorrelated)"
        else:
            return "Coupled"
