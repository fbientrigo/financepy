import yfinance as yf
import pandas as pd
import datetime
from typing import List, Dict
from .store import DataStore
from .logger_config import get_logger

logger = get_logger(__name__)

class DataLoader:
    def __init__(self, store: DataStore):
        self.store = store

    def fetch_and_store(self, tickers: List[str], target_date: datetime.date = None):
        """
        Fetches data for multiple tickers and updates the cache.
        If target_date is provided, ensures data exists AT LEAST up to that date.
        If target_date is NOT provided, syncs to Today.
        """
        updated_count = 0
        errors = []

        # If no target provided, assume we want up-to-the-minute (Today)
        if target_date is None:
             target_date = datetime.date.today()

        for ticker in tickers:
            try:
                self._update_ticker(ticker, target_date)
                updated_count += 1
            except Exception as e:
                errors.append(f"{ticker}: {str(e)}")
        
        return updated_count, errors

    def _update_ticker(self, ticker: str, target_date: datetime.date):
        last_date_ts = self.store.get_last_date(ticker)
        last_date = last_date_ts.date() if last_date_ts else None
        
        # Check if we already have sufficient data
        if last_date and last_date >= target_date:
            logger.info(f"[{ticker}] Cache up to {last_date} covers target {target_date}. Skipping fetch.")
            return

        # Determine start date
        if last_date:
            # Fetch from last_date. Use overlap to ensure no gaps and correct adj.
            # yfinance logic: start is inclusive.
            start_date = last_date
        else:
            # Default to a reasonable history if no cache
            # Look back 2 years to allow 200d MA + buffer
            start_date = target_date - datetime.timedelta(days=365*2)
            
        # Determine end date
        # yfinance end is EXCLUSIVE. 
        # If we want to include target_date, end must be > target_date.
        # Ideally we fetch up to Today if we are doing a real run, 
        # but if the user asked for a past date, do we STOP at that date?
        # Safe default: Fetch up to max(target_date, today) + 1?
        # Or just fetch up to target_date + 1 to satisfy the requirement?
        # User said: "consider that we always have to look to the past regarding the choosen date"
        # Let's strictly fetch up to target_date + 1 (so we get target_date).
        # This prevents "Fetching future lines" if re-running history.
        
        # BUT wait: if we are filling a gap? e.g. cache is 2023, target is 2025.
        # We need everything in between.
        
        fetch_start = start_date
        fetch_end = target_date + datetime.timedelta(days=1)
        
        # If fetch_end <= fetch_start (which shouldn't happen given the check above), skip
        if fetch_end <= fetch_start:
             return

        logger.info(f"[{ticker}] Fetching from {fetch_start} to {fetch_end} (Target: {target_date})...")
        df = yf.download(ticker, start=str(fetch_start), end=str(fetch_end), auto_adjust=True, progress=False)
        
        if df.empty:
            logger.warning(f"No data found for {ticker} in range {fetch_start} - {fetch_end}")
            return

        # Flatten columns if MultiIndex (common in new yfinance)
        if isinstance(df.columns, pd.MultiIndex):
            # If second level is ticker, drop it
            try:
                df.columns = df.columns.get_level_values(0)
            except:
                pass
        
        # Validation: We strictly need 'Close'

        if 'Close' not in df.columns:
            if 'Adj Close' in df.columns:
                df.rename(columns={'Adj Close': 'Close'}, inplace=True)
            else:
                # Case-insensitive search for any column containing 'close'
                close_cols = [c for c in df.columns if 'close' in c.lower()]
                if close_cols:
                    df.rename(columns={close_cols[0]: 'Close'}, inplace=True)
                else:
                    raise ValueError(f"[{ticker}] Missing Close column. Columns: {list(df.columns)}")
            
        # Standardize columns to standard lower case or keep as is? 
        # Requirement says: A) prices: ... values=AdjClose.
        # Since we used auto_adjust=True, 'Close' IS the adjusted close.
        
        # We only really strictly need 'Close' for now, but keeping OHLCV is good practice.
        self.store.save(ticker, df)

    def load_combined_prices(self, tickers: List[str], start_date: datetime.date = None) -> pd.DataFrame:
        """
        Returns a DataFrame where columns are tickers and values are Close prices.
        Index is Date.
        """
        series_list = {}
        for t in tickers:
            df = self.store.load(t)
            if df is not None and not df.empty:
                # Assuming 'Close' exists. 
                # If yfinance structure changed, might need robust check.
                if 'Close' in df.columns:
                    series_list[t] = df['Close']
                else:
                    # fallback
                    cols = [c for c in df.columns if 'close' in c.lower()]
                    if cols:
                        series_list[t] = df[cols[0]]
        
        if not series_list:
            return pd.DataFrame()

        prices = pd.DataFrame(series_list)
        prices = prices.sort_index()
        prices = prices.ffill()
        
        if start_date:
             prices = prices[prices.index.date >= start_date]
             
        # Drop rows where all are NaN? Or keep aligned?
        # ffill is usually good for prices if holidays differ, 
        # but let's leave that to the feature calculator or return raw.
        # Requirement says 'EOD', assume aligned dates mostly.
        
        return prices
