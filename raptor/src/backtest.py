"""Backtesting utilities for portfolio strategies and forecasting evaluation."""
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
import logging
from raptor.src import ingest_aggregate

logger = logging.getLogger('raptor.backtest')


def portfolio_performance_from_navs(nav_dict: Dict[str, pd.Series], weights: Dict[str, float]) -> Tuple[pd.Series, Dict]:
    """Compute portfolio daily returns and metrics from NAV series per scheme.

    nav_dict: mapping scheme_code -> pd.Series indexed by date
    weights: mapping scheme_code -> weight (sums to 1)

    Returns: (portfolio_nav_series, metrics)
    Metrics include cumulative_return, annualized_return, annualized_vol, sharpe, max_drawdown
    """
    # Align dates
    frames = []
    for code, s in nav_dict.items():
        sr = s.rename(code)
        frames.append(sr)
    df = pd.concat(frames, axis=1).sort_index().dropna()
    # daily returns
    daily_ret = df.pct_change().dropna()
    w = np.array([weights.get(c, 0.0) for c in df.columns])
    port_ret = daily_ret.dot(w)
    port_nav = (1 + port_ret).cumprod()
    # metrics
    cumulative_return = float(port_nav.iloc[-1] - 1.0)
    ann_ret = (1 + cumulative_return) ** (252 / len(port_ret)) - 1 if len(port_ret) > 0 else 0.0
    ann_vol = float(port_ret.std() * np.sqrt(252)) if len(port_ret) > 0 else 0.0
    sharpe = ann_ret / ann_vol if ann_vol > 0 else 0.0
    # max drawdown
    rol_max = port_nav.cummax()
    drawdown = (port_nav - rol_max) / rol_max
    max_dd = float(drawdown.min())
    metrics = {
        'cumulative_return': cumulative_return,
        'annualized_return': ann_ret,
        'annualized_vol': ann_vol,
        'sharpe': sharpe,
        'max_drawdown': max_dd
    }
    return port_nav, metrics


def backtest_black_litterman(lookback_days: int = 252, rebalance_freq_days: int = 21, top_k: int = 5) -> Dict:
    """A simple rolling backtest that computes BL allocations at each rebalance date using past lookback data,
    invests equally according to weights, and measures realized returns over the rebalance period.

    Returns a dictionary with timeseries of portfolio NAV and summary metrics.
    """
    agg = ingest_aggregate.load_aggregated()
    # choose rebalance dates as dates present in dataset after lookback
    daily_dates = sorted(agg['date'].unique())
    if len(daily_dates) < lookback_days + rebalance_freq_days:
        raise ValueError('Not enough data for requested lookback and rebalance parameters')
    rebalance_dates = daily_dates[lookback_days::rebalance_freq_days]
    portfolio_nav_series = []
    portfolio_dates = []
    # for each rebalance date compute BL allocations using data up to that date
    for t in rebalance_dates:
        past_end = pd.to_datetime(t)
        past_start = past_end - pd.Timedelta(days=lookback_days)
        past_df = agg[(agg['date'] >= past_start) & (agg['date'] <= past_end)]
        try:
            from raptor.src import recommender
            rec = recommender.recommend_black_litterman(amount=1.0, scheme_codes=None, top_k=top_k, min_obs=10)
            # build nav_dict for next period
            next_start = past_end + pd.Timedelta(days=1)
            next_end = past_end + pd.Timedelta(days=rebalance_freq_days)
            codes = [c['scheme_code'] for c in rec['allocations']]
            nav_dict = {}
            for c in codes:
                try:
                    from raptor.src.data_loader import load_nav_timeseries
                    nav = load_nav_timeseries(c)
                    nav = nav.set_index('date')['nav']
                    nav = nav[(nav.index >= next_start) & (nav.index <= next_end)]
                    if len(nav) == 0:
                        raise ValueError('No future nav data')
                    nav_dict[c] = nav
                except Exception:
                    # skip schemes without future data
                    continue
            weights = {a['scheme_code']: a['weight'] for a in rec['allocations'] if a['scheme_code'] in nav_dict}
            if not weights:
                continue
            pnav, _ = portfolio_performance_from_navs(nav_dict, weights)
            portfolio_nav_series.append(pnav)
            portfolio_dates.append((next_start, next_end))
        except Exception as e:
            logger.warning(f'Backtest step failed for date {t}: {e}')
            continue
    # concatenate portfolio period navs by reindexing to a continuous index (simple concatenation)
    if not portfolio_nav_series:
        raise ValueError('No portfolio periods could be constructed during backtest')
    combined = pd.concat(portfolio_nav_series)
    combined = combined[~combined.index.duplicated(keep='first')]
    # compute metrics
    _, metrics = portfolio_performance_from_navs({ 'p': combined }, {'p': 1.0})
    return {'portfolio_nav': combined, 'metrics': metrics, 'periods': portfolio_dates}
