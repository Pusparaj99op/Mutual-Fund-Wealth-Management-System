import pytest
from fastapi.testclient import TestClient
from raptor.src.api import app

client = TestClient(app)


def test_predict_with_samples():
    # pick an existing scheme
    from raptor.src import data_loader, preprocessing
    preprocessing.generate_all_features(limit=3)
    schemes = data_loader.list_available_schemes()
    assert schemes
    r = client.post('/predict', json={'scheme_code': schemes[0], 'horizon':7, 'n_sim':200, 'include_samples': True, 'samples_to_return': 10})
    assert r.status_code == 200
    j = r.json()
    assert 'samples' in j
    assert isinstance(j['samples'], list)
    assert len(j['samples']) <= 10
