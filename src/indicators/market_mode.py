import pandas as pd
import numpy as np

def compute_lambda1_norm(returns: pd.DataFrame, window: int, min_assets: int = 5) -> pd.Series:
    """
    Computes the largest eigenvalue (Lambda 1) of the rolling correlation matrix.
    Normalized by the number of assets (N) to be in range [1/N, 1].
    Actually, for Corr Matrix, sum(eigenvalues) = N.
    So Lambda1 ranges [1, N].
    We normalize it: Lambda1 / N.
    
    Interpretation:
    - Close to 0 (actually 1/N): Diversified / Random structure.
    - Close to 1: High systemic correlation (Risk Off/Crash mode).
    
    Args:
        returns: DataFrame of asset returns (cols=tickers, index=date).
        window: Rolling window size.
        min_assets: Minimum valid assets required to compute.
        
    Returns:
        pd.Series: Time series of normalized Lambda1.
    """
    # Rolling correlation is expensive.
    # returns.rolling(window).corr() returns a MultiIndex (Date, Ticker) -> Ticker matrix.
    
    # Optimization: We only need the largest eigenvalue. 
    # For daily frequency and reasonable window (e.g., 20) and tickers (<500), 
    # iterating over dates might be cleaner than dealing with MultiIndex tensor.
    
    output_index = returns.index
    lambda1_series = pd.Series(index=output_index, dtype=float)
    lambda1_series[:] = np.nan
    
    # We need to start from 'window' size
    # Efficient iteration: use stride_tricks or just loop if N_days is small (<10k).
    # FinancePy is likely end-of-day, N_days ~ 2520 (10 years). Loop is fine.
    
    values = returns.values
    dates = returns.index
    
    # Pre-check NaNs?
    # We must handle changing universe (NaNs).
    
    # Relaxed handling for NaN
    # We want window including 'i' if we treat i as "today"
    # dates[i] is the label for row i.
    # values[i] is the data for row i.
    # Standard rolling: window ending at i (inclusive).
    # Slice: [i - window + 1 : i + 1]
    
    for i in range(window - 1, len(dates)):
        # Slice window (inclusive of i)
        start_idx = i - window + 1
        end_idx = i + 1
        if start_idx < 0:
             continue
             
        window_data = values[start_idx : end_idx]
        
        # Use Pandas for correlation
        sub_df = pd.DataFrame(window_data)
        
        # Robustness:
        # 1. Drop columns with too many NaNs (e.g. > 50% missing)
        # 2. Compute corr (pairwise)
        # 3. Fill remaining NaNs in corr with 0 (uncorrelated) to allow eigendecomp
        
        threshold = int(window * 0.5)
        # count valid
        valid_counts = sub_df.count()
        valid_cols = valid_counts[valid_counts >= threshold].index
        
        sub_df_valid = sub_df[valid_cols]
        
        n_assets = sub_df_valid.shape[1]
        
        if n_assets < min_assets:
            continue
            
        # Correlation matrix
        corr = sub_df_valid.corr()
        # Fill NaN correlations with 0 (conservative)
        corr = corr.fillna(0).values
        
        if corr.shape[0] == 0:
             continue
             
        # Eigenvalues
        eigvals = np.linalg.eigvalsh(corr)
        
        # Max eigenvalue
        max_eig = eigvals.max()
        
        # Normalize
        lambda1_series.iloc[i] = max_eig / n_assets
        
        lambda1_series.iloc[i] = max_eig / n_assets
        
    return lambda1_series

def compute_market_mode_details(returns: pd.DataFrame, 
                                target_date: pd.Timestamp, 
                                window: int, 
                                min_assets: int = 3) -> dict:
    """
    Computes detailed diagnostics for Market Mode on a specific date.
    Returns a dictionary suitable for manifest/transparency.
    """
    if target_date not in returns.index:
        return {"error": f"Target date {target_date.date()} not in returns index."}
        
    # Find integer index
    try:
        idx = returns.index.get_loc(target_date)
    except KeyError:
        return {"error": "Date lookup failed"}
        
    # Define window: [start_idx : idx + 1]
    start_idx = idx - window + 1
    if start_idx < 0:
        return {"error": "Insufficient history for window"}
        
    window_data = returns.iloc[start_idx : idx + 1]
    
    # Metadata
    window_start = window_data.index[0]
    window_end = window_data.index[-1]
    n_days = len(window_data)
    
    # Columns usage
    all_tickers = returns.columns.tolist()
    
    # Filtering logic (same as compute_lambda1_norm)
    threshold = int(window * 0.5)
    valid_counts = window_data.count()
    used_tickers = valid_counts[valid_counts >= threshold].index.tolist()
    
    # Compile asset status
    asset_status = []
    for t in all_tickers:
        missing_count = window_data[t].isna().sum()
        missing_pct = missing_count / n_days
        status = {
            "ticker": t,
            "used": bool(t in used_tickers), # bool
            "missing_pct": float(missing_pct), # float
            "n_obs": int(n_days - missing_count), # int
            "reason": "Too many NaNs" if t not in used_tickers else "OK"
        }
        asset_status.append(status)
        
    sub_df = window_data[used_tickers]
    n_assets = sub_df.shape[1]
    
    if n_assets < min_assets:
        return {
            "error": f"Not enough assets ({n_assets}/{min_assets})",
            "assets": asset_status
        }
        
    # Corr
    corr_df = sub_df.corr()
    corr = corr_df.fillna(0).values
    
    # Eigendecomp
    eigvals, eigvecs = np.linalg.eigh(corr) # eigh for symmetric, returns sorted ascending
    
    # Sort descending
    eigvals = eigvals[::-1]
    eigvecs = eigvecs[:, ::-1]
    
    lambda1 = float(eigvals[0])
    lambda1_norm = float(lambda1 / n_assets)
    total_var = float(eigvals.sum())
    explained_ratio = float(lambda1 / total_var if total_var > 0 else 0)
    
    # Top 5 Eigenvalues
    top_k_vals = [{"rank": i+1, "value": float(v), "explained": float(v/total_var)} for i, v in enumerate(eigvals[:5])]
    
    # Top Component of 1st Eigenvector
    # Map back to tickers
    vec1 = eigvecs[:, 0]
    # Create list of (ticker, weight)
    components = []
    for t, w in zip(used_tickers, vec1):
        components.append({"ticker": t, "weight": float(w), "abs_weight": float(abs(w))})
        
    # Sort by influence
    components.sort(key=lambda x: x['abs_weight'], reverse=True)
    top_components = components[:10] 
    
    return {
        "meta": {
            "window_days": int(window),
            "window_start": str(window_start.date()),
            "window_end": str(window_end.date()),
            "n_obs_window": int(n_days),
            "n_assets_effective": int(n_assets)
        },
        "metrics": {
            "lambda1": lambda1,
            "lambda1_norm": lambda1_norm,
            "explained_ratio": explained_ratio
        },
        "assets": asset_status,
        "eigenvalues": top_k_vals,
        "eigenvector_1": top_components 
    }
