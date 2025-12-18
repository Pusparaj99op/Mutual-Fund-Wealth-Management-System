from raptor.src import train_baselines, backtest, preprocessing


def test_train_pooled_and_backtest_small():
    # ensure features exist for a handful of schemes
    preprocessing.generate_all_features(limit=6)
    # Build aggregated dataset
    from raptor.src import ingest_aggregate
    ingest_aggregate.build_aggregated_dataset(min_observations=10, limit=6)
    # Train pooled model (small) — skip if sklearn not installed in environment
    import pytest
    pytest.importorskip('sklearn')
    res = train_baselines.train_pooled_rf(horizon=7, n_estimators=10, sample_limit=10)
    assert 'mae' in res and 'rmse' in res
    # Run a small backtest with small lookback (reduce to small for test)
    out = backtest.backtest_black_litterman(lookback_days=120, rebalance_freq_days=30, top_k=3)
    assert 'metrics' in out and 'portfolio_nav' in out
    assert out['metrics']['annualized_return'] is not None
