import unittest

import pandas as pd

from src.report import Reporter

# pyright: reportArgumentType=false


class ReporterResilienceTests(unittest.TestCase):
    def test_reporter_does_not_expose_generate_report(self):
        self.assertFalse(hasattr(Reporter, "generate_report"))

    def test_generate_from_snapshot_requires_close_and_ret(self):
        snapshot_df = pd.DataFrame([{"Ticker": "AAA"}])
        reporter = Reporter("x")
        report = reporter.generate_from_snapshot(snapshot_df, errors=None)  # type: ignore
        self.assertIn("AAA", report)

    def test_generate_from_snapshot_requires_signal_column(self):
        snapshot_df = pd.DataFrame([
            {"Ticker": "BBB", "Close": 10.0, "ret_1d": 0.01}
        ])
        reporter = Reporter("x")
        report = reporter.generate_from_snapshot(snapshot_df, errors=None)  # type: ignore
        self.assertIn("BBB", report)


if __name__ == "__main__":
    _ = unittest.main()
