import plotly.graph_objects as go
import pandas as pd
import numpy as np

def panel_correlation_heatmap(universe_returns: pd.DataFrame, window: int = 60) -> go.Figure:
    """
    Rolling Correlation Heatmap (Last available window).
    """
    if universe_returns.empty:
        return go.Figure()
        
    # Slice last 'window' days
    recent = universe_returns.tail(window)
    
    if recent.empty:
        return go.Figure()
        
    # Compute Correlation
    corr = recent.corr()
    
    # Sort by average correlation (Cluster-ish)
    # Calculate mean correlation for each asset
    mean_corr = corr.mean().sort_values(ascending=False)
    sorted_tickers = mean_corr.index
    
    corr = corr.loc[sorted_tickers, sorted_tickers]
    
    # Heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.index,
        colorscale='RdBu_r', # Red = High Corr, Blue = Low/Neg
        zmin=-1, zmax=1
    ))
    
    fig.update_layout(
        title=f"Correlation Matrix (Last {window} days)",
        template="plotly_dark",
        height=600,
        width=600
    )
    return fig
