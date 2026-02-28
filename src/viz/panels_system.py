import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def panel_regime(df: pd.DataFrame, ticker: str) -> go.Figure:
    """
    Price chart with Regime Background Shading.
    Green = TREND, Red = MEAN_REVERT (or standard interpretation).
    Actually:
    TREND (H > 0.55): Shaded Green? Or maybe just distinct.
    MEAN_REVERT (H < 0.45): Shaded Yellow/Red?
    Let's use:
    - BLUE shade for TREND
    - ORANGE shade for MEAN_REVERT
    """
    fig = go.Figure()
    
    # 2. Shapes for Regimes (Add first so they are behind)
    # We need to find contiguous blocks of regimes
    if 'regime_label' in df.columns:
        # We handle this by identifying segments
        df['regime_change'] = df['regime_label'].ne(df['regime_label'].shift())
        df['regime_group'] = df['regime_change'].cumsum()
        
        # Legend proxies
        fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', 
                                marker=dict(size=10, color="rgba(0, 0, 255, 0.2)", symbol="square"),
                                name="Trend (Blue Shade)"))
        fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', 
                                marker=dict(size=10, color="rgba(255, 165, 0, 0.2)", symbol="square"),
                                name="Mean Revert (Orange Shade)"))
        
        for g, data in df.groupby('regime_group'):
            regime = data['regime_label'].iloc[0]
            start = data.index[0]
            end = data.index[-1]
            
            color = None
            if regime == 'TREND':
                color = "rgba(0, 0, 255, 0.2)" # Blueish, slightly more opaque
            elif regime == 'MEAN_REVERT':
                color = "rgba(255, 165, 0, 0.2)" # Orangeish
                
            if color:
                fig.add_vrect(
                    x0=start, x1=end,
                    fillcolor=color, opacity=1,
                    layer="below", line_width=0
                )

    # 1. Price (Add last to be on top)
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Close'], 
        mode='lines', name=f'{ticker} Price',
        line=dict(color='white', width=1.5)
    ))

    fig.update_layout(
        title=f"{ticker} Market Regime",
        yaxis_title="Price",
        template="plotly_dark",
        height=500,
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def panel_risk(df: pd.DataFrame) -> go.Figure:
    """
    Volatility + Risk Off Flags.
    """
    fig = go.Figure()
    
    # Volatility
    vol_col = 'vol_ewma' if 'vol_ewma' in df.columns else 'vol_20d'
    if vol_col in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df[vol_col],
            name='Volatility',
            line=dict(color='cyan', width=1)
        ))
        
    # Risk Off Markers
    if 'risk_off_flag' in df.columns:
        risk_off_days = df[df['risk_off_flag'] == True]
        if not risk_off_days.empty and vol_col in df.columns:
             fig.add_trace(go.Scatter(
                x=risk_off_days.index, y=risk_off_days[vol_col],
                mode='markers',
                name='Risk Off Trigger',
                marker=dict(color='red', size=8, symbol='x')
             ))

    fig.update_layout(
        title="Volatility & Risk Off Events",
        yaxis_title="Volatility",
        template="plotly_dark",
        height=400
    )
    return fig

def panel_market_mode(lambda1: pd.Series) -> go.Figure:
    """
    Timeline of Global Market Mode (Lambda1).
    """
    fig = go.Figure()
    
    if lambda1.empty:
        return fig
        
    fig.add_trace(go.Scatter(
        x=lambda1.index, y=lambda1,
        name='Market Mode (Normalized)',
        line=dict(color='magenta', width=1.5)
    ))
    
    # Add percentiles lines (historical)
    # Simple static lines? or rolling?
    # Simple static lines for context
    p90 = lambda1.quantile(0.90)
    p50 = lambda1.median()
    
    fig.add_hline(y=p90, line_dash="dot", line_color="red", annotation_text="90th Pctl (Systemic Risk)")
    fig.add_hline(y=p50, line_dash="dot", line_color="gray", annotation_text="Median")

    fig.update_layout(
        title="Systemic Risk: Market Mode (Lambda 1)",
        yaxis_title="Lambda1 / N",
        template="plotly_dark",
        height=400
    )
    return fig
