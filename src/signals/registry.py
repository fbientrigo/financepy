import pandas as pd
from typing import Protocol, List

class SignalGenerator(Protocol):
    def generate(self, df_features: pd.DataFrame) -> pd.DataFrame:
        """
        Takes features DataFrame (long).
        Returns DataFrame with columns: signal, state, confidence, reasons.
        """
        ...

class SignalRegistry:
    def __init__(self):
        self._generators: List[SignalGenerator] = []

    def register(self, generator: SignalGenerator):
        self._generators.append(generator)

    def apply_all(self, df_features: pd.DataFrame) -> pd.DataFrame:
        # For simplicity, we assume we merge signals or take the last one?
        # Or maybe we apply sequentially and they append columns?
        # Requirement says "signals_long" has specific columns. 
        # So we probably want one main generator or a composition.
        # Let's assume we return a concatenated list of signals or aggregate them.
        # But for 'daily summary', we likely want one authoritative signal set per ticker/day.
        # Let's return the result of the LAST generator for now, allowing overriding.
        df_out = pd.DataFrame(index=df_features.index)
        # Initialize defaults
        df_out['signal'] = 'NONE'
        df_out['state'] = 'NEUTRAL'
        df_out['confidence'] = 0.0
        df_out['reasons'] = [[] for _ in range(len(df_out))]

        for gen in self._generators:
            # We assume generato rreturns a DF aligned with index
            new_signals = gen.generate(df_features)
            # update
            # Ideally we'd merge intelligently (e.g. if one says BUY and other NONE, keep BUY)
            # Simple override for now
            mask = new_signals['signal'] != 'NONE'
            df_out.loc[mask, 'signal'] = new_signals.loc[mask, 'signal']
            df_out.loc[mask, 'state'] = new_signals.loc[mask, 'state']
            df_out.loc[mask, 'confidence'] = new_signals.loc[mask, 'confidence']
            df_out.loc[mask, 'reasons'] = new_signals.loc[mask, 'reasons']
            
            # Also update states even if signal is NONE (e.g. OVERSOLD but no trigger)
            mask_state = new_signals['state'] != 'NEUTRAL'
            df_out.loc[mask_state, 'state'] = new_signals.loc[mask_state, 'state']
            
        return df_out
