"""Monte Carlo simulation utilities for NAV forecasting."""
import numpy as np
import pandas as pd


def monte_carlo_forecast(nav_series: pd.Series, n_sim: int = 500, horizon: int = 30, random_state: int = 42):
    """Generate Monte Carlo simulations of future NAVs using geometric Brownian motion.

    Returns a numpy array of shape (n_sim, horizon) with simulated NAV paths.
    """
    rs = np.random.RandomState(random_state)
    log_returns = np.log(nav_series).diff().dropna()
    mu = log_returns.mean()
    sigma = log_returns.std()
    s0 = nav_series.iloc[-1]
    dt = 1.0
    sims = np.zeros((n_sim, horizon))
    for i in range(n_sim):
        shocks = rs.normal(loc=(mu - 0.5 * sigma ** 2) * dt, scale=sigma * np.sqrt(dt), size=horizon)
        price_path = s0 * np.exp(np.cumsum(shocks))
        sims[i] = price_path
    return sims
