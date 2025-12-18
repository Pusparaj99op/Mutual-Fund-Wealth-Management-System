import os
import pytest
import numpy as np

# Prevent tests from triggering CUDA initialization in environments without GPUs
# by ensuring CUDA_VISIBLE_DEVICES is empty before importing torch.
os.environ.setdefault('CUDA_VISIBLE_DEVICES', '')

from raptor.src import transformer_models


def test_transformer_create_sequences():
    s = np.arange(60).astype(float)
    X, y = transformer_models.create_sequences(s, window=10, horizon=1)
    assert X.shape[0] == 60 - 10 - 1 + 1
    assert X.shape[1] == 10


def test_transformer_train_smoke():
    # Import torch while suppressing noisy stderr output from CUDA/device checks
    import io
    import contextlib

    with contextlib.redirect_stderr(io.StringIO()):
        torch = pytest.importorskip('torch')

    s = np.sin(np.linspace(0, 6.28, 200))
    X, y = transformer_models.create_sequences(s, window=20, horizon=1)
    model = transformer_models.TimeSeriesTransformer(input_size=1, d_model=16, nhead=2, num_layers=1, dim_feedforward=32, horizon=1)

    # Also suppress noisy PyTorch runtime warnings emitted during training
    with contextlib.redirect_stderr(io.StringIO()):
        model.fit(X, y, epochs=1, batch_size=16, lr=1e-3, verbose=False)

    preds = model.predict(X[:10])
    assert preds.shape == (10, 1)
