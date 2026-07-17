import argparse
import yaml
import datetime
import pandas as pd
from pathlib import Path
from typing import List, Optional

from src.store import DataStore
from src.data import DataLoader
from src.indicators.registry import IndicatorRegistry
from src.indicators.common import CommonIndicators
from src.indicators.advanced import AdvancedIndicators
from src.indicators.market_mode import compute_lambda1_norm
from src.analytics.regime import label_regime
from src.analytics.risk_off import compute_risk_off
from src.signals.registry import SignalRegistry
from src.signals.basic import BasicSignals
from src.report import Reporter
from src.portfolio_manager import get_portfolio_tickers, get_active_holdings
from src.logger_config import setup_logging, get_logger
import numpy as np

logger = get_logger("financepy.pipeline")

def load_config(path: str):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def run_pipeline(target_date: datetime.date, config_path: str) -> str:
    """
    Executes the pipeline for the given date and config.
    Returns the path to the generated report or raises error.
    """
    logger.info(f"Running pipeline for {target_date}...")

    # Load Config
    config = load_config(config_path)
    
    # Handle Universe Split
    if 'universes' in config:
        trade_tickers = config['universes']['trade']
        system_tickers = config['universes']['system']
        all_tickers = list(set(trade_tickers + system_tickers))
    else:
        # Fallback for old config
        trade_tickers = config['tickers']
        system_tickers = config['tickers']
        all_tickers = trade_tickers

    params = config['parameters']

    # Dynamic Ingestion: add portfolio tickers so they are always downloaded
    portfolio_db = config.get('paths', {}).get('portfolio_db', 'data_cache/portfolio.db')
    portfolio_tickers = get_portfolio_tickers(portfolio_db)
    if portfolio_tickers:
        logger.info(f"Portfolio tickers detected: {portfolio_tickers}")
        all_tickers = list(set(all_tickers + portfolio_tickers))

    # Initialize Components
    store = DataStore(config['paths']['data_cache'])
    loader = DataLoader(store)
    
    # 1. Ingest Data (All required tickers)
    logger.info(f"Ingesting data (Target: {target_date})...")
    # We ingest all distinct tickers needed
    count, errors = loader.fetch_and_store(all_tickers, target_date=target_date)
    for err in errors:
        logger.error(f"Ingestion error: {err}")
    
    # 4. Process Tickers
    
    # 4a. Global Market Mode Calculation (System Universe)
    logger.info("Loading system tickers for Global Analysis...")
    system_data = {}
    valid_returns = pd.DataFrame()
    
    for ticker in system_tickers:
        df = store.load(ticker)
        if df is not None and not df.empty:
            system_data[ticker] = df
            # We need log returns for Market Mode
            ret = np.log(df['Close'] / df['Close'].shift(1))
            valid_returns[ticker] = ret

    # Calculate Market Mode (Lambda1) - Time Series
    mm_cfg = params.get('market_mode', {})
    logger.info("Computing Market Mode (Lambda1)...")
    from src.indicators.market_mode import compute_market_mode_details
    
    lambda1 = compute_lambda1_norm(
        valid_returns, 
        window=mm_cfg.get('window', 20), 
        min_assets=mm_cfg.get('min_assets', 3)
    )
    
    # Calculate Detailed Diagnostics for Target Date
    mm_details = compute_market_mode_details(
        valid_returns,
        target_date=pd.Timestamp(target_date),
        window=mm_cfg.get('window', 20),
        min_assets=mm_cfg.get('min_assets', 3)
    )
    
    # Normalize Lambda1
    ro_cfg = params.get('risk_off', {})
    lb = ro_cfg.get('lookback', 252)
    lambda1_rank = lambda1.rolling(window=lb).rank(pct=True)
    
    snapshot_rows = []
    
    # 4b. Per-Ticker Processing (Trade Universe)
    ind_registry = IndicatorRegistry()
    ind_registry.register(CommonIndicators(params))
    ind_registry.register(AdvancedIndicators(params))
    
    sig_registry = SignalRegistry()
    sig_registry.register(BasicSignals(params)) 
    
    # Load Trade Data if different from system
    all_data_map = {} # Cache already loaded
    
    for ticker in trade_tickers:
        # Load from store if not already in system_data (optimization)
        if ticker in system_data:
            df = system_data[ticker]
        else:
            df = store.load(ticker)
            
        if df is None or df.empty:
            continue
            
        # Apply Indicators
        df_features = ind_registry.apply_all(df)
        
        # Integrate Global Features (Lambda 1)
        df_features['market_lambda1_norm'] = lambda1.reindex(df.index)
        df_features['market_lambda1_pctl'] = lambda1_rank.reindex(df.index)
        
        # Calculate Analytics (Regime & Risk Off)
        h_cfg = params.get('hurst', {})
        df_features['regime_label'] = label_regime(
            df_features['hurst_dfa'], 
            hi=h_cfg.get('high_threshold', 0.55), 
            lo=h_cfg.get('low_threshold', 0.45)
        )
        
        ro_cfg = params.get('risk_off', {})
        df_features['risk_off_flag'] = compute_risk_off(
            df_features['vol_ewma'], 
            df_features['market_lambda1_norm'],
            lookback=ro_cfg.get('lookback', 252),
            pctl=ro_cfg.get('percentile_threshold', 0.90)
        )
        
        # Apply Signals
        df_signals = sig_registry.apply_all(df_features)
        
        # Combine
        full_df = pd.concat([df_features, df_signals], axis=1)
        
        # Extract row for target date
        try:
            if pd.Timestamp(target_date) in full_df.index:
                row = full_df.loc[pd.Timestamp(target_date)]
                
                row_dict = row.to_dict()
                row_dict['Ticker'] = ticker
                
                # Capture recent history
                start_window = pd.Timestamp(target_date) - pd.Timedelta(days=30)
                recent_mask = (full_df.index >= start_window) & (full_df.index <= pd.Timestamp(target_date))
                recent_df = full_df.loc[recent_mask]
                
                recent_signals = []
                for dt, r_row in recent_df.iterrows():
                    sig = r_row.get('signal', 'NONE')
                    if sig != 'NONE':
                        recent_signals.append(f"{dt.date()}: {sig} (Z={r_row.get('zscore',0):.2f})")
                
                row_dict['recent_signals'] = recent_signals
                snapshot_rows.append(row_dict)
            else:
                last_dt = full_df.index[-1]
                logger.warning(f"No data for {ticker} on {target_date}. Last data: {last_dt.date()}")
        except Exception as e:
            logger.error(f"Error processing {ticker}: {e}")

    # 5. Report
    if not snapshot_rows:
        logger.warning("No data found for target date. Report will be empty/skipped.")
        
    snapshot_df = pd.DataFrame(snapshot_rows)
    if not snapshot_df.empty:
        snapshot_df = snapshot_df.sort_values("Ticker")

    # Transparency / Manifest
    from src.transparency.manifest import ManifestManager
    from src.transparency.render_md import MarkdownRenderer
    
    man_mgr = ManifestManager("reports/manifests")
    # Collect generic info
    manifest = man_mgr.collect_run_info(config, all_tickers, target_date, errors=errors)
    
    # Inject Detailed Metrics Info
    if 'details' not in manifest:
        manifest['details'] = {}
    
    manifest['details']['market_mode'] = mm_details
    
    saved_manifest_path = man_mgr.save_manifest(manifest, target_date)
    
    # Render Transparency MD
    # Link is relative to reports/YYYY-MM-DD_summary.md -> manifests/X.json
    rel_path = f"manifests/{saved_manifest_path.name}"
    transparency_md = MarkdownRenderer.render_transparency_section(manifest, relative_manifest_path=rel_path)

    # Load live portfolio holdings (empty DataFrame if DB not present)
    holdings_df = get_active_holdings(portfolio_db)

    reporter = Reporter(config['paths']['reports'])
    report_content = reporter.generate_from_snapshot(
        snapshot_df,
        errors=errors,
        holdings_df=holdings_df if not holdings_df.empty else None,
    )
    
    # Append Transparency Section
    report_content += "\n\n" + transparency_md
    
    saved_path = reporter.save(report_content, str(target_date))
    return saved_path

def main():
    parser = argparse.ArgumentParser(description="Run Daily Market Summary Pipeline")
    parser.add_argument("--date", type=str, help="Target date YYYY-MM-DD", default=None)
    parser.add_argument("--config", type=str, default="configs/config.yaml")
    parser.add_argument("--log-level", type=str, default="INFO", 
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    args = parser.parse_args()

    # Setup logging
    setup_logging(log_level=args.log_level)

    if args.date:
        target_date = datetime.datetime.strptime(args.date, "%Y-%m-%d").date()
    else:
        target_date = datetime.date.today()

    run_pipeline(target_date, args.config)

if __name__ == "__main__":
    main()
