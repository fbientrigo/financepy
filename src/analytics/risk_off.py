import pandas as pd
import numpy as np

def compute_risk_off(vol_ewma: pd.Series, lambda1_norm: pd.Series, lookback: int = 252, pctl: float = 0.90) -> pd.Series:
    """
    Computes a Risk-Off flag based on Volatility and Systemic Correlation (Lambda1).
    
    Logic:
    - If Volatility is in the top decile (historic lookback) OR
    - If Lambda1 is in the top decile (historic lookback)
    => RISK_OFF = True
    
    Args:
        vol_ewma: EWMA Volatility series.
        lambda1_norm: Systemic correlation series.
        lookback: Rolling window to compute percentiles (e.g., 1 year).
        pctl: Percentile threshold (0.90 = Top 10%).
        
    Returns:
        pd.Series: Boolean flag (True = Risk Off).
    """
    # We need to handle them independently or combined?
    # User requirement: "derivado de percentiles de vol_ewma y lambda1_norm"
    # Let's flag if EITHER is extreme? Or weighted?
    # Simple robust approach: Union of extremes.
    
    # Compute rolling quantile
    # Note: rolling quantile can be slow for large windows.
    # Optimization: rank(pct=True)? 
    # But rank() is expanding or full sample? We want rolling lookback.
    
    # Using rolling quantile
    vol_thresh = vol_ewma.rolling(window=lookback, min_periods=lookback//2).quantile(pctl)
    lambda_thresh = lambda1_norm.rolling(window=lookback, min_periods=lookback//2).quantile(pctl)
    
    risk_off = (vol_ewma > vol_thresh) | (lambda1_norm > lambda_thresh)
    
    return risk_off.fillna(False)
