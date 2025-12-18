import pytest
import numpy as np
import pandas as pd
from raptor.src import deep_models


def test_sequence_creation_and_dummy():
    # create a small synthetic series
    s = np.arange(50).astype(float)
    X, y = deep_models.create_sequences(pd.Series(s), window=10, horizon=1)
    assert X.shape[0] == 50 - 10 - 1 + 1
    assert X.shape[1] == 10
    assert X.shape[2] == 1


def test_train_lstm_smoke():
    pytest.importorskip('tensorflow')
    s = np.sin(np.linspace(0, 6.28, 200))
    X, y = deep_models.create_sequences(pd.Series(s), window=20, horizon=1)
    model = deep_models.build_and_train_lstm(X, y, epochs=2, batch_size=16, verbose=0)
    pred = deep_models.predict_sequence(model, X[-1])
    assert pred.shape[0] == 1
