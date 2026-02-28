import pandas as pd
from typing import Protocol, List

class Indicator(Protocol):
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Takes a DataFrame with at least 'Close' column.
        Returns a DataFrame with calculated features added.
        """
        ...

class IndicatorRegistry:
    def __init__(self):
        self._indicators: List[Indicator] = []

    def register(self, indicator: Indicator):
        self._indicators.append(indicator)

    def apply_all(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all registered indicators sequentially.
        """
        df_out = df.copy()
        for ind in self._indicators:
            df_out = ind.calculate(df_out)
        return df_out
