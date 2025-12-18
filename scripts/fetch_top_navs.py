"""Fetch NAV histories for top N schemes (by fund_size_cr) and save CSVs to data/raw/"""
import asyncio
import logging
from pathlib import Path
from typing import List
import difflib

import pandas as pd

from mfapi_client import list_schemes, get_nav_history, nav_json_to_df, batch_fetch_navs, search_schemes
import json
import argparse

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


async def fetch_and_save(codes: List[int], concurrency: int = 10, save_json: bool = False, overwrite: bool = False,
                         csv_dir: Path = RAW_DIR, json_dir: Path = RAW_DIR):
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
            # fallback to any scheme_code field in meta or top-level
            sc = None
            if isinstance(meta, dict):
                sc = meta.get('scheme_code') or meta.get('schemeCode') or meta.get('scheme_code_')
            if sc is None:
                sc = j.get('scheme_code') or j.get('schemeCode') or j.get('scheme_code')
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
        csv_dir.mkdir(parents=True, exist_ok=True)
        json_dir.mkdir(parents=True, exist_ok=True)
        csv_out = Path(csv_dir) / f'nav_{code}.csv'
        json_out = Path(json_dir) / f'nav_{code}.json'

        # CSV
        if csv_out.exists() and not overwrite:
            logger.info('CSV exists for %s (%s); skipping CSV write (use --overwrite to force)', code, name)
        else:
            df.to_csv(csv_out, index=False)
            logger.info('Saved %s rows for %s (%s) -> %s', len(df), code, name, csv_out)

        # JSON
        if save_json:
            if json_out.exists() and not overwrite:
                logger.info('JSON exists for %s (%s); skipping JSON write (use --overwrite to force)', code, name)
            else:
                try:
                    # write pretty JSON with ASCII disabled for names
                    with open(json_out, 'w', encoding='utf-8') as fh:
                        json.dump(j, fh, ensure_ascii=False, indent=2)
                    logger.info('Saved JSON for %s (%s) -> %s', code, name, json_out)
                except Exception:
                    logger.exception('Failed to write JSON for %s -> %s', code, json_out)


def main():
    parser = argparse.ArgumentParser(description='Fetch NAV histories and save CSV/JSON to data/raw')
    parser.add_argument('--top-n', type=int, default=0, help='If >0, select top N schemes by fund_size_cr from PS/dataset/MF_India_AI.csv')
    parser.add_argument('--names', type=str, help='Comma-separated list of scheme names to fetch (best-effort matching)')
    parser.add_argument('--names-file', type=str, help='Path to a file with scheme names (one per line)')
    parser.add_argument('--codes', type=str, help='Comma-separated scheme codes to fetch directly (integers)')
    parser.add_argument('--all', action='store_true', help='Fetch NAVs for all schemes listed in PS/dataset/MF_India_AI.csv')
    parser.add_argument('--csv-dir', type=str, default=str(RAW_DIR / 'csv'), help='Directory to save CSV files')
    parser.add_argument('--json-dir', type=str, default=str(RAW_DIR / 'json'), help='Directory to save JSON files')
    parser.add_argument('--batch-size', type=int, default=200, help='Process scheme codes in batches of this many')
    parser.add_argument('--save-json', action='store_true', help='Also save raw JSON responses alongside CSV')
    parser.add_argument('--concurrency', type=int, default=10, help='Concurrency for async fetching')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing files')
    args = parser.parse_args()

    names = []
    codes = []

    if args.names:
        names = [n.strip() for n in args.names.split(',') if n.strip()]
    if args.names_file:
        p = Path(args.names_file)
        if p.exists():
            with p.open() as fh:
                names.extend([l.strip() for l in fh if l.strip()])
        else:
            logger.error('Names file %s does not exist', args.names_file)
            return
    if args.all:
        master = pd.read_csv(DATA_DIR / 'MF_India_AI.csv')
        names = master['scheme_name'].dropna().astype(str).tolist()
        logger.info('Will fetch NAVs for %d scheme names from dataset', len(names))
    if args.top_n and args.top_n > 0:
        master = pd.read_csv(DATA_DIR / 'MF_India_AI.csv')
        master['fund_size_cr'] = pd.to_numeric(master['fund_size_cr'], errors='coerce')
        top = master.sort_values('fund_size_cr', ascending=False).head(args.top_n)
        names.extend(top['scheme_name'].tolist())

    if args.codes:
        try:
            codes = [int(c.strip()) for c in args.codes.split(',') if c.strip()]
        except Exception:
            logger.exception('Failed to parse codes from --codes')
            return

    # get schemes list from API if we need to resolve names
    schemes = None
    mapping = {}
    if names and not codes:
        logger.info('Fetching schemes list from API for name resolution')
        schemes = list_schemes()
        mapping = resolve_scheme_codes(names, schemes)
        logger.info('Name->Code mapping resolved for %d names (showing up to 10): %s', len(mapping), dict(list(mapping.items())[:10]))
        codes = list(mapping.values())

    if not codes:
        logger.error('No scheme codes to fetch; nothing to do')
        return

    logger.info('Resolved %d schemes to fetch', len(codes))
    csv_dir = Path(args.csv_dir)
    json_dir = Path(args.json_dir)
    batch_size = max(1, args.batch_size)
    for i in range(0, len(codes), batch_size):
        batch = codes[i:i + batch_size]
        logger.info('Processing batch %d-%d (%d schemes)', i + 1, i + len(batch), len(batch))
        asyncio.run(fetch_and_save(batch, concurrency=args.concurrency, save_json=args.save_json,
                                   overwrite=args.overwrite, csv_dir=csv_dir, json_dir=json_dir))


if __name__ == '__main__':
    main()
