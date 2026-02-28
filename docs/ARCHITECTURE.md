# System Architecture

## Overview
FinancePy is designed as a linear ETL pipeline: **Extract (yfinance) -> Transform (Indicators) -> Load (Report)**. It emphasizes robustness (cache) and extensibility (registries).

## Data Flow

1.  **Ingestion (`src.data`)**:
    - `DataLoader` requests data for tickers.
    - Checks `DataStore` (Parquet) for existing data.
    - Fetches only missing ranges from `yfinance`.
    - Updates Cache.

2.  **Processing (`run_daily.py`)**:
    - **Global Pass**: Loads all tickers to compute Cross-Sectional metrics (Market Mode / Lambda 1). See [METRICS.md](METRICS.md) for definitions.
    - **Local Pass**: Iterates each ticker.
        - **Indicators (`src.indicators`)**: Calculates features (Returns, Vol, Hurst, Z-Score).
        - **Analytics (`src.analytics`)**: Derives higher-level tags (Regime, Risk-Off).
        - **Signals (`src.signals`)**: Generates alerts (BUY/SELL) filtering by Regime/Risk.

3.  **Reporting (`src.report`)**:
    - Aggregates snapshots.
    - Generates Markdown table.
    - Saves to `reports/`.

## Contracts

### DataFrames
- **Raw Data**: Columns `['Close', 'Open', 'High', 'Low', 'Volume']`. Index: `Datetime`.
- **Features**: Appends `ret_1d`, `vol_ewma`, `hurst_dfa`, `bb_upper`, `zscore`, etc.
- **Signals**: Appends `signal` (str), `confidence` (float), `reasons` (list).

### Extensibility
- **New Indicator**: Implement `calculate(df) -> df` and register in `run_daily`.
- **New Signal**: Implement `generate(df) -> df` and register.

## Directory Layout
```
src/
  data.py       # Fetching & Caching
  store.py      # Persistence (Parquet wrapper)
  report.py     # Markdown generation
  indicators/   # Feature logic
  signals/      # Trading logic
  analytics/    # Regime & Risk models
tests/          # Unittest suite
configs/        # YAML config
```
