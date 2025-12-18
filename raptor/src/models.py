"""Model utilities: baseline training and prediction helpers."""
import importlib
from pathlib import Path
import logging

logger = logging.getLogger('raptor.models')
ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = ROOT / 'raptor_cache'
CACHE_DIR.mkdir(exist_ok=True)


def train_baseline_rf(X, y, n_estimators=100, random_state=42):
    # import sklearn modules lazily so module import does not fail in minimal envs
    Pipeline = importlib.import_module('sklearn.pipeline').Pipeline
    RF = importlib.import_module('sklearn.ensemble').RandomForestRegressor
    pipe = Pipeline([
        ('est', RF(n_estimators=n_estimators, random_state=random_state, n_jobs=-1))
    ])
    logger.info('Fitting RandomForest baseline')
    pipe.fit(X, y)
    joblib.dump(pipe, CACHE_DIR / 'rf_baseline.joblib')
    logger.info(f'Saved model to {CACHE_DIR / "rf_baseline.joblib"}')
    return pipe


def load_baseline():
    joblib = importlib.import_module('joblib')
    return joblib.load(CACHE_DIR / 'rf_baseline.joblib')


def load_pooled_model():
    """Load pooled RF model artifact saved by train_baselines."""
    p = CACHE_DIR / 'pooled_rf.joblib'
    if not p.exists():
        raise FileNotFoundError('Pooled model not found; run training first')
    joblib = importlib.import_module('joblib')
    return joblib.load(p)


def predict_pooled_one(scheme_code: str, feature_row: dict):
    """Predict single-row target using pooled model artifact.

    feature_row: mapping feature_name -> value (should include numeric features and will set scheme_code_cat)
    Returns predicted target (float)
    """
    artifact = load_pooled_model()
    model = artifact['model']
    feat_cols = artifact['feat_cols']
    scheme_map = artifact.get('scheme_code_map', {})
    # encode scheme_code
    if 'scheme_code_cat' in feat_cols:
        feature_row = dict(feature_row)
        feature_row['scheme_code_cat'] = scheme_map.get(scheme_code, -1)
    # build X in order
    import pandas as pd
    X = pd.DataFrame([feature_row])[feat_cols].fillna(0)
    pred = model.predict(X)[0]
    return float(pred)
