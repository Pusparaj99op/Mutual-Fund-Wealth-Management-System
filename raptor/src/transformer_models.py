"""Transformer-based time-series forecasting (prototype).

This module implements a simple Transformer encoder-based model for sequence forecasting.
All heavy dependencies (PyTorch) are imported lazily; functions raise ImportError when PyTorch is not installed.
"""
from typing import Tuple
import numpy as np
import logging

logger = logging.getLogger('raptor.transformer')


def _ensure_torch():
    try:
        import torch
        import torch.nn as nn
        return torch, nn
    except Exception as e:
        raise ImportError('PyTorch is required for transformer_models but is not installed') from e


class TimeSeriesTransformer:
    """Wrapper class for a Transformer-based predictor.

    Usage (prototype):
      model = TimeSeriesTransformer(input_size=1, d_model=64, nhead=4, num_layers=2, dim_feedforward=128, horizon=1)
      model.train(X_train, y_train, epochs=10)
      preds = model.predict(X_val)
    """

    def __init__(self, input_size=1, d_model=64, nhead=4, num_layers=2, dim_feedforward=128, horizon=1, device=None):
        torch, nn = _ensure_torch()
        self.torch = torch
        # Default to CPU to avoid triggering CUDA initialization during import/tests.
        # Consumers can still pass an explicit `device` (e.g., torch.device('cuda')) to use GPU.
        self.device = device or torch.device('cpu')
        self.input_size = input_size
        self.horizon = horizon
        # simple linear input projection
        class _Model(nn.Module):
            def __init__(self, input_size, d_model, nhead, num_layers, dim_feedforward, horizon):
                super().__init__()
                self.input_proj = nn.Linear(input_size, d_model)
                encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead, dim_feedforward=dim_feedforward)
                self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
                self.head = nn.Linear(d_model, horizon)

            def forward(self, x):
                # x: (B, L, C)
                x = self.input_proj(x)  # (B, L, d)
                # Transformer expects (L, B, d)
                x = x.permute(1, 0, 2)
                x = self.encoder(x)  # (L, B, d)
                x = x.mean(dim=0)  # aggregate over sequence -> (B, d)
                out = self.head(x)  # (B, horizon)
                return out

        self.model = _Model(input_size, d_model, nhead, num_layers, dim_feedforward, horizon).to(self.device)

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 10, batch_size: int = 64, lr: float = 1e-3, verbose: bool = True):
        torch = self.torch
        # X: (N, L, C), y: (N, H)
        dataset = torch.utils.data.TensorDataset(torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32))
        loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
        opt = torch.optim.Adam(self.model.parameters(), lr=lr)
        loss_fn = torch.nn.MSELoss()
        self.model.train()
        for ep in range(epochs):
            total = 0.0
            cnt = 0
            for xb, yb in loader:
                xb = xb.to(self.device)
                yb = yb.to(self.device)
                opt.zero_grad()
                out = self.model(xb)
                loss = loss_fn(out, yb)
                loss.backward()
                opt.step()
                total += float(loss.item())
                cnt += 1
            if verbose:
                logger.info(f'Epoch {ep+1}/{epochs} - loss={total/cnt:.6f}')

    def predict(self, X: np.ndarray) -> np.ndarray:
        torch = self.torch
        self.model.eval()
        with torch.no_grad():
            xb = torch.tensor(X, dtype=torch.float32).to(self.device)
            out = self.model(xb)
            return out.cpu().numpy()

    def save(self, path: str):
        torch = self.torch
        torch.save(self.model.state_dict(), path)

    def load(self, path: str):
        torch = self.torch
        self.model.load_state_dict(torch.load(path))


def create_sequences(series: np.ndarray, window: int = 30, horizon: int = 1) -> Tuple[np.ndarray, np.ndarray]:
    """Small wrapper to create sequences for Transformer (same as deep_models.create_sequences)."""
    arr = np.asarray(series)
    X = []
    y = []
    for i in range(len(arr) - window - horizon + 1):
        X.append(arr[i:i+window])
        y.append(arr[i+window:i+window+horizon])
    X = np.array(X)
    y = np.array(y)
    X = X.reshape((X.shape[0], X.shape[1], 1))
    return X, y
