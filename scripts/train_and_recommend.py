"""Train RandomForest on fund-level features, perform KMeans risk profiling,
and expose a rule-based recommender that returns Top-3 fund suggestions.

Usage (examples):
  python scripts/train_and_recommend.py --train
  python scripts/train_and_recommend.py --recommend --category Equity --tenure 5 --amount 100000

Outputs:
 - models/rf_return_1yr.pkl  (joblib)
 - models/preprocessor.pkl    (joblib) : dict with encoders and feature columns
 - reports/models/recommendations_example.csv
"""
from pathlib import Path
import logging
import argparse
import joblib
import numpy as np
import pandas as pd
import json
from typing import Tuple

from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

ROOT = Path('.')
DATA_META = Path('PS/dataset/cleaned dataset/Cleaned_MF_India_AI.csv')
OUT_DIR = Path('models')
OUT_DIR.mkdir(parents=True, exist_ok=True)
LOG = logging.getLogger('train_and_recommend')
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

SCHEMES_CACHE = Path('data/schemes_list.json')
FEATURES_PARQUET = Path('data/features/all_nav_features.parquet')


def load_meta():
    df = pd.read_csv(DATA_META)
    LOG.info('Loaded metadata rows=%d', len(df))
    return df


def prepare_features(df: pd.DataFrame):
    """Prepare a fund-level feature matrix and target (returns_1yr).

    Returns X (DataFrame), y (Series), and a dict with preprocessing metadata.
    """
    # keep a copy of identifiers
    df = df.copy()
    # target
    y = pd.to_numeric(df['returns_1yr'], errors='coerce')

    # numeric features to use
    numeric = ['alpha', 'beta', 'expense_ratio', 'fund_age_yr', 'fund_size_cr',
               'log_fund_size', 'min_lumpsum', 'min_sip', 'rating', 'sd', 'sharpe', 'sortino']
    # ensure numeric
    for c in numeric:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')

    # categories: keep 'category' and top N AMCs
    cat_cols = []
    if 'category' in df.columns:
        cat_d = pd.get_dummies(df['category'].fillna('UNKNOWN'), prefix='cat')
        cat_cols = list(cat_d.columns)
        df = pd.concat([df, cat_d], axis=1)

    # AMC: one-hot for top 10 AMCs (others -> OTHER_AMC)
    if 'amc_name' in df.columns:
        top_amcs = df['amc_name'].value_counts().head(10).index.tolist()
        df['amc_top'] = df['amc_name'].apply(lambda x: x if x in top_amcs else 'OTHER_AMC')
        amc_d = pd.get_dummies(df['amc_top'], prefix='amc')
        amc_cols = list(amc_d.columns)
        df = pd.concat([df, amc_d], axis=1)
    else:
        amc_cols = []

    # final feature list
    # attempt to augment with aggregated time-series features if available
    if FEATURES_PARQUET.exists():
        try:
            nav_aggs = aggregate_nav_features(FEATURES_PARQUET)
            LOG.info('Aggregated nav features for %d scheme_codes', len(nav_aggs))
            df = merge_nav_aggs_into_meta(df, nav_aggs)
            # incorporate new agg columns into consideration
            agg_cols = [c for c in nav_aggs.columns if c not in ['scheme_code', 'schemeName']]
        except Exception as e:
            LOG.exception('Failed to aggregate nav features: %s', e)
            agg_cols = []
    else:
        agg_cols = []

    # only keep aggregated columns that were actually merged into meta
    agg_cols_present = [c for c in agg_cols if c in df.columns]
    if agg_cols and not agg_cols_present:
        LOG.info('No NAV aggregated columns merged into metadata (no name matches found)')
    feature_cols = [c for c in numeric if c in df.columns] + cat_cols + amc_cols + agg_cols_present
    X = df[feature_cols].copy()

    # drop rows with NA target or all-NA features
    mask = (~y.isna()) & (~X.isna().all(axis=1))
    X = X.loc[mask]
    y = y.loc[mask]

    # fill small NAs with median
    for c in X.columns:
        if X[c].isna().any():
            X[c] = X[c].fillna(X[c].median())

    prep = {
        'feature_cols': feature_cols,
        'numeric': [c for c in numeric if c in df.columns],
        'category_cols': cat_cols,
        'amc_cols': amc_cols,
        'id_cols': ['scheme_name', 'amc_name'] if 'scheme_name' in df.columns else []
    }
    return X, y, prep, df


def aggregate_nav_features(p: Path) -> pd.DataFrame:
    """Read per-date nav features parquet and compute per-scheme aggregates.

    Returns a DataFrame with columns: scheme_code, schemeName (if available via API),
    recent_ann_ret_252, mean_ann_ret_252, mean_sharpe_252, min_max_dd_252, mean_ann_vol_252
    """
    df = pd.read_parquet(p)
    out = []
    for code, g in df.groupby('scheme_code'):
        g = g.sort_values('date')
        recent_ann = g['ann_ret_252'].dropna().iloc[-1] if g['ann_ret_252'].dropna().size>0 else np.nan
        mean_ann = g['ann_ret_252'].mean()
        mean_sharpe = g['roll_sharpe_252'].mean()
        min_dd = g['max_dd_252'].min()
        mean_ann_vol = g['ann_vol_252'].mean()
        out.append({'scheme_code': int(code), 'recent_ann_ret_252': recent_ann,
                    'mean_ann_ret_252': mean_ann, 'mean_sharpe_252': mean_sharpe,
                    'min_max_dd_252': min_dd, 'mean_ann_vol_252': mean_ann_vol})
    nav_aggs = pd.DataFrame(out)
    # try to attach schemeName from cached schemes list or API
    try:
        scheme_map = load_or_fetch_schemes()
        nav_aggs['schemeName'] = nav_aggs['scheme_code'].apply(lambda c: scheme_map.get(str(int(c)), ''))
    except Exception:
        LOG.exception('Could not attach schemeName mapping')
        nav_aggs['schemeName'] = ''
    return nav_aggs


def load_or_fetch_schemes() -> dict:
    """Return mapping schemeCode (string) -> schemeName. Caches locally in JSON."""
    try:
        if SCHEMES_CACHE.exists():
            with SCHEMES_CACHE.open('r') as f:
                return json.load(f)
        # fetch from API
        from mfapi_client import list_schemes
        schemes = list_schemes()
        mapping = {}
        for s in schemes:
            code = s.get('schemeCode') or s.get('scheme_code')
            name = s.get('schemeName') or s.get('scheme_name')
            if code and name:
                mapping[str(int(code))] = name
        with SCHEMES_CACHE.open('w') as f:
            json.dump(mapping, f)
        return mapping
    except Exception:
        LOG.exception('Failed to fetch schemes list from API')
        return {}


def merge_nav_aggs_into_meta(meta_df: pd.DataFrame, nav_aggs: pd.DataFrame) -> pd.DataFrame:
    """Merge aggregated nav features into metadata using substring/fuzzy match on scheme names."""
    meta = meta_df.copy()
    # simple substring match: for each nav row, find metadata rows where scheme_name contains schemeName or vice versa
    for _, r in nav_aggs.iterrows():
        sname = (r.get('schemeName') or '').lower()
        if not sname:
            continue
        mask = meta['scheme_name'].str.lower().str.contains(sname, na=False)
        if mask.any():
            for c in [k for k in r.index if k not in ['scheme_code', 'schemeName']]:
                meta.loc[mask, c] = r[c]
        else:
            # try reverse: schemeName contains scheme_name
            mask2 = meta['scheme_name'].apply(lambda x: sname in str(x).lower())
            if mask2.any():
                for c in [k for k in r.index if k not in ['scheme_code', 'schemeName']]:
                    meta.loc[mask2, c] = r[c]
    return meta


def train_rf(X, y):
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(Xtr, ytr)
    yp = model.predict(Xte)
    mae = mean_absolute_error(yte, yp)
    rmse = mean_squared_error(yte, yp, squared=False)
    LOG.info('RF trained: MAE=%.4f RMSE=%.4f (test_rows=%d)', mae, rmse, len(yte))
    return model, {'mae': mae, 'rmse': rmse}


def fit_kmeans_risk(X, n_clusters=3):
    """Fit KMeans on scaled risk-related columns and return labels and scaler.
    We'll use volatility-related measures (sd, beta, expense_ratio, fund_age_yr, log_fund_size).
    """
    risk_feats = [c for c in ['sd', 'beta', 'expense_ratio', 'fund_age_yr', 'log_fund_size'] if c in X.columns]
    scaler = StandardScaler()
    arr = scaler.fit_transform(X[risk_feats])
    k = KMeans(n_clusters=n_clusters, random_state=42)
    labels = k.fit_predict(arr)
    # compute avg sd per cluster to order them low->high risk
    import pandas as pd
    dfc = pd.DataFrame(arr, columns=risk_feats)
    dfc['cluster'] = labels
    # map cluster index -> risk name by mean(sd)
    means = dfc.groupby('cluster')[risk_feats[0]].mean().sort_values().index.tolist()
    risk_map = {}
    names = ['Low', 'Medium', 'High']
    for i, cl in enumerate(means):
        risk_map[cl] = names[i] if i < len(names) else f'Risk_{i}'
    LOG.info('KMeans risk mapping: %s', risk_map)
    return labels, scaler, k, risk_map


def recommend(df_meta, X, model, scaler_k, kmeans, prep, category=None, amc=None, amount=0, tenure=5, topn=3):
    """Rule-based recommendation: map tenure -> tolerance and select funds accordingly.
    Returns topn rows (DataFrame) with predictions and risk cluster labels.
    """
    # determine user risk tolerance from tenure
    if tenure < 2:
        tol = 'Low'
    elif tenure < 5:
        tol = 'Medium'
    else:
        tol = 'High'

    # Predict on full X
    preds = model.predict(X)
    df_out = X.copy()
    df_out['pred_return_1yr'] = preds
    # restore identifier columns from df_meta (aligned earlier in prepare_features return df)
    df_ids = df_meta.loc[X.index]
    if 'scheme_name' in df_ids.columns:
        df_out['scheme_name'] = df_ids['scheme_name'].values
    if 'amc_name' in df_ids.columns:
        df_out['amc_name'] = df_ids['amc_name'].values
    if 'returns_1yr' in df_ids.columns:
        df_out['returns_1yr'] = df_ids['returns_1yr'].values

    # risk cluster assignment
    # use the same risk features used when fitting kmeans
    risk_feats = [c for c in ['sd', 'beta', 'expense_ratio', 'fund_age_yr', 'log_fund_size'] if c in X.columns]
    arr = scaler_k.transform(X[risk_feats])
    clusters = kmeans.predict(arr)
    df_out['cluster'] = clusters
    # try to map cluster to name using cluster ordering by centroid sd (this mapping is in kmeans object? if not, infer)
    # We will compute mean sd per cluster and map
    cl_means = df_out.groupby('cluster')['sd'].mean().sort_values()
    cluster_order = cl_means.index.tolist()
    cluster_name = {}
    names = ['Low', 'Medium', 'High']
    for i, cl in enumerate(cluster_order):
        cluster_name[cl] = names[i] if i < len(names) else f'Risk_{i}'
    df_out['risk_name'] = df_out['cluster'].map(cluster_name)

    # filter by category/amc if provided
    candidates = df_out
    if category:
        # try to match any feature cat_{category}
        col = f'cat_{category}'
        if col in candidates.columns:
            candidates = candidates[candidates[col] == 1]
        else:
            # try substring match in scheme_name
            candidates = candidates[candidates['scheme_name'].str.contains(category, case=False, na=False)]
    if amc:
        candidates = candidates[candidates['amc_name'].str.contains(amc, case=False, na=False)]

    # match risk tolerance
    cand = candidates[candidates['risk_name'] == tol]
    if len(cand) < topn:
        LOG.info('Not enough candidates for strict risk=%s, relaxing', tol)
        cand = candidates

    # rank by predicted return then rating
    if 'rating' in cand.columns:
        cand = cand.sort_values(['pred_return_1yr', 'rating'], ascending=[False, False])
    else:
        cand = cand.sort_values('pred_return_1yr', ascending=False)

    cols = ['scheme_name', 'amc_name', 'pred_return_1yr', 'returns_1yr', 'risk_name', 'sd', 'rating', 'expense_ratio']
    exist_cols = [c for c in cols if c in cand.columns]
    return cand[exist_cols].head(topn)


def main(args):
    df = load_meta()
    X, y, prep, df_full = prepare_features(df)

    if args.train:
        model, stats = train_rf(X, y)
        joblib.dump(model, OUT_DIR / 'rf_return_1yr.pkl')
        joblib.dump(prep, OUT_DIR / 'preprocessor.pkl')
        LOG.info('Saved RF and preprocessor to %s', OUT_DIR)

        # fit kmeans on X
        labels, scaler_k, k, risk_map = fit_kmeans_risk(X, n_clusters=3)
        joblib.dump({'kmeans': k, 'scaler': scaler_k, 'risk_map': risk_map}, OUT_DIR / 'kmeans_risk.pkl')
        LOG.info('Saved KMeans risk model')

        # save a small example recommendations CSV
        rec = recommend(df_full, X, model, scaler_k, k, prep, category=None, tenure=5)
        outp = Path('reports/models')
        outp.mkdir(parents=True, exist_ok=True)
        rec.to_csv(outp / 'recommendations_example.csv', index=False)
        LOG.info('Wrote example recommendations -> %s', outp / 'recommendations_example.csv')

    if args.recommend:
        # load models if not in memory
        mpath = OUT_DIR / 'rf_return_1yr.pkl'
        prep_path = OUT_DIR / 'preprocessor.pkl'
        km_path = OUT_DIR / 'kmeans_risk.pkl'
        if not mpath.exists() or not prep_path.exists() or not km_path.exists():
            LOG.error('Models not found; run with --train first')
            return
        model = joblib.load(mpath)
        prep = joblib.load(prep_path)
        krec = joblib.load(km_path)
        rec = recommend(df_full, X, model, krec['scaler'], krec['kmeans'], prep,
                        category=args.category, amc=args.amc, amount=args.amount, tenure=args.tenure, topn=3)
        print(rec.to_string(index=False))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--train', action='store_true', help='Train models and save artifacts')
    p.add_argument('--recommend', action='store_true', help='Run recommendation (needs trained models)')
    p.add_argument('--category', type=str, help='Filter by category')
    p.add_argument('--amc', type=str, help='Filter by AMC name substring')
    p.add_argument('--amount', type=float, default=0, help='Investment amount (INR)')
    p.add_argument('--tenure', type=float, default=5, help='Investment tenure (years)')
    args = p.parse_args()
    main(args)
