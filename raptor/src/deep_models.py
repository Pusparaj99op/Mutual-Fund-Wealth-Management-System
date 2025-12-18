"""Deep learning helpers for time-series forecasting using LSTM (prototype).

Functions are written to import TensorFlow lazily so environments without TF won't fail on import.
"""
from typing import Tuple
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger('raptor.deep')


def create_sequences(series: pd.Series, window: int = 30, horizon: int = 1) -> Tuple[np.ndarray, np.ndarray]:
    """Turn a 1-D series into supervised samples for sequence models.

    Returns X (n_samples, window, 1) and y (n_samples, horizon)
    """
    arr = series.values
    X = []
    y = []
    for i in range(len(arr) - window - horizon + 1):
        X.append(arr[i:i+window])
        y.append(arr[i+window:i+window+horizon])
    X = np.array(X)
    y = np.array(y)
    # reshape X for LSTM
    X = X.reshape((X.shape[0], X.shape[1], 1))
    return X, y


def build_and_train_lstm(X: np.ndarray, y: np.ndarray, epochs: int = 10, batch_size: int = 32, verbose: int = 1):
    """Build a simple LSTM model using tensorflow.keras and train it. Returns the fitted model.

    This function will raise ImportError if tensorflow is not installed.
    """
    tf = __import__('tensorflow')
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense
    from tensorflow.keras.callbacks import EarlyStopping

    model = Sequential([LSTM(32, input_shape=(X.shape[1], X.shape[2])), Dense(y.shape[1])])
    model.compile(optimizer='adam', loss='mse')
    es = EarlyStopping(patience=3, restore_best_weights=True)
    model.fit(X, y, epochs=epochs, batch_size=batch_size, callbacks=[es], verbose=verbose)
    return model


def predict_sequence(model, recent_window: np.ndarray) -> np.ndarray:
    """Predict horizon given a trained model and a recent window (shape (window, 1))."""
    arr = recent_window.reshape((1, recent_window.shape[0], recent_window.shape[1]))
    pred = model.predict(arr)
    return pred.flatten()
