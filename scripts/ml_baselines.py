"""Simple ML baselines for next-day return prediction using RandomForest and XGBoost.

Produces walk-forward evaluation (expanding window) and writes metrics to `reports/models/ml_baseline_metrics.csv`.
"""
from pathlib import Path
import logging
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('ml_baselines')

ROOT = Path('.')
FEATURES = Path('data/features/all_nav_features.parquet')
OUT = Path('reports/models')
OUT.mkdir(parents=True, exist_ok=True)


def prepare_dataset(df: pd.DataFrame, lags=5):
    # predict next-day log return
    df = df.sort_values('date').reset_index(drop=True)
    df['target'] = df['logret_1d'].shift(-1)
    # simple features: recent log returns
    for i in range(1, lags + 1):
        df[f'lag_logret_{i}'] = df['logret_1d'].shift(i)
    # drop rows with NA in target or lags
    df = df.dropna(subset=['target'] + [f'lag_logret_{i}' for i in range(1, lags + 1)])
    return df


def walk_forward_cv(df: pd.DataFrame, model, initial_train=200, step=30):
    preds = []
    trues = []
    n = len(df)
    start = initial_train
    i = start
    while i + step <= n:
        train = df.iloc[:i]
        test = df.iloc[i:i + step]
        Xtr = train[[c for c in train.columns if c.startswith('lag_logret_')]]
        ytr = train['target']
        Xte = test[[c for c in train.columns if c.startswith('lag_logret_')]]
        yte = test['target']
        model.fit(Xtr, ytr)
        p = model.predict(Xte)
        preds.append(p)
        trues.append(yte.values)
        i += step
    if not preds:
        return None
    return np.concatenate(trues), np.concatenate(preds)


def metrics(y_true, y_pred):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    mae = np.mean(np.abs(y_true - y_pred))
    rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
    return {'MAE': mae, 'RMSE': rmse}


def run_all():
    df = pd.read_parquet(FEATURES)
    rows = []
    try:
        from sklearn.ensemble import RandomForestRegressor
    except Exception:
        logger.exception('sklearn is required')
        return
    try:
        from xgboost import XGBRegressor
        has_xgb = True
    except Exception:
        logger.info('xgboost not installed; skipping XGB baseline')
        has_xgb = False

    for code, g in df.groupby('scheme_code'):
        ds = prepare_dataset(g)
        if len(ds) < 300:
            logger.info('Skipping %s: too few rows (%d)', code, len(ds))
            continue
        # RF
        rf = RandomForestRegressor(n_estimators=50, random_state=42)
        res = walk_forward_cv(ds, rf, initial_train=200, step=30)
        if res is None:
            continue
        ytrue, ypred = res
        rows.append({'scheme_code': code, 'model': 'RandomForest', **metrics(ytrue, ypred)})
        # XGB
        if has_xgb:
            xgb = XGBRegressor(n_estimators=50, random_state=42, verbosity=0)
            res = walk_forward_cv(ds, xgb, initial_train=200, step=30)
            if res is not None:
                ytrue, ypred = res
                rows.append({'scheme_code': code, 'model': 'XGBoost', **metrics(ytrue, ypred)})

    out = pd.DataFrame(rows)
    out.to_csv(OUT / 'ml_baseline_metrics.csv', index=False)
    logger.info('Wrote ML baseline metrics -> %s', OUT / 'ml_baseline_metrics.csv')


if __name__ == '__main__':
    run_all()
