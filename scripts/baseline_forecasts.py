"""Baseline time-series forecasting (naive, seasonal-naive, ARIMA, ETS) with rolling evaluation.

Saves per-scheme forecasts and a summary metrics CSV under `reports/models/`.
"""
from pathlib import Path
import logging
import numpy as np
import pandas as pd
from typing import Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('baseline_forecasts')

ROOT = Path('.')
FEATURES = Path('data/features/all_nav_features.parquet')
OUT = Path('reports/models')
OUT.mkdir(parents=True, exist_ok=True)


def split_train_test(series: pd.Series, test_horizon: int = 30) -> Tuple[pd.Series, pd.Series]:
    """Simple last-window split: last `test_horizon` points are test."""
    s = series.dropna()
    if len(s) <= test_horizon + 10:
        raise ValueError('Series too short for test split')
    train = s.iloc[:-test_horizon]
    test = s.iloc[-test_horizon:]
    return train, test


def rolling_backtest(series: pd.Series, methods: dict, test_horizon: int = 30,
                     initial_train: int = 200, step: int = 30) -> pd.DataFrame:
    """Perform rolling-origin backtest and return a dataframe with one row per prediction.

    Columns: date, method, origin_date, pred, actual
    """
    s = series.dropna()
    n = len(s)
    rows = []
    if n <= initial_train + test_horizon:
        raise ValueError('Series too short for rolling backtest')
    for start in range(initial_train, n - test_horizon + 1, step):
        train = s.iloc[:start]
        test = s.iloc[start:start + test_horizon]
        origin_date = train.index[-1]
        steps = len(test)
        for name, fn in methods.items():
            try:
                preds = fn(train, steps)
            except Exception:
                logger.exception('Method %s failed at origin %s', name, origin_date)
                preds = [train.iloc[-1]] * steps
            for i, dt in enumerate(test.index):
                # use positional access to avoid index label issues
                actual_val = float(test.iat[i])
                pred_val = float(np.asarray(preds)[i])
                rows.append({'date': dt, 'method': name, 'origin_date': origin_date, 'pred': pred_val, 'actual': actual_val})
    return pd.DataFrame(rows)


def naive_forecast(train: pd.Series, steps: int):
    # naive: last observed value
    last = train.iloc[-1]
    return np.repeat(last, steps)


def seasonal_naive(train: pd.Series, steps: int, season: int = 252):
    # use value from same season in previous period if available
    if len(train) < season:
        return naive_forecast(train, steps)
    vals = []
    for h in range(1, steps + 1):
        idx = -h - season + 1
        if abs(idx) <= len(train):
            vals.append(train.iloc[idx])
        else:
            vals.append(train.iloc[-1])
    return np.array(list(reversed(vals)))


def arima_forecast(train: pd.Series, steps: int):
    try:
        from statsmodels.tsa.arima.model import ARIMA
    except Exception:
        logger.exception('statsmodels ARIMA not available')
        return naive_forecast(train, steps)

    # small grid search for p,d,q in 0..2
    best_aic = np.inf
    best_model = None
    for p in range(3):
        for d in range(3):
            for q in range(3):
                try:
                    m = ARIMA(train, order=(p, d, q)).fit(method_kwargs={"warn_convergence": False})
                    if m.aic < best_aic:
                        best_aic = m.aic
                        best_model = m
                except Exception:
                    continue
    if best_model is None:
        return naive_forecast(train, steps)
    pred = best_model.forecast(steps)
    return pred


def ets_forecast(train: pd.Series, steps: int):
    try:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing
    except Exception:
        logger.exception('statsmodels ETS not available')
        return naive_forecast(train, steps)
    try:
        m = ExponentialSmoothing(train, trend='add', seasonal=None, damped_trend=True).fit()
        return m.forecast(steps)
    except Exception:
        try:
            m = ExponentialSmoothing(train, trend=None, seasonal=None).fit()
            return m.forecast(steps)
        except Exception:
            return naive_forecast(train, steps)


def metrics(y_true: np.ndarray, y_pred: np.ndarray):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    mae = np.mean(np.abs(y_true - y_pred))
    rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
    mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-9))) * 100
    return {'MAE': mae, 'RMSE': rmse, 'MAPE': mape}


def evaluate_series_rolling(series: pd.Series, test_horizon: int = 30, initial_train: int = 200, step: int = 30):
    methods = {
        'naive': naive_forecast,
        'seasonal_naive': seasonal_naive,
        'arima': arima_forecast,
        'ets': ets_forecast,
    }
    try:
        preds_df = rolling_backtest(series, methods, test_horizon=test_horizon, initial_train=initial_train, step=step)
    except ValueError as e:
        logger.warning('Skipping series rolling eval: %s', e)
        return None

    # compute aggregated metrics per method
    out = {}
    for name, g in preds_df.groupby('method'):
        m = metrics(g['actual'].values, g['pred'].values)
        out[name] = m
    return out, preds_df


def run_all():
    df = pd.read_parquet(FEATURES)
    # group by scheme_code present in features
    out_rows = []
    for code, g in df.groupby('scheme_code'):
        s = g.sort_values('date').set_index(pd.to_datetime(g.sort_values('date')['date'], dayfirst=True))['nav']
        logger.info('Rolling-evaluating scheme %s (rows=%d)', code, len(s))
        res = evaluate_series_rolling(s, test_horizon=30, initial_train=200, step=30)
        if res is None:
            continue
        metrics_dict, preds_df = res

        # save per-scheme forecast table
        out_forecast = OUT / f'forecasts_{code}.csv'
        preds_df.to_csv(out_forecast, index=False)
        logger.info('Wrote rolling forecasts -> %s', out_forecast)

        for method, mets in metrics_dict.items():
            out_rows.append({'scheme_code': code, 'method': method, **mets})

    out_df = pd.DataFrame(out_rows)
    out_df.to_csv(OUT / 'baseline_forecast_metrics.csv', index=False)
    logger.info('Wrote baseline metrics -> %s', OUT / 'baseline_forecast_metrics.csv')


if __name__ == '__main__':
    run_all()
