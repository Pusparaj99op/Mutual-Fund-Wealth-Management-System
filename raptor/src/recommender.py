"""Recommendation utilities using Black-Litterman + portfolio construction.

Prototype behaviors:
- Build historical returns matrix per scheme from aggregated features
- Estimate prior returns (pi) using historical mean returns
- Allow simple views (P, Q) input; if none, BL reduces to adjusted priors
- Compute posterior expected returns and mean-variance optimal weights
- Return allocation recommendations and simple portfolio metrics
"""
from typing import List, Optional, Tuple, Dict
import numpy as np
import pandas as pd
import logging
from raptor.src import ingest_aggregate, monte_carlo, black_scholes, black_litterman

logger = logging.getLogger('raptor.recommender')


def build_returns_matrix(agg: pd.DataFrame, scheme_codes: Optional[List[str]] = None, ret_col: str = 'ret_1d') -> pd.DataFrame:
    """Return a DataFrame of aligned returns (rows: dates, cols: scheme_codes).
    If scheme_codes is None, use all available schemes in aggregated data.
    """
    if scheme_codes is None:
        scheme_codes = agg['scheme_code'].unique().tolist()
    parts = []
    for code in scheme_codes:
        tmp = agg[agg['scheme_code'] == code][['date', ret_col]].rename(columns={ret_col: code})
        parts.append(tmp.set_index('date'))
    if not parts:
        raise ValueError('No schemes provided')
    df = pd.concat(parts, axis=1).sort_index()
    return df


def estimate_prior(returns_df: pd.DataFrame, annualize_factor: int = 252) -> Tuple[np.ndarray, np.ndarray]:
    """Estimate prior expected returns (pi) and covariance matrix from historical returns.
    Returns (pi, cov) where pi is vector (n,), cov is (n,n)
    """
    mean_daily = returns_df.mean()
    pi = mean_daily.values * annualize_factor
    cov = returns_df.cov().values * annualize_factor
    return pi, cov


def recommend_black_litterman(scheme_codes: Optional[List[str]] = None,
                              amount: float = 10000,
                              tau: float = 0.025,
                              risk_aversion: float = 3.0,
                              top_k: int = 5,
                              min_obs: int = 100) -> Dict:
    """Compute BL posterior returns and return a recommended allocation for the given schemes.

    If scheme_codes is None, consider top schemes available in aggregated dataset.
    """
    agg = ingest_aggregate.load_aggregated()
    if scheme_codes is None:
        # pick schemes with enough observations
        counts = agg.groupby('scheme_code').size().sort_values(ascending=False)
        scheme_codes = counts[counts >= min_obs].index.tolist()[:50]
    # Build returns matrix (daily returns)
    returns_df = build_returns_matrix(agg, scheme_codes=scheme_codes)
    # Drop columns with too few non-nulls
    valid = returns_df.columns[returns_df.notnull().sum() >= min_obs].tolist()
    returns_df = returns_df[valid].dropna()
    if returns_df.shape[1] == 0:
        raise ValueError('No schemes with sufficient observations')
    # Estimate priors
    pi, cov = estimate_prior(returns_df)
    # Default: empty views (P,Q) -> BL reduces to posterior near prior, but formula applies
    n = len(valid)
    P = np.eye(n)
    Q = pi.copy()
    posterior = black_litterman.black_litterman_expected_returns(tau=tau, pi=pi, P=P, Q=Q, cov=cov)
    # Get weights via mean-variance
    weights = black_litterman.markowitz_weights(posterior, cov, risk_aversion=risk_aversion)
    # Build allocations
    alloc = {code: float(w) for code, w in zip(valid, weights)}
    # Normalize tiny negatives to zero and renormalize
    for k in list(alloc.keys()):
        if alloc[k] < 1e-6:
            alloc[k] = 0.0
    s = sum(alloc.values())
    if s > 0:
        alloc = {k: v / s for k, v in alloc.items()}
    # Compose result list sorted by weight
    sorted_alloc = sorted(alloc.items(), key=lambda x: x[1], reverse=True)
    top_alloc = sorted_alloc[:top_k]
    # Add Monte Carlo and GBM expected returns for top_k schemes
    details = []
    for code, w in top_alloc:
        # Load NAV directly from raw CSV using monte_carlo function expectation
        try:
            from raptor.src.data_loader import load_nav_timeseries
            nav = load_nav_timeseries(code)['nav']
            sims = monte_carlo.monte_carlo_forecast(nav, n_sim=200, horizon=30)
            mc_mean = float(np.median(sims, axis=0)[-1])
            gbm_expect, _ = black_scholes.black_scholes_gbm_forecast(nav, horizon=30)
            gbm_last = float(gbm_expect[-1])
        except Exception as e:
            mc_mean = None
            gbm_last = None
        details.append({'scheme_code': code, 'weight': float(w), 'mc_30d_median_last': mc_mean, 'gbm_30d_last': gbm_last})
    return {
        'amount': amount,
        'allocations': [{ 'scheme_code': k, 'weight': v, 'allocated_amount': v*amount } for k, v in top_alloc],
        'details': details,
        'n_candidates': len(valid)
    }
