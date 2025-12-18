import pytest
from fastapi.testclient import TestClient
from raptor.src.api import app

client = TestClient(app)


def test_backtest_endpoint():
    # This test may be data-dependent; skip if not enough data
    from raptor.src import preprocessing, ingest_aggregate
    preprocessing.generate_all_features(limit=6)
    ingest_aggregate.build_aggregated_dataset(min_observations=10, limit=6)
    r = client.post('/backtest', json={'lookback_days':120, 'rebalance_freq_days':30, 'top_k':3})
    assert r.status_code == 200
    j = r.json()
    assert 'metrics' in j and 'series' in j
    assert isinstance(j['series'], list)
