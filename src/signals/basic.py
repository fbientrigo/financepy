import pandas as pd
import numpy as np
import json

class BasicSignals:
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.policy = self.config.get('signal_policy', {})
        
    def generate(self, df: pd.DataFrame) -> pd.DataFrame:
        # Expects: zscore, risk_off_flag, regime_label
        if 'zscore' not in df.columns:
            return pd.DataFrame(index=df.index, columns=['signal', 'state', 'confidence', 'reasons'])
            
        risk_off_action = self.policy.get('risk_off_action', 'degrade')

        out = pd.DataFrame(index=df.index)
        out['signal'] = 'NONE'
        out['state'] = 'NEUTRAL'
        out['confidence'] = 0.0
        # Initialize reasons as empty lists
        out['reasons'] = [[] for _ in range(len(out))]

        z = df['zscore']
        
        # Logic:
        # Z < -2 => Oversold
        # Z > 2 => Overbought
        # Z < -2.5 => BUY_ALERT (Mean reversion)
        # Z > 2.5 => SELL_ALERT
        
        # Vectorized approach is tricky with list columns for reasons, use iteration for reasons or mapped apply
        
        # States
        out.loc[z < -2.0, 'state'] = 'OVERSOLD'
        out.loc[z > 2.0, 'state'] = 'OVERBOUGHT'

        # Signals
        buy_mask = z < -2.0
        sell_mask = z > 2.0
        
        out.loc[buy_mask, 'signal'] = 'BUY_ALERT'
        out.loc[sell_mask, 'signal'] = 'SELL_ALERT'
        
        # Confidence logic
        # If |z| = 2 -> 0.5, |z| = 4 -> 1.0
        out.loc[buy_mask | sell_mask, 'confidence'] = (z.abs() / 4.0).clip(upper=1.0)

        # --- REGIME & RISK OFF FILTERS ---
        if 'risk_off_flag' in df.columns:
            ro_mask = df['risk_off_flag'].fillna(False).astype(bool)
            if ro_mask.any():
                if risk_off_action == 'block':
                     # Force to NONE
                     out.loc[ro_mask, 'signal'] = 'NONE'
                     out.loc[ro_mask, 'confidence'] = 0.0
                else: # degrade
                     out.loc[ro_mask, 'confidence'] *= 0.5
        
        # MEAN REVERSION Checks
        # If Regime is TREND, Z-Score mean reversion signals are dangerous -> Degrade
        if 'regime_label' in df.columns:
            trend_mask = df['regime_label'] == 'TREND'
            mr_signals = (out['signal'].isin(['BUY_ALERT', 'SELL_ALERT']))
            
            # Degrade MR signals in Trend
            target = trend_mask & mr_signals
            out.loc[target, 'confidence'] *= 0.5
            
            # Boost MR signals in Mean Revert
            mr_regime_mask = df['regime_label'] == 'MEAN_REVERT'
            boost = mr_regime_mask & mr_signals
            out.loc[boost, 'confidence'] = (out.loc[boost, 'confidence'] * 1.2).clip(upper=1.0)

        # Reasons
        # We need to fill the list.
        reasons_list = []
        # Safely access zscore series
        z_series = df['zscore']
        
        # Need to iterate by index integer to access filtering columns row by row efficiently
        # Or use iteritem on df... slow but safe.
        for i in range(len(df)):
             val = z_series.iloc[i]
             r = []
             # ensure val is scalar, though series iteration usually yields scalars
             if pd.isna(val):
                 reasons_list.append(r)
                 continue
                 
             if val < -2.0:
                 r.append(f"Z-Score {val:.2f} < -2.0 (Oversold)")
             elif val > 2.0:
                 r.append(f"Z-Score {val:.2f} > 2.0 (Overbought)")
                 
             # Add context info
             if 'regime_label' in df.columns and pd.notna(df.iloc[i]['regime_label']):
                 reg = df.iloc[i]['regime_label']
                 if reg != 'UNCLEAR':
                     r.append(f"Regime: {reg}")
             
             if 'risk_off_flag' in df.columns and df.iloc[i]['risk_off_flag']:
                 r.append("RISK OFF detected")
                 
             reasons_list.append(r)
            
        out['reasons'] = reasons_list

        return out


