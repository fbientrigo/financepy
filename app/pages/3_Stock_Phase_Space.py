import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add root to path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.data import DataLoader
from src.store import DataStore
from src.analytics.phase_space import compute_phase_space_trails

# ------------------------------------------------------------------------------
# Config
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Stock Phase Space",
    page_icon="🚀",
    layout="wide"
)

# ------------------------------------------------------------------------------
# State & Data Loading
# ------------------------------------------------------------------------------
@st.cache_resource
def get_loader():
    store = DataStore("data_cache")
    return DataLoader(store)

def load_stock_data(tickers, start_date, end_date):
    loader = get_loader()
    
    # 1. Update Cache (Defensive)
    # We don't want to crash if a user types garbage
    valid_tickers = []
    
    with st.spinner(f"Updating data for {len(tickers)} tickers..."):
        # We process in batch or loop to catch individual errors?
        # Loader.fetch_and_store processes list but returns error list.
        # Let's trust loader to handle bulk, but we should probably filter before 'load'
        
        # Actually loader.fetch_and_store returns (count, errors)
        try:
           count, errors = loader.fetch_and_store(tickers, target_date=end_date)
           if errors:
               # Show warning but proceed with what we have
               st.warning(f"Issues fetching some tickers: {errors}")
        except Exception as e:
            st.error(f"Critical Loader Error: {e}")
            return pd.DataFrame()

    # 2. Load Combined
    # We blindly load all requested. The loader will return what exists.
    try:
        data = loader.load_combined_prices(tickers, start_date=start_date)
        return data.ffill().dropna()
    except Exception as e:
        st.error(f"Error loading combined data: {e}")
        return pd.DataFrame()

def run_analytics(df, analysis_window):
    return compute_phase_space_trails(df, analysis_window=analysis_window, hurst_window=60)

# Sidebar
st.sidebar.title("Stock Cinemática 🚀")

# A. Selector de Activos
DEFAULT_TICKERS = ['NVDA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'AMD', 'COIN']

selected_tickers = st.sidebar.multiselect(
    "Selecciona Activos (Escribe para buscar):",
    options=DEFAULT_TICKERS + ['INTC', 'NFLX', 'SPY', 'QQQ', 'IWM'], # Add some commons to list
    default=DEFAULT_TICKERS
)

# Interactivity: Slider
analysis_window = st.sidebar.slider("Ventana de Dinámica (Lookback)", 100, 500, 252)

if not selected_tickers:
    st.info("Selecciona al menos un activo para iniciar.")
    st.stop()

# Execution Pipeline
start_fetch = datetime.today().date() - timedelta(days=analysis_window*2 + 100) # Buffer
end_fetch = datetime.today().date()

prices = load_stock_data(selected_tickers, start_fetch, end_fetch)

if prices.empty:
    st.warning("No hay datos suficientes para los activos seleccionados.")
    st.stop()

# Computation
trails_data = run_analytics(prices, analysis_window)

# ------------------------------------------------------------------------------
# UI: Visualization (Comet Plot)
# ------------------------------------------------------------------------------
st.title("🚀 Dinámica de Acciones (Comet Plot)")
st.markdown(f"**Espacio de Fase:** Eficiencia (Hurst) vs Performance (Retorno) | {analysis_window} días")

# Plotly
fig = go.Figure()

# 1. Background Zones (Reusing style)
fig.add_vrect(x0=0.0, x1=0.45, fillcolor="red", opacity=0.1, layer="below", line_width=0)
fig.add_vrect(x0=0.45, x1=0.55, fillcolor="gray", opacity=0.1, layer="below", line_width=0)
fig.add_vrect(x0=0.55, x1=1.0, fillcolor="green", opacity=0.1, layer="below", line_width=0)
fig.add_vline(x=0.5, line_width=1, line_dash="dash", line_color="white")
fig.add_hline(y=0.0, line_width=1, line_color="white")

# Color Palette generator (Cycle)
import plotly.colors as pc
palette = pc.qualitative.Plotly

for i, (ticker, data) in enumerate(trails_data.items()):
    color = palette[i % len(palette)]
    
    # A. Trail
    fig.add_trace(go.Scatter(
        x=data['hurst_history'],
        y=data['return_history'],
        mode='lines',
        line=dict(color=color, width=1),
        opacity=0.3,
        name=ticker, # Legend controls this group? No, legend is per trace usually.
        legendgroup=ticker,
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # B. Head
    size = max(8, data['current_vol'] * 150) # Heuristic size
    
    fig.add_trace(go.Scatter(
        x=[data['current_hurst']],
        y=[data['current_return']],
        mode='markers+text',
        marker=dict(color=color, size=size, line=dict(width=1, color='white')),
        text=[ticker],
        textposition="top center",
        name=ticker,
        legendgroup=ticker, # Click legend toggles both head and trail
        hovertemplate=f"<b>{ticker}</b><br>H: %{{x:.2f}}<br>Ret: %{{y:.2%}}<br>Vol: {data['current_vol']:.2%}"
    ))

fig.update_layout(
    xaxis_title="Hurst Exponent (Efficiency/Trend)",
    yaxis_title=f"Rolling Return (60d)",
    height=800,
    width=1200,
    template="plotly_dark",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)
