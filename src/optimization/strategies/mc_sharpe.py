"""
src/optimization/strategies/mc_sharpe.py
----------------------------------------
Monte Carlo Mean-Variance Portfolio Optimizer.

Maximizes the Sharpe Ratio by randomly sampling millions of portfolios.
"""

import pandas as pd
import numpy as np
from typing import Dict
from src.optimization.base import PortfolioOptimizer

class MonteCarloSharpeOptimizer(PortfolioOptimizer):
    """
    Portfolio optimizer utilizing Monte Carlo Simulation.
    
    It generates N random portfolios and selects the one that maximizes
    the annualized Sharpe Ratio:
    
        Sharpe Ratio = (Expected Return - Risk-Free Rate) / Expected Volatility
    """
    
    def __init__(self, num_simulations: int = 10000, risk_free_rate: float = 0.04):
        """
        Args:
            num_simulations (int): Limit of random portfolios to generate.
            risk_free_rate (float): Annually compounded risk-free rate (default 4%).
        """
        self.num_simulations = num_simulations
        self.risk_free_rate = risk_free_rate

    def optimize(self, prices_df: pd.DataFrame) -> Dict[str, float]:
        """
        Runs Monte Carlo simulations to find weights that maximize the Sharpe ratio.
        """
        # Calculate daily log returns
        returns = np.log(prices_df / prices_df.shift(1)).dropna()
        
        num_assets = len(prices_df.columns)
        if num_assets == 0:
            return {}
        if num_assets == 1:
            return {prices_df.columns[0]: 1.0}
            
        # Annualized metrics based on ~252 trading days
        trading_days = 252
        mean_returns = returns.mean() * trading_days
        cov_matrix = returns.cov() * trading_days

        # We will hold the optimal state here
        max_sharpe = -float('inf')
        optimal_weights = np.zeros(num_assets)

        for _ in range(self.num_simulations):
            # Generate random normalized weights
            weights = np.random.random(num_assets)
            weights /= np.sum(weights)

            # Expected Portfolio Return
            port_return = np.sum(mean_returns * weights)
            
            # Expected Portfolio Volatility (Risk)
            # w^T * Cov * w
            port_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            # Calculate Sharpe Ratio
            sharpe_ratio = (port_return - self.risk_free_rate) / port_volatility

            # Check if this is the best so far
            if sharpe_ratio > max_sharpe:
                max_sharpe = sharpe_ratio
                optimal_weights = weights

        # Format optimal weights into a dictionary mapping ticker to weight
        weights_dict = {
            ticker: float(weight) 
            for ticker, weight in zip(prices_df.columns, optimal_weights)
        }
        
        return weights_dict
