import pandas as pd
import numpy as np
from typing import Dict
from ..indicators.hurst_dfa import rolling_hurst_dfa, prepare_log_returns

def compute_phase_space_trails(
    prices: pd.DataFrame, 
    analysis_window: int = 252, 
    hurst_window: int = 60
) -> Dict:
    """
    Computes the Phase Space Trails (Comet Plot Data) for a given set of prices.
    
    This function is generic and reusable for any basket of assets (ETFs or Stocks).
    
    Parameters
    ----------
    prices : pd.DataFrame
        Adjusted close prices.
    analysis_window : int
        The lookback period (N points) from the end of the series to analyze.
        Defaults to 252.
    hurst_window : int
        The window size for the Rolling Hurst and Rolling Return calculation.
        Defaults to 60.
        
    Returns
    -------
    Dict[Ticker, Dict]
        Dictionary where keys are tickers and values contain:
        - 'hurst_history': list (last 10 points)
        - 'return_history': list (last 10 points)
        - 'current_hurst': float
        - 'current_return': float
        - 'current_vol': float
    """
    results = {}
    
    # 1. Log Returns
    log_rets = prepare_log_returns(prices)
    
    # 2. Slice to Analysis Window (Lookback from END)
    if len(log_rets) > analysis_window:
        log_rets_view = log_rets.iloc[-analysis_window:]
    else:
        log_rets_view = log_rets
        
    for ticker in prices.columns:
        series = log_rets_view[ticker].dropna()
        
        # Determine strict minimum length
        # Need window for Hurst + at least 1 point for result + buffer for trail
        if len(series) < hurst_window + 10:
            continue
        
        # 3. Rolling Metrics
        
        # A. Rolling Hurst
        # Uses hurst.py's implementation
        roll_hurst = rolling_hurst_dfa(series, window=hurst_window, min_scale=10)
        
        # B. Rolling Return (CAGR/Yield of that window)
        # Simple sum of log returns in window = Total Log Return in window
        roll_ret = series.rolling(window=hurst_window).sum() 
        
        # C. Rolling Volatility (for bubble size)
        roll_vol = series.rolling(window=hurst_window).std() * np.sqrt(252)
        
        # 4. Extract Trails (Last 10 valid points)
        # Combine into DF to drop NaNs together (handling start of rolling window)
        df_metrics = pd.DataFrame({
            'H': roll_hurst,
            'R': roll_ret,
            'V': roll_vol
        }).dropna()
        
        if len(df_metrics) == 0:
            continue
            
        trail_len = 10
        trail = df_metrics.iloc[-trail_len:]
        
        results[ticker] = {
            'hurst_history': trail['H'].tolist(),
            'return_history': trail['R'].tolist(),
            'current_hurst': trail['H'].iloc[-1],
            'current_return': trail['R'].iloc[-1],
            'current_vol': trail['V'].iloc[-1]
            # No 'region' here, caller must add it if needed
        }
        
    return results
