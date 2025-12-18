import pytest
from fastapi.testclient import TestClient
from raptor.src.api import app

client = TestClient(app)


def test_train_and_predict_endpoints():
    # Skip test if sklearn not available
    pytest.importorskip('sklearn')
    # Trigger training (small)
    r = client.post('/train_pooled', json={'horizon':7, 'n_estimators':10, 'sample_limit':10})
    assert r.status_code == 200
    j = r.json()
    assert 'mae' in j and 'rmse' in j
    # Now predict for a scheme from generated features
    # Ensure features exist for a small sample
    from raptor.src import preprocessing
    preprocessing.generate_all_features(limit=6)
    # use one of the files created
    schemes = [p.stem.split('_')[-1] for p in (preprocessing.FEATURES_DIR).glob('features_*.parquet')][:1]
    assert schemes
    r2 = client.post('/predict_model', json={'scheme_code': schemes[0], 'horizon':7})
    assert r2.status_code == 200
    j2 = r2.json()
    assert 'pred_target_ret' in j2
