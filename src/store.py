import pandas as pd
import os
from pathlib import Path
from typing import Optional
from .logger_config import get_logger

logger = get_logger(__name__)

class DataStore:
    def __init__(self, cache_dir: str):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, ticker: str) -> Path:
        # Sanitize ticker for filename (e.g., USDCLP=X -> USDCLP_X)
        clean_ticker = ticker.replace("=", "_").replace("^", "")
        return self.cache_dir / f"{clean_ticker}.parquet"

    def load(self, ticker: str) -> Optional[pd.DataFrame]:
        path = self._get_path(ticker)
        if not path.exists():
            return None
        try:
            df = pd.read_parquet(path)
            # Ensure index is DatetimeIndex
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)
            return df.sort_index()
        except Exception as e:
            logger.warning(f"Failed to load cache for {ticker}: {e}")
            return None

    def save(self, ticker: str, df: pd.DataFrame, merge: bool = True):
        if df is None or df.empty:
            return

        path = self._get_path(ticker)
        
        # Ensure index is clean
        df = df.sort_index()
        # Remove duplicates in new data just in case
        df = df[~df.index.duplicated(keep='last')]

        if merge and path.exists():
            existing_df = self.load(ticker)
            if existing_df is not None:
                # Combine and drop duplicates, preferring new data? 
                # Actually, usually new data is more up to date.
                # combine_first prefers the caller, so let's use standard concat + drop_duplicates
                combined = pd.concat([existing_df, df])
                combined = combined[~combined.index.duplicated(keep='last')]
                combined = combined.sort_index()
                df = combined

        try:
            df.to_parquet(path)
        except Exception as e:
            logger.error(f"Error saving cache for {ticker}: {e}")

    def get_last_date(self, ticker: str):
        df = self.load(ticker)
        if df is None or df.empty:
            return None
        return df.index[-1]
