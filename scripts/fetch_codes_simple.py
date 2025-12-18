"""Fetch specific scheme codes synchronously and save CSVs (debug helper)."""
import logging
from pathlib import Path
import pandas as pd

import sys
from pathlib import Path as _P
sys.path.insert(0, str(_P(__file__).resolve().parent))
from mfapi_client import get_nav_history, nav_json_to_df

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('fetch_codes_simple')

RAW_DIR = Path('data/raw')
RAW_DIR.mkdir(parents=True, exist_ok=True)


def save_code(code: int):
    logger.info('Fetching code %s', code)
    j = get_nav_history(code)
    df = nav_json_to_df(j)
    out = RAW_DIR / f'nav_{code}.csv'
    df.to_csv(out, index=False)
    logger.info('Saved %s rows to %s', len(df), out)


if __name__ == '__main__':
    # small sample codes known to exist
    sample = [100121, 100122]
    for c in sample:
        save_code(c)
