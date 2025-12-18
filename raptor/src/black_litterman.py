"""Simple Black-Litterman posterior return and weight calculator.

This is a simplified implementation intended for prototype/demo use only.
"""
import numpy as np
from numpy.linalg import inv


def black_litterman_expected_returns(tau, pi, P, Q, cov):
    """Compute posterior expected returns using Black-Litterman formula.

    tau: scalar
    pi: prior equilibrium returns (n,)
    P: views matrix (k, n)
    Q: view returns (k,)
    cov: covariance matrix (n, n)
    Returns: posterior expected returns (n,)
    """
    # Following the standard formula: mu = inv(inv(tau*cov) + P.T * inv(P*(tau*cov)*P.T) * P) * (inv(tau*cov)*pi + P.T * inv(P*(tau*cov)*P.T) * Q)
    tau_cov = tau * cov
    inv_tau_cov = inv(tau_cov)
    middle = P.dot(tau_cov).dot(P.T)
    inv_middle = inv(middle)
    A = inv(inv_tau_cov + P.T.dot(inv_middle).dot(P))
    b = inv_tau_cov.dot(pi) + P.T.dot(inv_middle).dot(Q)
    mu = A.dot(b)
    return mu


def markowitz_weights(expected_returns, cov, risk_aversion=1.0):
    """Compute mean-variance optimal weights (no constraints) w = inv(risk_aversion*cov) * expected_returns"""
    w = inv(risk_aversion * cov).dot(expected_returns)
    # normalize to sum to 1 if possible
    if np.isfinite(w).all() and np.abs(w.sum())>1e-8:
        w = w / w.sum()
    return w
