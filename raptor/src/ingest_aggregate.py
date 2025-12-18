"""Build an aggregated dataset from per-scheme feature files.

This module looks for per-scheme feature parquet files under `data/features/` (features_<code>.parquet)
and creates a long-form aggregated parquet at `data/processed/aggregated_features.parquet`.
"""
from pathlib import Path
import pandas as pd
import logging
from typing import Optional

logger = logging.getLogger('raptor.ingest')
ROOT = Path(__file__).resolve().parents[2]
FEATURES_DIR = ROOT / 'data' / 'features'
PROCESSED_DIR = ROOT / 'data' / 'processed'
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
OUT_PATH = PROCESSED_DIR / 'aggregated_features.parquet'


def build_aggregated_dataset(min_observations: int = 250, limit: Optional[int] = None) -> pd.DataFrame:
    """Aggregate per-scheme feature files into a single DataFrame.

    Args:
        min_observations: minimum number of observations required to include a scheme
        limit: optional number of schemes to process (for faster runs)
    Returns:
        Aggregated DataFrame
    """
    files = sorted(FEATURES_DIR.glob('features_*.parquet'))
    if limit:
        files = files[:limit]
    if not files:
        raise FileNotFoundError(f'No feature files found in {FEATURES_DIR}; run preprocessing.generate_all_features() first')
    parts = []
    for f in files:
        code = f.stem.split('_')[-1]
        df = pd.read_parquet(f)
        if len(df) < min_observations:
            logger.info(f'Skipping {code}: not enough observations ({len(df)})')
            continue
        df = df.copy()
        df['scheme_code'] = code
        parts.append(df)
    if not parts:
        raise ValueError('No scheme met the min_observations requirement')
    agg = pd.concat(parts, ignore_index=True)
    agg = agg.sort_values(['scheme_code', 'date']).reset_index(drop=True)
    agg.to_parquet(OUT_PATH)
    logger.info(f'Aggregated dataset saved to {OUT_PATH} with shape {agg.shape}')
    return agg


def load_aggregated() -> pd.DataFrame:
    if not OUT_PATH.exists():
        raise FileNotFoundError('Aggregated dataset not found; build it using build_aggregated_dataset()')
    return pd.read_parquet(OUT_PATH)
