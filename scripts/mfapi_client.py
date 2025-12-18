"""Simple mfapi client with sync and async helpers.
"""
import asyncio
import logging
from typing import Dict, Any, List

import aiohttp
import async_timeout
import requests

logger = logging.getLogger('mfapi_client')
BASE_URL = 'https://api.mfapi.in'
API_TIMEOUT = 20

_session = requests.Session()
_session.headers.update({'User-Agent': 'mfapi-client/0.1'})


class MFAPIError(Exception):
    pass


def mf_get(path: str, params: Dict[str, Any] = None, timeout: int = API_TIMEOUT) -> Any:
    url = BASE_URL.rstrip('/') + path
    try:
        resp = _session.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.HTTPError as e:
        logger.error('HTTP error for %s: %s', url, e)
        raise MFAPIError(e)
    except requests.RequestException as e:
        logger.error('Request error for %s: %s', url, e)
        raise MFAPIError(e)


def list_schemes() -> List[Dict[str, Any]]:
    return mf_get('/mf')


def search_schemes(q: str) -> List[Dict[str, Any]]:
    return mf_get('/mf/search', params={'q': q})


def get_nav_history(scheme_code: int) -> Dict[str, Any]:
    return mf_get(f'/mf/{scheme_code}')


async def fetch_nav_async(session: aiohttp.ClientSession, scheme_code: int) -> Dict[str, Any]:
    url = f"{BASE_URL}/mf/{scheme_code}"
    try:
        async with async_timeout.timeout(API_TIMEOUT):
            async with session.get(url) as resp:
                resp.raise_for_status()
                return await resp.json()
    except Exception as e:
        logger.exception('Async fetch error %s: %s', url, e)
        return {'error': str(e), 'scheme_code': scheme_code}


async def batch_fetch_navs(codes: List[int], concurrency: int = 10) -> List[Dict[str, Any]]:
    semaphore = asyncio.Semaphore(concurrency)
    async with aiohttp.ClientSession(headers={'User-Agent': 'mfapi-async/0.1'}) as session:
        async def _safe_fetch(code):
            async with semaphore:
                return await fetch_nav_async(session, code)

        tasks = [_safe_fetch(c) for c in codes]
        return await asyncio.gather(*tasks)


def nav_json_to_df(nav_json: Dict[str, Any]):
    import pandas as pd
    data = nav_json.get('data', []) if isinstance(nav_json, dict) else []
    df = pd.DataFrame(data)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    if 'nav' in df.columns:
        df['nav'] = pd.to_numeric(df['nav'].str.replace(',', ''), errors='coerce')
    return df.sort_values('date').reset_index(drop=True)
