#!/usr/bin/env python3
import csv
import json
from pathlib import Path

SRC = Path(__file__).resolve().parents[0] / '..' / 'PS' / 'MF_India_AI.csv'
OUT = Path(__file__).resolve().parents[0] / '..' / 'PS' / 'MF_India_AI.json'

def parse_value(v):
    if v is None:
        return None
    v = v.strip()
    if v == '' or v == '-':
        return None
    # try int
    try:
        i = int(v)
        return i
    except Exception:
        pass
    # try float
    try:
        f = float(v)
        return f
    except Exception:
        pass
    return v

if __name__ == '__main__':
    src = SRC
    out = OUT
    rows = []
    with open(src, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            obj = {k: parse_value(v) for k, v in r.items()}
            rows.append(obj)

    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    print(f'Wrote {len(rows)} records to {out}')
