"""Data loading utilities for Raptor prototype."""
from pathlib import Path
import pandas as pd
import logging

logger = logging.getLogger('raptor.data_loader')

ROOT = Path(__file__).resolve().parents[2]
CLEANED_PATH = ROOT / 'PS' / 'dataset' / 'cleaned dataset' / 'Cleaned_MF_India_AI.csv'
RAW_NAV_DIR = ROOT / 'data' / 'raw' / 'csv'


def load_cleaned_metadata() -> pd.DataFrame:
    """Load cleaned MF metadata CSV used for recommendations and features."""
    if not CLEANED_PATH.exists():
        raise FileNotFoundError(f"Cleaned dataset not found at {CLEANED_PATH}")
    df = pd.read_csv(CLEANED_PATH)
    logger.info(f'Loaded cleaned metadata with shape {df.shape}')
    return df


def load_nav_timeseries(scheme_code: str) -> pd.DataFrame:
    """Load NAV time series for a given scheme code (file name pattern: nav_<code>.csv)."""
    file = RAW_NAV_DIR / f'nav_{scheme_code}.csv'
    if not file.exists():
        raise FileNotFoundError(f"NAV file not found: {file}")
    df = pd.read_csv(file, parse_dates=['date'])
    df = df.rename(columns=lambda s: s.strip().lower())
    df = df.sort_values('date').reset_index(drop=True)
    return df


def list_available_schemes():
    files = list(RAW_NAV_DIR.glob('nav_*.csv'))
    return [p.stem.split('_')[-1] for p in files]
