"""
src/portfolio_manager.py
------------------------
Data Access Layer (DAL) for portfolio.db (SQLite).

Public API:
  - get_active_holdings(db_path) -> pd.DataFrame
  - get_portfolio_tickers(db_path) -> list[str]

Design invariants:
  - Never raises if the DB file does not exist; returns empty results.
  - Each function opens and closes its own connection (no global state).
  - Only exposes DataFrames; no raw SQL or connection objects leak to callers.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

try:
    from src.data import DataLoader
    from src.optimization.base import PortfolioOptimizer
except ImportError:
    pass  # For tests that mock the structure


# ---------------------------------------------------------------------------
# SQL
# ---------------------------------------------------------------------------

_HOLDINGS_QUERY = """
    SELECT
        ticker,
        usd_amount,
        MAX(timestamp) AS last_updated
    FROM holdings
    GROUP BY ticker
    HAVING usd_amount > 0
    ORDER BY usd_amount DESC
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_active_holdings(db_path: str) -> pd.DataFrame:
    """
    Return the current portfolio snapshot: one row per ticker, the record with
    MAX(timestamp) wins. Tickers with usd_amount == 0 are excluded.

    Columns: ['ticker', 'usd_amount', 'last_updated']

    Returns an empty DataFrame if the database file does not exist.
    """
    if not Path(db_path).exists():
        return pd.DataFrame(columns=["ticker", "usd_amount", "last_updated"])

    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(_HOLDINGS_QUERY, conn)
    except Exception:
        return pd.DataFrame(columns=["ticker", "usd_amount", "last_updated"])
    finally:
        conn.close()

    return df


def get_portfolio_tickers(db_path: str) -> list[str]:
    """
    Return the list of active ticker symbols from the portfolio.

    This is a convenience wrapper over ``get_active_holdings``:
    it extracts and returns the 'ticker' column as a plain Python list.

    Returns an empty list if the database file does not exist.
    """
    df = get_active_holdings(db_path)
    if df.empty:
        return []
    return df["ticker"].tolist()


def compute_rebalance_orders(
    db_path: str,
    data_loader: 'DataLoader',
    optimizer: 'PortfolioOptimizer',
    target_total_usd: float = None
) -> pd.DataFrame:
    """
    Computes rebalancing orders (in USD) to transition from the current portfolio
    to the optimal target portfolio.

    Args:
        db_path: Path to portfolio.db SQLite database.
        data_loader: Instance of DataLoader to fetch historical prices.
        optimizer: Instance of a PortfolioOptimizer strategy.
        target_total_usd: The desired total portfolio value after rebalancing. 
                          If None, it uses the current total USD value of the portfolio.

    Returns:
        pd.DataFrame with columns:
        ['ticker', 'current_usd', 'target_weight', 'target_usd', 'delta_usd']
    """
    # 1. Fetch current portfolio
    current_holdings = get_active_holdings(db_path)
    
    # Extract current total and active tickers
    if current_holdings.empty:
        current_total = 0.0
        current_tickers = []
    else:
        current_total = current_holdings["usd_amount"].sum()
        current_tickers = current_holdings["ticker"].tolist()

    # Determine total pool of money to allocate
    total_pool = target_total_usd if target_total_usd is not None else current_total
    
    if total_pool <= 0:
        return pd.DataFrame(columns=['ticker', 'current_usd', 'target_weight', 'target_usd', 'delta_usd'])

    # 2. Fetch Historical Prices for optimization
    # (Assuming we optimize across all currently held assets, though a real system 
    # might inject a broader target universe here).
    if not current_tickers:
        return pd.DataFrame()
        
    prices_df = data_loader.load_combined_prices(current_tickers)
    
    if prices_df.empty:
        raise ValueError("No historical price data available to perform optimization.")

    # 3. Optimize Portfolio
    optimal_weights = optimizer.optimize(prices_df)

    # 4. Calculate Deltas
    # Prepare current state map
    current_map = dict(zip(current_holdings["ticker"], current_holdings["usd_amount"])) if not current_holdings.empty else {}
    
    orders = []
    for ticker, weight in optimal_weights.items():
        curr_usd = current_map.get(ticker, 0.0)
        target_usd = total_pool * weight
        delta = target_usd - curr_usd
        
        orders.append({
            "ticker": ticker,
            "current_usd": curr_usd,
            "target_weight": weight,
            "target_usd": target_usd,
            "delta_usd": delta
        })
        
        # Remove from map to track assets that were dropped to weight=0
        if ticker in current_map:
            del current_map[ticker]
            
    # Handle any assets that the optimizer dropped entirely (not in optimal_weights)
    for ticker, curr_usd in current_map.items():
        orders.append({
            "ticker": ticker,
            "current_usd": curr_usd,
            "target_weight": 0.0,
            "target_usd": 0.0,
            "delta_usd": -curr_usd
        })

    result_df = pd.DataFrame(orders)
    return result_df.sort_values(by="delta_usd", ascending=False).reset_index(drop=True)

