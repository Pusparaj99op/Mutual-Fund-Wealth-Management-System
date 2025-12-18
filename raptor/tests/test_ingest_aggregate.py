import os
from raptor.src import ingest_aggregate, preprocessing


def test_build_aggregated_limit():
    # ensure at least some feature files exist; if not, generate a small subset
    features_dir = preprocessing.FEATURES_DIR
    files = list(features_dir.glob('features_*.parquet'))
    if not files:
        # generate features for a few raw files
        preprocessing.generate_all_features(limit=5)
    agg = ingest_aggregate.build_aggregated_dataset(min_observations=10, limit=5)
    assert 'scheme_code' in agg.columns
    assert len(agg) > 0
    # check that file exists on disk
    assert (preprocessing.ROOT / 'data' / 'processed' / 'aggregated_features.parquet').exists()
