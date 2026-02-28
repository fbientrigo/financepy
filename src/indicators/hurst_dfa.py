"""
Hurst Exponent Estimation using Detrended Fluctuation Analysis (DFA).

This module implements the DFA algorithm to estimate the Hurst exponent (H) of a time series.
It is designed for financial time series analysis, specifically dealing with stationarity
and microstructural noise issues.

Execution:
    To run the built-in verification (synthetic Brownian Motion test), use:

    .. code-block:: bash

        conda activate colab-env; python src/indicators/hurst_dfa.py

References:
    - Peng C.K., et al., "Mosaic organization of DNA nucleotides", Phys. Rev. E, 49, 1685 (1994).
    - Hardcoded Bias Audit (2026-01-08): Fixed spectral subsampling and microstructure noise contamination.
"""

import numpy as np
import pandas as pd
from typing import Optional, Union, List, Tuple
import warnings

def compute_hurst_dfa(
    series: pd.Series, 
    min_scale: int = 10, 
    max_scale: Optional[int] = None, 
    order: int = 1
) -> float:
    """
    Computes the Hurst Exponent (H) using Detrended Fluctuation Analysis (DFA).

    This implementation includes dynamic spectral sampling to avoid undersampling bias
    detected in previous audits.

    Parameters
    ----------
    series : pd.Series
        Time series data. Must be **STATIONARY** (e.g., Log-Returns).
        Do NOT pass raw prices directly; use `prepare_log_returns` first.
    min_scale : int, optional
        The minimum window size (s) for local trend fitting.
        Defaults to 10 to avoid microstructure noise (bid-ask bounce) and thermal noise.
        Warning: Values < 10 may include non-fractal noise.
    max_scale : int, optional
        The maximum window size. If None, defaults to N // 4.
        Ensures at least 4 windows are available for averaging at the largest scale.
    order : int, optional
        The order of the polynomial trend to remove.
        - 1: Linear detrending (remove local linear trends).
        - 2: Quadratic detrending.
        Defaults to 1.

    Returns
    -------
    float
        The estimated Hurst exponent H (0 < H < 1).
        - H ~ 0.5: Random Walk (uncorrelated noise).
        - H > 0.5: Persistent (Trending behavior).
        - H < 0.5: Anti-persistent (Mean Reversion).
        Returns np.nan if input length is insufficient or regression fails.

    Raises
    ------
    None
        Functions returns NaN on failure to allow pipeline continuity.

    Notes
    -----
    **Algorithm Steps & Mathematics:**

    1. **Integration (Profile Calculation):**
       The input stationary series :math:`X(t)` (noise) is mapped to a random walk profile :math:`Y(k)`:

       .. math::
           Y(k) = \sum_{t=1}^{k} [X(t) - \langle X \rangle]

       *Audit Note:* Global mean subtraction :math:`\langle X \rangle` implies weak stationarity. 
       For non-stationary history, use rolling windows.

    2. **Scale Segmentation:**
       The profile is divided into :math:`N_s = \lfloor N/s \rfloor` non-overlapping segments of length :math:`s`.

    3. **Detrending & Fluctuation Function:**
       In each segment :math:`v`, a polynomial trend :math:`Y_{trend}` is fitted.
       The Root Mean Square (RMS) fluctuation is calculated:

       .. math::
           F(s) = \sqrt{ \\frac{1}{N_s s} \sum_{v=1}^{N_s} \sum_{t=1}^{s} [Y_{v}(t) - Y_{v,trend}(t)]^2 }

    4. **Scaling Law Regression:**
       If the series is fractal, :math:`F(s)` follows a power law:

       .. math::
           F(s) \sim s^H \implies \log F(s) = H \log s + C

       The slope of the execution of the linear regression gives :math:`H`.

    **Algorithmic Complexity:**
    - Time Complexity: :math:`O(N \log N)`
      (Due to polynomial fitting across :math:`\log N` scales).
    - Space Complexity: :math:`O(N)`
      (To store the integrated profile).

    **Bias Mitigation (Audit 2026-01-08):**
    - **Spectral Sampling:** Uses dynamic density (approx 10/decade, min 20 scales) instead of fixed 10 points.
    - **Microstructure:** Default `min_scale=10` filters high-frequency noise.
    """
    # 1. Clean data validation
    # Drop NaNs to ensure contiguous memory block for vectorization
    y = series.dropna().values
    N = len(y)
    
    if max_scale is None:
        max_scale = N // 4
        
    # Validation: Need enough data for the minimum scale
    if N < 2 * min_scale:
        return np.nan
        
    if max_scale < min_scale:
        max_scale = min_scale
        
    # 2. Integrate the series (Profile)
    # Transformation: Noise -> Walk
    # Subtract global mean to avoid runaway drift in cumulative sum
    y_integrated = np.cumsum(y - np.mean(y))
    
    # 3. Define scales (Dynamic Spectral Sampling)
    # Refactored: Use dynamic sampling to avoid undersampling bias.
    # We aim for equidistant points in log-space (log-uniform distribution).
    n_decades = np.log10(max_scale / min_scale)
    # Heuristic: ~10 scales per decade, but at least 20 total for robust regression
    num_scales = int(max(20, n_decades * 10))
    
    scales = np.floor(np.logspace(np.log10(min_scale), np.log10(max_scale), num=num_scales)).astype(int)
    scales = np.unique(scales) # Remove duplicates from rounding
    scales = scales[scales > order + 2] # Ensure strictly enough points for poly fit degree
    
    if len(scales) < 2:
        return np.nan
        
    fluctuations = []
    
    # 4. Fluctuation Analysis Loop
    # Complexity: Sum of (N/s * s) for all s -> O(N * number_of_scales)
    for s in scales:
        # Split into segments of length s
        n_segments = N // s
        rms = 0.0
        
        # Vectorized segment processing is possible but complex due to reshaping issues with remainder.
        # Iterative approach is clearer for audit.
        
        # Iterate over segments
        for i in range(n_segments):
            seg_data = y_integrated[i*s : (i+1)*s]
            x_seg = np.arange(s)
            
            # Poly fit (Detrending)
            coeffs = np.polyfit(x_seg, seg_data, order)
            trend = np.polyval(coeffs, x_seg)
            
            # Sum of squared errors
            rms += np.sum((seg_data - trend)**2)
            
        # Average RMS calculation
        # Normalization by total number of points actually used (n_segments * s)
        rms /= (n_segments * s)
        fluctuations.append(np.sqrt(rms))
        
    # 5. Log-Log Regression Verification
    fluctuations = np.array(fluctuations)
    valid = fluctuations > 0 # Avoid log(0)
    
    if np.sum(valid) < 2:
        return np.nan
        
    log_s = np.log(scales[valid])
    log_f = np.log(fluctuations[valid])
    
    # OLS Regression
    # Note: OLS treats all scales equally. Weighted Least Squares (WLS) could be considered
    # to downweight larger, noisier scales, but OLS is standard for DFA.
    fit = np.polyfit(log_s, log_f, 1)
    hurst_obs = fit[0]
    
    return hurst_obs

def rolling_hurst_dfa(
    series: pd.Series, 
    window: int, 
    min_scale: int = 10
) -> pd.Series:
    """
    Apply DFA on a rolling window.

    Parameters
    ----------
    series : pd.Series
        Input time series.
    window : int
        Size of the rolling window.
    min_scale : int, optional
        Minimum scale for DFA. Defaults to 10.

    Returns
    -------
    pd.Series
        Series of Hurst exponents aligned with the input index.
    """
    return series.rolling(window=window).apply(
        lambda x: compute_hurst_dfa(x, min_scale=min_scale)
    )

def prepare_log_returns(
    series: Union[pd.Series, pd.DataFrame], 
    epsilon: float = 1e-8
) -> Union[pd.Series, pd.DataFrame]:
    """
    Transforms prices into Log-Returns to ensure stationarity for DFA.
    
    Implements robust handling for zero values to avoid "Survival Bias" (dropping crash data).

    Formula:
    .. math::
        r_t = \ln(P_t + \epsilon) - \ln(P_{t-1} + \epsilon)

    Parameters
    ----------
    series : Union[pd.Series, pd.DataFrame]
        Input asset prices.
    epsilon : float, optional
        Small constant to avoid log(0). Defaults to 1e-8.

    Returns
    -------
    Union[pd.Series, pd.DataFrame]
        Log-returns series. NaNs from shift are dropped or handled by caller.
    """
    # 1. Log Difference with epsilon for zero-robustness
    log_ret = np.log(series + epsilon) - np.log(series.shift(1) + epsilon)
    
    # 2. Cleanup
    # Even with epsilon, we might get NaNs from the shift or existing NaNs
    # Note: We do NOT strictly dropna here to allow caller to decide, 
    # but specifically handle Inf if they somehow appear.
    with pd.option_context('mode.use_inf_as_na', True):
         log_ret = log_ret.dropna()
         
    return log_ret

# ==============================================================================
# Execution Block: Synthetic Verification
# ==============================================================================
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    
    print("=== Hurst DFA Production Verification ===")
    
    # 1. Generate Geometric Brownian Motion (H=0.5 target)
    np.random.seed(42)
    N = 2000
    # Steps (Returns) ~ N(0, 1) -> Integration -> Brownian Motion
    steps = np.random.normal(loc=0, scale=0.02, size=N) 
    
    # Create Series
    ts_noise = pd.Series(steps)
    
    # 2. Test DFA on Noise (Should be H ~ 0.5)
    print(f"Testing on White Noise (Target H=0.5)...")
    h_noise = compute_hurst_dfa(ts_noise, min_scale=10)
    print(f"Estimated H (Noise): {h_noise:.4f}")
    
    if not (0.4 < h_noise < 0.6):
        warnings.warn(f"WARNING: H estimation for noise is far from 0.5: {h_noise}")
    else:
        print("PASS: Noise estimation within bounds.")

    # 3. Test on Random Walk (Price)
    # Caution: DFA requires STATIONARY input. 
    # If we pass a Random Walk directly to compute_hurst_dfa, it interprets it as "noise".
    # Standard DFA on a Random Walk (integrated noise) gives H ~ 1.5 theoretically?
    # No, DFA input assumption is usually the fractional Gaussian noise (fGn).
    # If we pass steps (fGn with H=0.5), we get 0.5.
    
    # Let's generate a fractional noise with python library if available? 
    # Or just rely on the white noise test.
    
    # 4. Test Rolling
    print("\nTesting Rolling DFA...")
    rolling_h = rolling_hurst_dfa(ts_noise, window=500, min_scale=10)
    print(f"Rolling H Mean: {rolling_h.mean():.4f}")
    print(f"Rolling H Std:  {rolling_h.std():.4f}")
    
    print("\nVerification Complete.")
