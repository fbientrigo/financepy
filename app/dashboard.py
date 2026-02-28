import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add root to path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ... (previous imports)
from src.viz.loader import DashboardLoader
from src.viz.panels import panel_price, panel_indicators
from src.viz.panels_system import panel_regime, panel_risk, panel_market_mode
from src.viz.panels_corr import panel_correlation_heatmap
from src.transparency.manifest import ManifestManager
from src.transparency.render_st import StreamlitRenderer
import os

st.set_page_config(page_title="FinancePy Dashboard", layout="wide")

# Legacy helper removed. Using StreamlitRenderer.



# --- Initialize ---
@st.cache_data
def get_loader():
    return DashboardLoader()

@st.cache_data
def get_universe_data():
    l = get_loader()
    univ = l.load_universe_returns()
    mm = l.compute_global_market_mode(univ)
    return univ, mm

@st.cache_data
def get_manifest(run_date):
    mgr = ManifestManager("reports/manifests")
    return mgr.load_manifest(run_date)

loader = get_loader()

# --- Sidebar ---
st.sidebar.title("FinancePy Explorer")

available_tickers = loader.get_available_tickers()
if not available_tickers:
    st.error("No data found in cache. Run pipeline first.")
    st.stop()

selected_ticker = st.sidebar.selectbox("Select Ticker", available_tickers)

# Date Range
default_start = datetime.today() - timedelta(days=365)
default_end = datetime.today()

col1, col2 = st.sidebar.columns(2)
start_date = col1.date_input("Start", default_start)
end_date = col2.date_input("End", default_end)

# Load Manifest for End Date
manifest = get_manifest(end_date)
if not manifest:
    # Try looking back a few days? NO, explicit is better.
    # Just load without manifest.
    pass

# --- Tabs ---
tab_ticker, tab_regime, tab_system, tab_corr = st.tabs(["Ticker", "Régimen & Riesgo", "Sistema", "Correlación"])

# --- Load Single Ticker Data ---
df = loader.load_ticker(selected_ticker)

if df.empty:
    st.warning(f"No data for {selected_ticker}")
    st.stop()

# Filter Date
mask = (df.index.date >= start_date) & (df.index.date <= end_date)
df_view = df.loc[mask]

# --- TAB 1: TICKER ---
with tab_ticker:
    StreamlitRenderer.render_transparency_expander(manifest, metric_keys=["bollinger"])
    if df_view.empty:
        st.warning("No data in selected range.")
    else:
        c1, c2 = st.columns(2)
        show_ma = c1.checkbox("Show MA (50/200)", value=True)
        show_bb = c2.checkbox("Show Bollinger Bands", value=True)
        
        overlays = []
        if show_ma: overlays.append('MA')
        if show_bb: overlays.append('Bollinger')

        st.plotly_chart(panel_price(df_view, selected_ticker, overlays), use_container_width=True)

        st.subheader("Indicadores")
        i1, i2, i3 = st.columns(3)
        show_zscore = i1.checkbox("Z-Score", value=True)
        show_hurst = i2.checkbox("Hurst", value=False)
        show_vol = i3.checkbox("Volatility", value=False)
        
        indicators = []
        if show_zscore: indicators.append('Z-Score')
        if show_hurst: indicators.append('Hurst')
        if show_vol: indicators.append('Volatility')

        if indicators:
            st.plotly_chart(panel_indicators(df_view, indicators), use_container_width=True)

# --- TAB 2: REGIMEN & RIESGO ---
with tab_regime:
    StreamlitRenderer.render_transparency_expander(manifest, metric_keys=["hurst_dfa", "ewma_vol"])
    if df_view.empty:
        st.write("No data.")
    else:
        st.write("### Análisis de Régimen de Mercado")
        st.plotly_chart(panel_regime(df_view, selected_ticker), use_container_width=True)
        
        st.write("### Análisis de Riesgo (Risk Off)")
        st.plotly_chart(panel_risk(df_view), use_container_width=True)

# --- TAB 3: SISTEMA (Market Mode) ---
with tab_system:
    StreamlitRenderer.render_transparency_expander(manifest, metric_keys=["market_mode"])
    st.write("### Riesgo Sistémico Global")
    univ, mm = get_universe_data()
    
    if mm.empty:
        st.warning("Not enough data to calculate Systemic Risk.")
    else:
        mm_view = mm[(mm.index.date >= start_date) & (mm.index.date <= end_date)]
        st.plotly_chart(panel_market_mode(mm_view), use_container_width=True)
        
        st.info(f"Current Market Mode Level: {mm.iloc[-1]:.2f} (Norm)")

# --- TAB 4: CORRELACION ---
with tab_corr:
    StreamlitRenderer.render_transparency_expander(manifest, metric_keys=[]) # Show generic
    st.write("### Mapa de Calor de Correlación")
    univ, _ = get_universe_data()
    
    if univ.empty:
        st.warning("No universe data available.")
    else:
        window = st.slider("Ventana (días)", min_value=10, max_value=252, value=60)
        st.plotly_chart(panel_correlation_heatmap(univ, window=window), use_container_width=True)

