import pandas as pd
import numpy as np
from src.store import DataStore
from src.indicators.market_mode import compute_lambda1_norm
import yaml

# Load config
with open("configs/config.yaml", 'r') as f:
    config = yaml.safe_load(f)

tickers = config['tickers']
store = DataStore(config['paths']['data_cache'])

# Load data
valid_returns = pd.DataFrame()
for ticker in tickers:
    df = store.load(ticker)
    if df is not None and not df.empty:
        ret = np.log(df['Close'] / df['Close'].shift(1))
        valid_returns[ticker] = ret

print(f"Returns Shape: {valid_returns.shape}")
print("NaN counts per column:")
print(valid_returns.isna().sum())

print("\nHead:")
print(valid_returns.tail(20))

# Compute Lambda1
print("\nComputing Lambda1...")
lambda1 = compute_lambda1_norm(valid_returns, window=20, min_assets=3)

print("\nLambda1 Tail:")
print(lambda1.tail(10))

print("\nLast Value:")
print(lambda1.iloc[-1])
