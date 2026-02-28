import pandas as pd
import numpy as np

class CommonIndicators:
    """
    Calculates the 'base set' of features as required:
    returns, vol, Bollinger/z
    """
    def __init__(self, config: dict):
        self.zscore_window = config.get('zscore_window', 20)
        self.vol_window_short = config.get('volatility_window_short', 20)
        self.vol_window_long = config.get('volatility_window_long', 60)
        self.bb_window = config.get('bollinger_window', 20)
        self.bb_std = config.get('bollinger_std', 2.0)

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        # Expects index=Date, columns include 'Close' (or handled inside)
        if 'Close' not in df.columns:
            # Fallback if case mismatch
            raise ValueError("DataFrame must contain 'Close' column")

        close = df['Close']

        # Returns
        df['ret_1d'] = np.log(close / close.shift(1))
        df['ret_5d'] = np.log(close / close.shift(5))
        df['ret_20d'] = np.log(close / close.shift(20))

        # Volatility (Annualized assuming 252 days)
        # vol = std_dev of log_returns * sqrt(252)
        df['vol_20d'] = df['ret_1d'].rolling(window=self.vol_window_short).std() * np.sqrt(252)
        df['vol_60d'] = df['ret_1d'].rolling(window=self.vol_window_long).std() * np.sqrt(252)

        # Bollinger Bands
        # MB = SMA(Close, N)
        # UP = MB + k * std
        # DN = MB - k * std
        mb = close.rolling(window=self.bb_window).mean()
        std = close.rolling(window=self.bb_window).std()
        
        df['bb_mid'] = mb
        df['bb_upper'] = mb + (self.bb_std * std)
        df['bb_lower'] = mb - (self.bb_std * std)

        # Z-Score (Price relative to Bollinger bands style or just MA)
        # Definition: (Close - Mean) / Std
        # Use epsilon to avoid div by zero
        df['zscore'] = (close - mb) / (std.replace(0, np.nan))

        return df
