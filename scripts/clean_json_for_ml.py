#!/usr/bin/env python3
"""Clean PS/MF_India_AI cleaned.json for ML:
- normalize keys to snake_case
- trim strings
- deduplicate by scheme_name (keep row with fewest nulls, then larger fund_size_cr)
- median-impute numeric columns
- fill categorical missing with 'Unknown'
- replace rating==0 with median rating (treated as missing)
- add log_fund_size feature
- write CSV and JSON cleaned outputs and a small report
"""

import json
import math
import csv
from pathlib import Path
from collections import defaultdict

SRC = Path(__file__).resolve().parents[0] / '..' / 'PS' / 'MF_India_AI cleaned.json'
OUT_JSON = Path(__file__).resolve().parents[0] / '..' / 'PS' / 'MF_India_AI_for_ml.json'
OUT_CSV = Path(__file__).resolve().parents[0] / '..' / 'PS' / 'MF_India_AI_for_ml.csv'
REPORT = Path(__file__).resolve().parents[0] / '..' / 'PS' / 'clean_report.txt'

numeric_cols = ['min_sip','min_lumpsum','expense_ratio','fund_size_cr','fund_age_yr','rating',
                'returns_1yr','returns_3yr','returns_5yr','risk_level','sd','sharpe','sortino','alpha','beta']
cat_cols = ['scheme_name','amc_name','sub_category','category','fund_manager']

def normalize_record(r):
    out = {}
    for k,v in r.items():
        nk = k.strip().lower().replace(' ','_')
        if isinstance(v,str):
            vv = v.strip()
        else:
            vv = v
        out[nk]=vv
    return out


def count_missing(r):
    return sum(1 for v in r.values() if v is None)


def median(vals):
    vals = sorted(vals)
    n = len(vals)
    if n==0:
        return None
    mid = n//2
    if n%2==1:
        return vals[mid]
    return (vals[mid-1]+vals[mid])/2


if __name__=='__main__':
    data = json.load(open(SRC, encoding='utf-8'))
    # normalize keys and trim
    data = [normalize_record(r) for r in data]

    # deduplicate by scheme_name
    groups = defaultdict(list)
    for r in data:
        groups[r['scheme_name']].append(r)

    deduped = []
    for name, rows in groups.items():
        if len(rows)==1:
            deduped.append(rows[0])
            continue
        # choose row with fewest missing; tie-breaker: larger fund_size_cr
        rows_sorted = sorted(rows, key=lambda x:(count_missing(x), -(x.get('fund_size_cr') or 0)))
        deduped.append(rows_sorted[0])

    # collect medians for numeric columns; treat rating==0 as missing
    col_vals = defaultdict(list)
    for r in deduped:
        for c in numeric_cols:
            v = r.get(c)
            if v is None:
                continue
            if c=='rating' and (isinstance(v,(int,float)) and v==0):
                continue
            try:
                col_vals[c].append(float(v))
            except Exception:
                pass

    med = {c: (median(col_vals[c]) if col_vals[c] else None) for c in numeric_cols}

    # impute numerics with median
    for r in deduped:
        for c in numeric_cols:
            v = r.get(c)
            if c=='rating' and (isinstance(v,(int,float)) and v==0):
                v = None
            if v is None:
                if med[c] is not None:
                    if c in ['fund_age_yr','rating','risk_level','min_sip','min_lumpsum']:
                        # keep as integer
                        r[c] = int(round(med[c]))
                    else:
                        r[c] = float(med[c])
                else:
                    r[c] = None

    # fill categorical missing
    for r in deduped:
        for c in cat_cols:
            v = r.get(c)
            if v is None or (isinstance(v,str) and v.strip()==''):
                r[c] = 'Unknown'
            else:
                # normalize whitespace and title-case for categories
                if c in ['amc_name','category','sub_category','fund_manager'] and isinstance(r[c],str):
                    r[c] = ' '.join(r[c].split())

    # add derived feature
    for r in deduped:
        fs = r.get('fund_size_cr')
        try:
            r['log_fund_size'] = math.log1p(float(fs)) if fs is not None else None
        except Exception:
            r['log_fund_size'] = None

    # write outputs
    with open(OUT_JSON,'w',encoding='utf-8') as f:
        json.dump(deduped,f,indent=2,ensure_ascii=False)

    keys = sorted(set().union(*[set(r.keys()) for r in deduped]))
    with open(OUT_CSV,'w',encoding='utf-8',newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in deduped:
            writer.writerow(r)

    # write report
    with open(REPORT,'w',encoding='utf-8') as f:
        f.write(f'Records input: {len(data)}\n')
        f.write(f'Records after dedup: {len(deduped)}\n')
        f.write('Medians used for imputation:\n')
        for c in numeric_cols:
            f.write(f' - {c}: {med[c]}\n')

    print('Cleaning done.')
    print(f'Wrote {len(deduped)} records to {OUT_JSON} and {OUT_CSV}.')
    print('Report:', REPORT)
