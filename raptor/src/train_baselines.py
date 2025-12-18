"""Train baseline ML/regression models on aggregated features.

This script trains a RandomForest per-scheme (if enough data) and also a pooled model across schemes.
Models are saved to raptor_cache and evaluation metrics are returned.
"""
import logging
from pathlib import Path
import importlib
import numpy as np
import pandas as pd
import importlib
from raptor.src import ingest_aggregate

logger = logging.getLogger('raptor.train')
ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / 'raptor_cache'
MODEL_DIR.mkdir(exist_ok=True)


def train_pooled_rf(horizon: int = 7, n_estimators: int = 100, sample_limit: int = None):
    agg = ingest_aggregate.load_aggregated()
    # Build supervised dataset across schemes
    records = []
    for code, g in agg.groupby('scheme_code'):
        g = g.sort_values('date')
        if len(g) < horizon + 20:
            continue
        df = g.copy()
        df['target_nav'] = df['nav'].shift(-horizon)
        df = df.dropna(subset=['target_nav'])
        df['target_ret'] = df['target_nav'] / df['nav'] - 1
        # take feature columns if present
        feat_cols = [c for c in df.columns if c.startswith('roll_') or c.startswith('ret_') or c=='log_nav']
        if not feat_cols:
            continue
        X = df[feat_cols]
        y = df['target_ret']
        X['scheme_code'] = code
        X['target'] = y
        X['date'] = df['date']
        records.append(X)
        if sample_limit and len(records) >= sample_limit:
            break
    if not records:
        raise ValueError('No training data assembled')
    pool = pd.concat(records, ignore_index=True).dropna()
    # Feature engineering for pooled model: one-hot scheme and scaled numerics handled by simple approach
    # For prototype, encode scheme as categorical codes
    pool['scheme_code_cat'] = pool['scheme_code'].astype('category').cat.codes
    feat_cols = [c for c in pool.columns if c.startswith('roll_') or c.startswith('ret_') or c=='log_nav'] + ['scheme_code_cat']
    X = pool[feat_cols]
    y = pool['target']
    # time-aware train/test split
    pool = pool.sort_values('date')
    split = int(len(pool)*0.8)
    X_train = X.iloc[:split]
    y_train = y.iloc[:split]
    X_test = X.iloc[split:]
    y_test = y.iloc[split:]
    logger.info(f'Training pooled RF on {len(X_train)} samples; testing on {len(X_test)}')
    # import sklearn modules lazily to avoid import errors in environments without sklearn
    sklearn_rf = importlib.import_module('sklearn.ensemble').RandomForestRegressor
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    model = sklearn_rf(n_estimators=n_estimators, n_jobs=-1, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    # Import joblib locally to avoid hard dependency at module import time in test environments
    joblib = importlib.import_module('joblib')
    # Save scheme_code mapping so predictions can be encoded consistently
    scheme_categories = pool['scheme_code'].astype('category').cat.categories.tolist()
    scheme_code_map = {c: int(i) for i, c in enumerate(scheme_categories)}
    joblib.dump({'model': model, 'feat_cols': feat_cols, 'scheme_code_map': scheme_code_map}, MODEL_DIR / 'pooled_rf.joblib')
    logger.info(f'Saved pooled model to {MODEL_DIR / "pooled_rf.joblib"} with MAE={mae:.5f} RMSE={rmse:.5f}')
    return {'mae': mae, 'rmse': rmse, 'model_path': str(MODEL_DIR / 'pooled_rf.joblib')}


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    res = train_pooled_rf(horizon=7, n_estimators=50, sample_limit=50)
    print(res)
