from raptor.src import ingest_aggregate, recommender, preprocessing


def test_recommend_basic():
    # Ensure features exist for a few schemes
    preprocessing.generate_all_features(limit=6)
    agg = ingest_aggregate.build_aggregated_dataset(min_observations=10, limit=6)
    out = recommender.recommend_black_litterman(amount=1000, top_k=3, min_obs=10)
    assert 'allocations' in out
    assert isinstance(out['allocations'], list)
    # allocations should not exceed 3
    assert len(out['allocations']) <= 3
    # each allocation has scheme_code and allocated_amount
    for a in out['allocations']:
        assert 'scheme_code' in a and 'allocated_amount' in a
