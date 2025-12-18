"""Preprocessing helpers: cleaning NAVs, imputing, rolling stats and saving features."""
from pathlib import Path
import numpy as np
import pandas as pd
import logging
from tqdm.auto import tqdm

logger = logging.getLogger('raptor.preprocessing')
ROOT = Path(__file__).resolve().parents[2]
FEATURES_DIR = ROOT / 'data' / 'features'
FEATURES_DIR.mkdir(parents=True, exist_ok=True)


def clean_nav_df(df: pd.DataFrame) -> pd.DataFrame:
    """Basic cleaning: ensure date, nav numeric, drop duplicates, forward-fill missing."""
    df = df.copy()
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    else:
        raise ValueError('`date` column missing')
    if 'nav' not in df.columns:
        raise ValueError('`nav` column missing')
    df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
    df = df.drop_duplicates(subset=['date'])
    df = df.sort_values('date')
    # forward/backfill small gaps
    df['nav'] = df['nav'].ffill().bfill()
    return df


def make_rolling_features(df: pd.DataFrame, windows=[7,30,90]) -> pd.DataFrame:
    df = df.copy().sort_values('date')
    for w in windows:
        df[f'roll_mean_{w}'] = df['nav'].rolling(w, min_periods=1).mean()
        df[f'roll_std_{w}'] = df['nav'].rolling(w, min_periods=1).std().fillna(0)
    df['ret_1d'] = df['nav'].pct_change().fillna(0)
    df['ret_7d'] = df['nav'].pct_change(7).fillna(0)
    df['log_nav'] = np.log1p(df['nav'])
    return df


def generate_all_features(limit=None):
    """Iterate over raw NAV files and save feature parquet files per scheme."""
    raw_dir = ROOT / 'data' / 'raw' / 'csv'
    files = sorted(raw_dir.glob('nav_*.csv'))
    if limit:
        files = files[:limit]
    for f in tqdm(files, desc='Generating features'):
        code = f.stem.split('_')[-1]
        tmp = pd.read_csv(f, parse_dates=['date']).rename(columns=lambda s: s.strip().lower())
        tmp = clean_nav_df(tmp)
        fg = make_rolling_features(tmp)
        out = FEATURES_DIR / f'features_{code}.parquet'
        fg.to_parquet(out)
    logger.info('Feature generation completed')
