"""
TDD – RED phase: tests for src/portfolio_manager.py
Run these BEFORE implementing the module to confirm they fail.
"""

import sqlite3
import datetime
import tempfile
import os
import unittest
import pandas as pd

from src.portfolio_manager import get_active_holdings, get_portfolio_tickers


def _create_test_db(path: str, rows: list[tuple]) -> None:
    """Helper: creates a portfolio.db at `path` and inserts `rows` (ticker, usd_amount, timestamp)."""
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE holdings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ticker TEXT NOT NULL,
            usd_amount REAL NOT NULL
        )
    """)
    cursor.executemany(
        "INSERT INTO holdings (ticker, usd_amount, timestamp) VALUES (?, ?, ?)",
        rows,
    )
    conn.commit()
    conn.close()


class TestGetActiveHoldings(unittest.TestCase):

    def test_returns_empty_df_when_db_missing(self):
        """If the DB doesn't exist, the function must return an empty DataFrame (no exception)."""
        result = get_active_holdings("/tmp/__nonexistent_portfolio_db__.db")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)

    def test_returns_latest_snapshot_per_ticker(self):
        """
        When a ticker has multiple rows, only the row with MAX(timestamp) survives.
        """
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            _create_test_db(db_path, [
                ("MSFT", 100.0, "2026-03-01 10:00:00"),
                ("MSFT", 250.0, "2026-03-05 10:00:00"),  # latest – this should win
                ("AAPL", 500.0, "2026-03-04 10:00:00"),
            ])
            result = get_active_holdings(db_path)
            self.assertEqual(len(result), 2)

            msft_row = result[result["ticker"] == "MSFT"]
            self.assertAlmostEqual(msft_row["usd_amount"].iloc[0], 250.0)
        finally:
            os.unlink(db_path)

    def test_result_has_expected_columns(self):
        """Output DataFrame must have: ticker, usd_amount, last_updated."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            _create_test_db(db_path, [
                ("QQQ", 1000.0, "2026-03-05 10:00:00"),
            ])
            result = get_active_holdings(db_path)
            for col in ("ticker", "usd_amount", "last_updated"):
                self.assertIn(col, result.columns, f"Missing column: {col}")
        finally:
            os.unlink(db_path)

    def test_excludes_zero_amount_tickers(self):
        """Tickers with usd_amount == 0 should NOT appear in the result."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            _create_test_db(db_path, [
                ("NVDA", 0.0, "2026-03-05 10:00:00"),
                ("AMD",  200.0, "2026-03-05 10:00:00"),
            ])
            result = get_active_holdings(db_path)
            self.assertNotIn("NVDA", result["ticker"].values)
            self.assertIn("AMD", result["ticker"].values)
        finally:
            os.unlink(db_path)


class TestGetPortfolioTickers(unittest.TestCase):

    def test_returns_empty_list_when_db_missing(self):
        """Resilience: no DB → empty list, no exception."""
        result = get_portfolio_tickers("/tmp/__nonexistent_portfolio_db__.db")
        self.assertIsInstance(result, list)
        self.assertEqual(result, [])

    def test_returns_list_of_strings(self):
        """Return type must be list[str]."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            _create_test_db(db_path, [
                ("SPY", 300.0, "2026-03-05 10:00:00"),
                ("GLD", 150.0, "2026-03-05 10:00:00"),
            ])
            result = get_portfolio_tickers(db_path)
            self.assertIsInstance(result, list)
            self.assertTrue(all(isinstance(t, str) for t in result))
            self.assertIn("SPY", result)
            self.assertIn("GLD", result)
        finally:
            os.unlink(db_path)


if __name__ == "__main__":
    unittest.main()
