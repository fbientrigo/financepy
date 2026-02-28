import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

# Add root to path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.analytics.etf_monitor import ETFMonitor
from src.indicators.hurst_dfa import rolling_hurst_dfa, prepare_log_returns

# ------------------------------------------------------------------------------
# Config
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Global Cinematic Ecosystem",
    page_icon="☄️",
    layout="wide"
)

# ------------------------------------------------------------------------------
# State & Data Loading
# ------------------------------------------------------------------------------
@st.cache_resource
def get_monitor():
    return ETFMonitor() # Now uses DataLoader internally

@st.cache_data(ttl=3600*24)
def load_data(start_date, end_date):
    monitor = get_monitor()
    df = monitor.fetch_data(start_date=str(start_date), end_date=str(end_date))
    return df

@st.cache_data
def run_phase_space(df, analysis_window):
    monitor = get_monitor()
    return monitor.compute_phase_space_trails(df, analysis_window=analysis_window)

@st.cache_data
def run_full_analytics(df):
    monitor = get_monitor()
    return monitor.compute_analytics(df, window_corr=60)

# Sidebar Config
st.sidebar.title("Configuración Cinemática")
# Phase Space is about recent history dynamics
analysis_window = st.sidebar.slider("Ventana de Dinámica (Lookback Segments)", 100, 500, 252)

monitor = get_monitor()

# We still need a broad enough dataset for the pipeline
start_date_fetch = datetime.today() - timedelta(days=analysis_window * 2) # buffer
end_date_fetch = datetime.today()

# Fetch
with st.spinner("Sincronizando Trayectorias..."):
    prices = load_data(start_date_fetch.date(), end_date_fetch.date())

if prices.empty:
    st.error("No se pudieron cargar datos.")
    st.stop()
    
# Compute
trails_data = run_phase_space(prices, analysis_window)
metrics = run_full_analytics(prices) # Keep the old metrics for Drill Down if needed

# ------------------------------------------------------------------------------
# UI: Header
# ------------------------------------------------------------------------------
st.title("☄️ Monitor de Dinámica de Fase")
st.markdown(f"**Análisis de Trayectoria:** Últimos {analysis_window} puntos comerciales.")

# ------------------------------------------------------------------------------
# UI: Comet Plot (Phase Space)
# ------------------------------------------------------------------------------
st.subheader("Espacio de Fase: Eficiencia vs Retorno")

fig = go.Figure()

# 1. Background Zones
# X axis: Hurst (0.2 to 0.8 usually)
# Y: Return (-0.2 to 0.2 usually for rolling window)

# We can add shapes, but they need fixed coordinates. 
# Better: Colored rectangles.
# Red (Low Hurst < 0.45) | Grey (0.45 - 0.55) | Green (High Hurst > 0.55)
fig.add_vrect(x0=0.0, x1=0.45, fillcolor="red", opacity=0.1, layer="below", line_width=0)
fig.add_vrect(x0=0.45, x1=0.55, fillcolor="gray", opacity=0.1, layer="below", line_width=0)
fig.add_vrect(x0=0.55, x1=1.0, fillcolor="green", opacity=0.1, layer="below", line_width=0)
fig.add_vline(x=0.5, line_width=1, line_dash="dash", line_color="white")
fig.add_hline(y=0.0, line_width=1, line_color="white")

# 2. Trails & Heads
# Color map
region_colors = {
    'USA (S&P 500)': 'cyan', 'USA (Nasdaq)': 'magenta', 
    'Europe (FTSE)': 'blue', 'Emerging Markets': 'orange',
    'China': 'red', 'Japan': 'white', 'Global (MSCI World)': 'lime',
    'Gold': 'gold', 'Oil': 'black', 'Macro': 'grey'
}

for ticker, data in trails_data.items():
    color = region_colors.get(data['region'], 'white')
    
    # A. Trail (The tail)
    fig.add_trace(go.Scatter(
        x=data['hurst_history'],
        y=data['return_history'],
        mode='lines',
        line=dict(color=color, width=1), # Thin line
        opacity=0.5, # Ghostly
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # B. Head (The star)
    # Size by volatility?
    size = max(5, data['current_vol'] * 100) # Scaling heuristic
    
    fig.add_trace(go.Scatter(
        x=[data['current_hurst']],
        y=[data['current_return']],
        mode='markers+text',
        marker=dict(color=color, size=size, line=dict(width=1, color='white')),
        text=[ticker],
        textposition="top center",
        name=ticker,
        hovertemplate=f"<b>{ticker}</b><br>H: %{{x:.2f}}<br>Ret: %{{y:.2%}}<br>Vol: {data['current_vol']:.2%}"
    ))

fig.update_layout(
    xaxis_title="Hurst Exponent (Market Efficiency)",
    yaxis_title=f"Rolling Return (60d)",
    height=700,
    width=1000,
    template="plotly_dark",
    title="Dinámica de Mercado: ¿Tendencia o Ruido?"
)

# Annotations for Quadrants
fig.add_annotation(x=0.8, y=0.15, text="Target Zone (Trend + Profit)", showarrow=False, opacity=0.5)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------------------
# Drill Down (Existing)
# ------------------------------------------------------------------------------
with st.expander("🔬 Drill-Down Tradicional (Detalles)"):
    st.markdown("---")
    st.subheader("Análisis Individual")
    
    col_sel, _ = st.columns(2)
    selected_ticker = col_sel.selectbox("Selecciona ETF:", monitor.get_basket_tickers())
    
    # ... (Keep existing Drill Down Logic but simplified or reusing metrics)
    # Reusing metrics from full run
    
    rolling_corr_dict = metrics['rolling_corr']
    
    # Need to regen the rolling hurst series specifically for the plot...
    # Or just fetch fresh from pipeline for visualization
    asset_prices = prices[selected_ticker]
    asset_hurst = rolling_hurst_dfa(prepare_log_returns(asset_prices), window=126)
    
    # Correlations
    corr_gld = rolling_corr_dict.get('GLD', pd.DataFrame())[selected_ticker] if 'GLD' in rolling_corr_dict else None
    
    # Simple Plot
    fig_dd = go.Figure()
    fig_dd.add_trace(go.Scatter(x=asset_prices.index, y=asset_prices, name="Price", line=dict(color='cyan')))
    fig_dd.add_trace(go.Scatter(x=asset_hurst.index, y=asset_hurst, name="Hurst", yaxis="y2", line=dict(color='yellow')))
    
    fig_dd.update_layout(
        template="plotly_dark", 
        yaxis2=dict(overlaying="y", side="right", range=[0, 1], title="Hurst"),
        title=f"{selected_ticker} Detail"
    )
    st.plotly_chart(fig_dd, use_container_width=True)
