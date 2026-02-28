METRIC_SPECS = {
    "bollinger": {
        "name": "Bollinger Bands & Z-Score",
        "type": "Technical Indicator",
        "description": "Measures price volatility and relative position using moving averages and standard deviations.",
        "definition_md": """
**Bollinger Bands** consist of:
- **Middle Band**: $N$-period Simple Moving Average (SMA).
- **Upper Band**: Middle Band + ($K \times$ $N$-period Standard Deviation).
- **Lower Band**: Middle Band - ($K \times$ $N$-period Standard Deviation).

**Z-Score**: Represents the distance between the current Close price and the Middle Band, normalized by the Standard Deviation.
$$ Z = \\frac{Price - SMA}{StdDev} $$
        """,
        "assumptions_md": """
- Assumes prices are roughly normally distributed around the mean for Z-Score interpretation (Z > 2 is rare).
- Relies on the specified window size ($N$) to capture the relevant trend.
        """,
        "params": ["bollinger_window", "bollinger_std"],
        "references": [
            ("Investopedia - Bollinger Bands", "https://www.investopedia.com/terms/b/bollingerbands.asp")
        ]
    },
    "ewma_vol": {
        "name": "EWMA Volatility",
        "type": "Risk Metric",
        "description": "Exponentially Weighted Moving Average of squared returns, providing a reactive volatility measure.",
        "definition_md": """
Recursive calculation:
$$ \\sigma_t^2 = (1 - \\lambda) r_{t-1}^2 + \\lambda \\sigma_{t-1}^2 $$
Where $\\lambda$ is the decay factor derived from the span $S$: $\\lambda = 1 - \\frac{2}{S+1}$.
        """,
        "assumptions_md": """
- More weight on recent data makes it "faster" to react to shocks than simple StdDev.
- Assumes mean daily return is effectively zero for daily data.
        """,
        "params": ["ewma_vol.span"],
        "references": [
            ("RiskMetrics Technical Document", "https://www.msci.com/documents/10199/5915b101-4206-4ba0-aee2-3449d5c7e95a")
        ]
    },
    "hurst_dfa": {
        "name": "Hurst Exponent (DFA)",
        "type": "Econophysics / Fractal",
        "description": "Estimates the long-term memory of a time series using Detrended Fluctuation Analysis.",
        "definition_md": """
Measures the scaling of root-mean-square fluctuations $F(n)$ of the integrated series:
$$ F(n) \propto n^H $$
- $H=0.5$: Random Walk (Brownian Motion).
- $H>0.5$: Persistent (Trending).
- $H<0.5$: Anti-persistent (Mean Reverting).
        """,
        "assumptions_md": """
- **CRITICAL**: Input is sanitized via Log-Returns ($r_t = \ln(P_t) - \ln(P_{t-1})$) to ensure stationarity (I(0)).
- Requires sufficient data length (minimum window) to be statistically significant.
- Assumes the underlying process has fractal properties (self-similarity).
        """,
        "params": ["hurst.window", "hurst.min_scale"],
        "references": [
            ("Wikipedia - Detrended Fluctuation Analysis", "https://en.wikipedia.org/wiki/Detrended_fluctuation_analysis"),
            ("Forensic Validation", "Internal Audit: Differential Sanitization Applied")
        ]
    },
    "market_mode": {
        "name": "Market Mode (Lambda 1)",
        "type": "Systemic Risk",
        "description": "Largest eigenvalue of the correlation matrix, normalized by N.",
        "definition_md": """
$$ \lambda_{1, norm} = \\frac{\max(\text{eig}(\mathbf{C}))}{N} $$
Where $\mathbf{C}$ is the correlation matrix of $N$ assets.
        """,
        "assumptions_md": """
- Captures the primary mode of collective motion.
- High values indicate systemic correlation (risk of simultaneous crash).
- Assumes linear pairwise correlations.
        """,
        "params": ["market_mode.window", "market_mode.min_assets"],
        "references": [
            ("Random Matrix Theory in Finance", "https://arxiv.org/abs/cond-mat/9903369")
        ]
    }
}
