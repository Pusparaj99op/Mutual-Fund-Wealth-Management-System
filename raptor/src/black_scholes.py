"""Black-Scholes / GBM helpers for forecasting and simple option-analog predictions."""
import numpy as np
import pandas as pd


def black_scholes_gbm_forecast(nav_series: pd.Series, horizon: int = 30):
    """Return expected price and variance per step using GBM assumption.

    Uses historical log-returns to estimate drift and volatility.
    """
    log_returns = np.log(nav_series).diff().dropna()
    mu = log_returns.mean()
    sigma = log_returns.std()
    s0 = nav_series.iloc[-1]
    # expected value under GBM: E[S_t] = S0 * exp(mu * t)
    times = np.arange(1, horizon + 1)
    expected = s0 * np.exp(mu * times)
    var = (s0 ** 2) * np.exp(2 * mu * times) * (np.exp((sigma ** 2) * times) - 1)
    return expected, var
