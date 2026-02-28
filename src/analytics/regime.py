import pandas as pd
import numpy as np

def label_regime(hurst: pd.Series, hi: float = 0.55, lo: float = 0.45) -> pd.Series:
    """
    Labels the regime based on Hurst Exponent.
    
    Args:
        hurst: Series of Rolling Hurst exponents.
        hi: Threshold for TRENDING regime (H > hi).
        lo: Threshold for MEAN_REVERSION regime (H < lo).
        
    Returns:
        pd.Series: String labels ['TREND', 'MEAN_REVERT', 'UNCLEAR', 'NaN']
    """
    labels = pd.Series(index=hurst.index, data='UNCLEAR')
    
    # Handle NaNs first
    labels[hurst.isna()] = 'NaN' # or keep Unclear? Let's be explicit
    
    # Trend
    labels[hurst > hi] = 'TREND'
    
    # Mean Reversion
    labels[hurst < lo] = 'MEAN_REVERT'
    
    return labels
