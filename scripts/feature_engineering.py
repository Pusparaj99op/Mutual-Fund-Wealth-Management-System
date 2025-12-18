"""Compute features from NAV time series and save per-scheme + combined files.

Features produced:
 - ret_1d: daily pct change
 - logret_1d: daily log return
 - roll_ret_{w}: rolling mean return (window w)
 - roll_vol_{w}: rolling std of returns (window w)
 - ann_ret_{w}: annualized mean return (w -> *252)
 - ann_vol_{w}: annualized volatility (std * sqrt(252))
 - roll_sharpe_{w}: ann_ret / ann_vol (small eps to avoid div0)
 - max_dd_{w}: rolling max drawdown over window w

Saves per-scheme csv to data/features/nav_features_<code>.csv and combined parquet
to data/features/all_nav_features.parquet
"""
from pathlib import Path
import logging
import math
import pandas as pd

ROOT = Path('.')
RAW_DIR = Path('data/raw')
OUT_DIR = Path('data/features')
OUT_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('feature_engineering')

WINDOWS = [7, 21, 63, 252]


def _annualize_return(mean_ret, window):
    # mean_ret is mean per-period (daily); annualize by *252
    return mean_ret * 252


def _annualize_vol(std_ret):
    return std_ret * (252 ** 0.5)


def rolling_max_drawdown(series: pd.Series, window: int):
    # compute rolling max drawdown over lookback window
    # for each date, compute (current / rolling_max - 1)
    roll_max = series.rolling(window, min_periods=1).max()
    dd = series / roll_max - 1.0
    # for reporting, we take the min (most negative) drawdown over the window ending at each date
    roll_dd = dd.rolling(window, min_periods=1).min()
    return roll_dd


def process_file(path: Path):
    df = pd.read_csv(path)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    if 'nav' not in df.columns:
        logger.warning('Skipping %s: no nav column', path)
        return None
    df = df.sort_values('date').reset_index(drop=True)
    df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
    df = df.dropna(subset=['date'])
    if len(df) < 2:
        logger.warning('Skipping %s: not enough rows', path)
        return None

    df['ret_1d'] = df['nav'].pct_change()
    df['logret_1d'] = (df['nav'] / df['nav'].shift(1)).apply(lambda x: math.log(x) if x>0 else float('nan'))

    for w in WINDOWS:
        df[f'roll_ret_{w}'] = df['ret_1d'].rolling(window=w, min_periods=1).mean()
        df[f'roll_vol_{w}'] = df['ret_1d'].rolling(window=w, min_periods=1).std()
        df[f'ann_ret_{w}'] = df[f'roll_ret_{w}'].apply(lambda x: _annualize_return(x, w))
        df[f'ann_vol_{w}'] = df[f'roll_vol_{w}'].apply(lambda x: _annualize_vol(x) if pd.notnull(x) else x)
        # sharpe: ann_ret / ann_vol
        df[f'roll_sharpe_{w}'] = df.apply(lambda r: (r.get(f'ann_ret_{w}', float('nan')) / (r.get(f'ann_vol_{w}', 1e-9) or 1e-9))
                                        if pd.notnull(r.get(f'ann_ret_{w}')) else float('nan'), axis=1)
        # rolling max drawdown
        df[f'max_dd_{w}'] = rolling_max_drawdown(df['nav'], w)

    # attach scheme_code if present in filename
    # filenames expected like nav_<code>.csv
    code = None
    try:
        code = int(path.stem.split('_')[-1])
    except Exception:
        logger.debug('Could not parse code from %s', path.name)

    if code:
        out = OUT_DIR / f'nav_features_{code}.csv'
        df.to_csv(out, index=False)
        logger.info('Wrote features for %s -> %s (rows=%d)', path.name, out, len(df))
    return df.assign(scheme_code=code)


def run_all():
    files = sorted(RAW_DIR.glob('nav_*.csv'))
    if not files:
        logger.error('No raw NAV files found in %s', RAW_DIR)
        return
    combined = []
    for f in files:
        res = process_file(f)
        if res is not None:
            combined.append(res)

    if not combined:
        logger.error('No feature files produced')
        return

    all_df = pd.concat(combined, ignore_index=True)
    # save combined parquet for downstream use
    outp = OUT_DIR / 'all_nav_features.parquet'
    all_df.to_parquet(outp, index=False)
    logger.info('Wrote combined features -> %s (rows=%d)', outp, len(all_df))


if __name__ == '__main__':
    run_all()
