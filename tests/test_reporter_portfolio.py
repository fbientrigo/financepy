"""
TDD – RED phase: tests for the new portfolio section in src/report.py
Run these BEFORE implementing the feature to confirm they fail.
"""

import unittest
import os
import shutil
import pandas as pd

from src.report import Reporter


def _make_snapshot_df(tickers_signals: dict) -> pd.DataFrame:
    """
    Helper: creates a minimal snapshot_df compatible with Reporter.generate_from_snapshot.
    tickers_signals: {ticker: signal_str}, e.g. {'MSFT': 'SELL_ALERT'}
    """
    rows = []
    for ticker, signal in tickers_signals.items():
        rows.append({
            "Ticker": ticker,
            "Close": 150.0,
            "ret_1d": 0.01,
            "vol_ewma": 0.02,
            "hurst_dfa": 0.5,
            "regime_label": "RANDOM",
            "risk_off_flag": False,
            "zscore": 1.5,
            "signal": signal,
            "state": "NEUTRAL",
            "confidence": 0.85,
            "reasons": [],
            "recent_signals": [],
            "market_lambda1_norm": 0.3,
            "market_lambda1_pctl": 0.5,
        })
    return pd.DataFrame(rows)


def _make_holdings_df(holdings: dict) -> pd.DataFrame:
    """
    Helper: creates a minimal holdings_df compatible with _render_portfolio_section.
    holdings: {ticker: usd_amount}, e.g. {'MSFT': 32.31}
    """
    rows = [{"ticker": t, "usd_amount": a, "last_updated": "2026-03-05"} for t, a in holdings.items()]
    return pd.DataFrame(rows)


class TestReporterPortfolioSection(unittest.TestCase):

    def setUp(self):
        self.test_reports = "test_reports_portfolio"
        os.makedirs(self.test_reports, exist_ok=True)
        self.reporter = Reporter(self.test_reports)

    def tearDown(self):
        shutil.rmtree(self.test_reports, ignore_errors=True)

    def test_portfolio_section_present_when_holdings_provided(self):
        """When holdings_df is provided, the report must contain the '💼 Mi Portafolio' section."""
        snapshot = _make_snapshot_df({"MSFT": "NONE"})
        holdings = _make_holdings_df({"MSFT": 100.0})

        content = self.reporter.generate_from_snapshot(snapshot, holdings_df=holdings)

        self.assertIn("Mi Portafolio", content)

    def test_sell_alert_highlighted_in_portfolio(self):
        """A ticker with SELL_ALERT must appear in the portfolio section with 🔴 and the USD amount."""
        snapshot = _make_snapshot_df({"MSFT": "SELL_ALERT"})
        holdings = _make_holdings_df({"MSFT": 32.31})

        content = self.reporter.generate_from_snapshot(snapshot, holdings_df=holdings)

        self.assertIn("🔴", content)
        self.assertIn("SELL_ALERT", content)
        self.assertIn("32.31", content)

    def test_buy_alert_highlighted_in_portfolio(self):
        """A ticker with BUY_ALERT must appear in the portfolio section with 🟢 and the USD amount."""
        snapshot = _make_snapshot_df({"NVDA": "BUY_ALERT"})
        holdings = _make_holdings_df({"NVDA": 500.0})

        content = self.reporter.generate_from_snapshot(snapshot, holdings_df=holdings)

        self.assertIn("🟢", content)
        self.assertIn("BUY_ALERT", content)
        self.assertIn("500.00", content)

    def test_no_portfolio_section_when_holdings_none(self):
        """Without holdings_df, the report must NOT contain the portfolio section header."""
        snapshot = _make_snapshot_df({"SPY": "NONE"})

        content = self.reporter.generate_from_snapshot(snapshot)

        self.assertNotIn("Mi Portafolio", content)
        # Core sections must still be present
        self.assertIn("Daily Market Summary", content)
        self.assertIn("Watchlist", content)

    def test_total_usd_value_shown(self):
        """The total portfolio value must be rendered in the section."""
        snapshot = _make_snapshot_df({"SPY": "NONE", "GLD": "NONE"})
        holdings = _make_holdings_df({"SPY": 300.0, "GLD": 150.0})

        content = self.reporter.generate_from_snapshot(snapshot, holdings_df=holdings)

        # Total = 450.00
        self.assertIn("450.00", content)


if __name__ == "__main__":
    unittest.main()
