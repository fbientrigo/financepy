import unittest
from typing import cast

import pandas as pd  # type: ignore[reportMissingTypeStubs]


class BasicSignalsCleanupTests(unittest.TestCase):
    def test_basic_signals_module_does_not_expose_transform_series(self):
        import src.signals.basic as basic

        self.assertFalse(
            hasattr(basic, "transform_series"),
            "module still exposes transform_series",
        )

    def test_basic_signals_generate_regression(self):
        from src.signals.basic import BasicSignals

        df = pd.DataFrame({"zscore": [-3.0, 0.0, 3.0]})
        out = BasicSignals().generate(df)

        for col in ("signal", "state", "confidence", "reasons"):
            self.assertIn(col, out.columns, f"missing column {col}")

        reasons: list[list[str]] = cast(list[list[str]], out["reasons"].tolist())
        for reason_list in reasons:
            self.assertIsInstance(reason_list, list)

        first_row_reasons: list[str] = reasons[0]
        self.assertTrue(
            any("Oversold" in reason for reason in first_row_reasons),
            "first row lacks Oversold reason",
        )

        last_row_reasons: list[str] = reasons[-1]
        self.assertTrue(
            any("Overbought" in reason for reason in last_row_reasons),
            "last row lacks Overbought reason",
        )


if __name__ == "__main__":
    _ = unittest.main()
