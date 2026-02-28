import pandas as pd
from typing import Dict, Any
from src.indicators.hurst_dfa import rolling_hurst_dfa, prepare_log_returns
from src.indicators.ewma_vol import compute_ewma_vol
import numpy as np

class AdvancedIndicators:
    """
    Calculates advanced features: Hurst, EWMA Vol.
    Market Mode is calculated externally and passed in? 
    Actually, per-ticker indicators can be here. Market Mode is global.
    """
    def __init__(self, config: Dict[str, Any]):
        self.hurst_cfg = config.get('hurst', {})
        self.ewma_cfg = config.get('ewma_vol', {})
        
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        # returns log returns assumed to be present as 'ret_1d' or calculate them
        if 'ret_1d' not in df.columns:
            # Recalculate if missing (should be there from CommonIndicators)
            df['ret_1d'] =  np.log(df['Close'] / df['Close'].shift(1))
            
        # Hurst
        w_hurst = self.hurst_cfg.get('window', 126)
        min_scale = self.hurst_cfg.get('min_scale', 10)
        
        # Ensure stationarity using the official sanitizer
        # Even if ret_1d exists, we re-derive from Close if possible or trust ret_1d?
        # Ideally we trust ret_1d if it's there. 
        # But to be ABSOLUTELY SURE as per audit, let's use the sanitizer on Price if available.
        if 'Close' in df.columns:
             # Re-calculate returns specifically for Hurst to be safe using the official sanitizer
             hurst_input = prepare_log_returns(df['Close'])
             
             # We need to reindex to match df in case of drops
             hurst_series = rolling_hurst_dfa(hurst_input, window=w_hurst, min_scale=min_scale)
             df['hurst_dfa'] = hurst_series.reindex(df.index)
        else:
             # Fallback
             df['hurst_dfa'] = rolling_hurst_dfa(df['ret_1d'], window=w_hurst, min_scale=min_scale)
        
        # EWMA Vol
        span = self.ewma_cfg.get('span', 20)
        df['vol_ewma'] = compute_ewma_vol(df['ret_1d'], span=span, annualize=True)
        
        return df
