# FinancePy: End-of-Day Market Pipeline

A robust, offline-first financial analysis pipeline for daily market summaries, calculating advanced indicators (Hurst, Market Mode, Volatility) and generating Markdown reports.

## Features
- **Data Ingestion**: Robust `yfinance` fetching with local caching (no re-download).
- **Indicators**: Bollinger Bands, EWMA Volatility, Hurst Exponent (DFA), Market Mode (PCA).
- **Analytics**: Regime classification (Trend/Mean Revert) and Risk-Off logic.
- **Reporting**: Daily markdown summary with watchlist and systemic risk analysis.

## Structure
- `src/`: Core logic (data, indicators, signals, reporting).
- `tests/`: Unit and smoke tests.
- `configs/`: Configuration (tickers, parameters).
- `reports/`: Generated daily reports.
- `data_cache/`: Local Parquet store.

## Installation
1.  **Clone** repo.
2.  **Environment**:
    ```bash
    # Create venv (optional but recommended)
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate     # Windows
    
    # Install dependencies
    pip install pandas numpy yfinance pyyaml scipy
    ```

## Usage

### Daily Run
Execute the pipeline for the current date (or specific date):
```bash
python run_daily.py --date 2025-12-30
```
Reports are saved in `reports/`.

### Quality Assurance (Tests)
To validate the codebase (Unit tests + Smoke test):
```bash
# Option 1: Using Make (if available)
make qa

# Option 2: Using Python script (Cross-platform)
python scripts/qa.py
```

### Dashboard
Launch the interactive visualizer (Streamlit):
```bash
make dashboard
# or
streamlit run app/dashboard.py
```

## Troubleshooting
- **Missing Data**: Check `logs/` or console output. The pipeline warns but continues.
- **NaN in Indicators**: `Hurst` requires sufficient history. `Market Mode` requires multiple assets.
- **Network Issues**: The pipeline uses cached data if available. First run requires internet.

## Architecture
See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details on data flow and design contracts.
