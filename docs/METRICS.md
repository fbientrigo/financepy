# Quantitative Metrics Documentation

## Market Mode (Lambda 1)
**Concept**: Measures the degree of systemic correlation in the market using the largest eigenvalue ($\lambda_1$) of the correlation matrix of asset returns. 
**Normalization**: We normalize $\lambda_1$ by the number of assets ($N$), resulting in a value between $1/N$ (uncorrelated) and $1.0$ (perfectly correlated).
**Interpretation**:
- **Low Values**: The market is driven by idiosyncratic factors; diversification works well.
- **High Values (>0.7)**: The market is moving in lockstep (Systemic Risk); diversification benefits are low. Often precedes or accompanies crashes.
**Assumptions**:
- Based on a rolling window (default 20 days).
- Assumes linear correlations (Pearson).

## EWMA Volatility
**Concept**: Exponentially Weighted Moving Average methodology (RiskMetrics).
**Interpretation**:
- Gives more weight to recent observations, making it more reactive to shocks than simple moving average volatility.
- Used as a "temperature" gauge for the asset.
**Assumptions**:
- Returns are normally distributed (mostly for scaling z-scores).
- Decay factor (lambda) is fixed (implied by span).

## Hurst Exponent (DFA)
**Concept**: Detrended Fluctuation Analysis (DFA) estimates the Hurst index ($H$) to classify time series memory.
**Interpretation**:
- **$H \approx 0.5$**: Random Walk (efficient market).
- **$H > 0.5$**: Persistent behavior (Trending).
- **$H < 0.5$**: Anti-persistent (Mean Reverting).
**Limits**:
- Requires sufficient data length for stable estimation. Short windows (e.g., <100 days) can be noisy.
- We use a rolling window to detect regime shifts.

## Correlation Heatmap
**Concept**: Visualizes the pairwise correlation matrix of the universe returns over a rolling window.
**Interpretation**:
- **Red**: High positive correlation.
- **Blue**: High negative correlation.
- **Ordered**: Tickers are sorted by average correlation to reveal clusters.
