"""Fetch NAV histories for top N schemes (by fund_size_cr) and save CSVs to data/raw/"""
import asyncio
import logging
from pathlib import Path
from typing import List
import difflib

import pandas as pd

from mfapi_client import list_schemes, get_nav_history, nav_json_to_df, batch_fetch_navs, search_schemes

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('fetch_top_navs')

ROOT = Path('.')
DATA_DIR = Path('PS/dataset')
RAW_DIR = Path('data/raw')
RAW_DIR.mkdir(parents=True, exist_ok=True)


def resolve_scheme_codes(names: List[str], schemes_list: List[dict]) -> dict:
    """Return mapping name -> scheme_code using substring matching (best effort)."""
    mapping = {}
    schemes_df = pd.DataFrame(schemes_list)
    schemes_df['schemeName_lower'] = schemes_df['schemeName'].str.lower()

    # helper: normalize names for better matching (strip punctuation, multiple spaces)
    def _normalize(s: str) -> str:
        import re
        if not isinstance(s, str):
            return ''
        s2 = s.lower()
        s2 = re.sub(r"[^a-z0-9]+", ' ', s2)
        s2 = re.sub(r"\s+", ' ', s2).strip()
        return s2

    schemes_df['schemeName_norm'] = schemes_df['schemeName'].apply(_normalize)
    norm_to_row = dict(zip(schemes_df['schemeName_norm'], schemes_df.to_dict('records')))
    for n in names:
        n_lower = n.lower()
        # try exact substring
        hits = schemes_df[schemes_df['schemeName_lower'].str.contains(n_lower, na=False)]
        if len(hits) == 0:
            # try normalized exact name match
            nn = _normalize(n)
            if nn in norm_to_row:
                sel = norm_to_row[nn]
                try:
                    mapping[n] = int(sel.get('schemeCode'))
                    logger.info('Resolved "%s" -> %s via normalized exact match (%s)', n, mapping[n], sel.get('schemeName'))
                    continue
                except Exception:
                    pass
            # try fuzzy match on normalized names
            candidates = difflib.get_close_matches(nn, norm_to_row.keys(), n=3, cutoff=0.6)
            if candidates:
                cand = candidates[0]
                sel = norm_to_row[cand]
                try:
                    mapping[n] = int(sel.get('schemeCode'))
                    logger.info('Resolved "%s" -> %s via fuzzy match (%s)', n, mapping[n], sel.get('schemeName'))
                    continue
                except Exception:
                    pass
            # fallback: use search endpoint (best-effort)
            logger.info('No substring match for "%s" in /mf list; trying /mf/search', n)
            try:
                s = search_schemes(n)
                if isinstance(s, list) and s:
                    # pick first result
                    mapping[n] = int(s[0].get('schemeCode'))
                    continue
            except Exception:
                logger.exception('Search fallback failed for %s', n)
            logger.info('Fallback failed for "%s"; skipping', n)
            continue
        # pick the hit with largest overlap (simple heuristic: longest name)
        sel = hits.sort_values('schemeName', key=lambda s: s.str.len(), ascending=False).iloc[0]
        mapping[n] = int(sel['schemeCode'])
    return mapping


async def fetch_and_save(codes: List[int], concurrency: int = 10):
    results = await batch_fetch_navs(codes, concurrency=concurrency)
    for j in results:
        # ensure we have valid data and meta
        if not isinstance(j, dict) or 'data' not in j:
            # avoid dumping large payloads to logs -- print a concise summary instead
            logger.warning('Invalid response (not a dict or missing data). Keys: %s',
                           list(j.keys()) if isinstance(j, dict) else type(j))
            continue
        meta = j.get('meta') or {}
        # try to get scheme code safely
        code = None
        if 'schemeCode' in meta and meta['schemeCode']:
            try:
                code = int(meta['schemeCode'])
            except Exception:
                code = None
        if code is None:
            # fallback to any top-level scheme_code field
            sc = j.get('scheme_code') or j.get('schemeCode')
            try:
                code = int(sc)
            except Exception:
                # Avoid logging entire response (very large). Log a concise summary.
                logger.warning('Could not determine scheme code for response; skipping. '
                               'meta_keys=%s data_len=%s', list(meta.keys()),
                               len(j.get('data') if isinstance(j.get('data'), list) else []))
                continue
        try:
            df = nav_json_to_df(j)
        except Exception:
            logger.exception('Failed to parse NAV JSON for scheme %s; skipping', code)
            continue
        name = (meta.get('schemeName') or f'scheme_{code}').replace('/', '_')
        out = RAW_DIR / f'nav_{code}.csv'
        df.to_csv(out, index=False)
        logger.info('Saved %s rows for %s (%s) -> %s', len(df), code, name, out)


def main(top_n: int = 20):
    master = pd.read_csv(DATA_DIR / 'MF_India_AI.csv')
    master['fund_size_cr'] = pd.to_numeric(master['fund_size_cr'], errors='coerce')
    top = master.sort_values('fund_size_cr', ascending=False).head(top_n)
    names = top['scheme_name'].tolist()

    # get schemes list from API
    logger.info('Fetching schemes list from API')
    schemes = list_schemes()

    mapping = resolve_scheme_codes(names, schemes)
    logger.info('Name->Code mapping: %s', mapping)
    codes = list(mapping.values())
    logger.info('Resolved %d/%d scheme names -> codes', len(codes), len(names))

    if not codes:
        logger.error('No scheme codes resolved; exiting')
        return

    asyncio.run(fetch_and_save(codes, concurrency=10))


if __name__ == '__main__':
    main(top_n=20)
