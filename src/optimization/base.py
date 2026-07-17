"""
src/optimization/base.py
------------------------
Base Protocol/Interface for Portfolio Optimization Engines.
"""

import pandas as pd
from typing import Protocol, Dict

class PortfolioOptimizer(Protocol):
    """
    Abstract Protocol defining the contract for all Portfolio Optimizers.
    Future implementations (Black-Litterman, HRP, Deep RL) must adhere to this.
    """
    
    def optimize(self, prices_df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculates the optimal weights for a portfolio given historical prices.

        Args:
            prices_df: DataFrame where index is Datetime and columns are asset tickers.
                       Values are aligned historical closing prices.

        Returns:
            A dictionary mapping ticker symbols to optimal weights (floats between 0 and 1).
            The sum of all weights must exactly equal 1.0.
        """
        ...
