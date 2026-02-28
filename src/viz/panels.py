import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def panel_price(df: pd.DataFrame, ticker: str, overlays: list) -> go.Figure:
    """
    Main Price Chart with Overlays.
    overlays: list of strings ['MA', 'Bollinger']
    """
    fig = go.Figure()
    
    # Candlestick or Line? User asked for history. Line is cleaner for long range, Candle for short.
    # Let's use Line for simplicity and performance in "Simple" dashboard, or Candle?
    # "Simple... visualizacion historial".
    # User might toggle. Let's stick to Line (Close) + Overlays.
    
    # Close Price
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Close'], 
        mode='lines', name=f'{ticker} Price',
        line=dict(color='white', width=1)
    ))

    # Overlays
    if 'MA' in overlays:
        # Check standard MAs from common indicators?
        # CommonIndicators calculates vol_20d, etc. usually MAs are ad-hoc or part of BB (20).
        # We can compute 50/200 on the fly if not in DF.
        # But wait, pipeline calculates what pipeline calculates.
        # "Dashboard no debe recalcular features... solo visualizar overlays (MA, Bollinger)."
        # But if standard pipeline doesn't emit MA50, we can calculate it here cheaply for VIZ.
        # Let's assume standard MAs (50, 200) are cheap enough for viz convenience.
        ma50 = df['Close'].rolling(50).mean()
        ma200 = df['Close'].rolling(200).mean()
        
        fig.add_trace(go.Scatter(x=df.index, y=ma50, name='MA50', line=dict(color='orange', width=1)))
        fig.add_trace(go.Scatter(x=df.index, y=ma200, name='MA200', line=dict(color='cyan', width=1)))

    if 'Bollinger' in overlays:
        if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df['bb_upper'], 
                name='BB Upper', line=dict(color='gray', width=0, dash='dot'),
                showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=df.index, y=df['bb_lower'], 
                name='BB Lower', line=dict(color='gray', width=0, dash='dot'),
                fill='tonexty', fillcolor='rgba(128, 128, 128, 0.2)',
                showlegend=True
            ))

    fig.update_layout(
        title=f"{ticker} Price History",
        yaxis_title="Price",
        template="plotly_dark",
        height=500,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    return fig

def panel_indicators(df: pd.DataFrame, indicators: list) -> go.Figure:
    """
    Secondary panel for Z-Score, Volatility, Hurst, etc.
    """
    fig = make_subplots(rows=len(indicators), cols=1, shared_xaxes=True)
    
    row_idx = 1
    for ind in indicators:
        if ind == 'Z-Score' and 'zscore' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df['zscore'],
                name='Z-Score', line=dict(color='magenta')
            ), row=row_idx, col=1)
            # Add threshold lines
            fig.add_hline(y=2.0, line_dash="dot", line_color="red", row=row_idx, col=1)
            fig.add_hline(y=-2.0, line_dash="dot", line_color="green", row=row_idx, col=1)
            fig.update_yaxes(title_text="Z-Score", row=row_idx, col=1)
            row_idx += 1
            
        elif ind == 'Hurst' and 'hurst_dfa' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df['hurst_dfa'],
                name='Hurst', line=dict(color='yellow')
            ), row=row_idx, col=1)
            fig.add_hline(y=0.5, line_dash="solid", line_color="white", row=row_idx, col=1)
            fig.update_yaxes(title_text="Hurst", row=row_idx, col=1)
            row_idx += 1
            
        elif ind == 'Volatility':
            # Prefer ewma if available
            col = 'vol_ewma' if 'vol_ewma' in df.columns else 'vol_20d'
            if col in df.columns:
                fig.add_trace(go.Scatter(
                    x=df.index, y=df[col],
                    name='Vol', line=dict(color='teal')
                ), row=row_idx, col=1)
                fig.update_yaxes(title_text="Vol", row=row_idx, col=1)
                row_idx += 1

    fig.update_layout(
        template="plotly_dark",
        height=150 * len(indicators),
        margin=dict(l=0, r=0, t=10, b=0)
    )
    return fig
