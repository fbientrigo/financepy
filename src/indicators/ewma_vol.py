import pandas as pd
import numpy as np

def compute_ewma_vol(returns: pd.Series, span: int, annualize: bool = True) -> pd.Series:
    """
    Computes EWMA Volatility.
    
    Args:
        returns: Log returns series.
        span: Span for EWMA smoothing (roughly corresponds to N-day moving average).
        annualize: If True, multiply by sqrt(252).
        
    Returns:
        pd.Series: Volatility series.
    """
    # Variance = EWM of squared returns (assuming mean return ~ 0 for daily data, or use var())
    # Standard practice for RiskMetrics: EWM of squared deviations.
    
    # Method 1: Pandas built-in std().ewm() ? No, ewm().std()
    # This centers the mean dynamically.
    vol = returns.ewm(span=span, adjust=False).std()
    
    if annualize:
        vol *= np.sqrt(252)
        
    return vol
