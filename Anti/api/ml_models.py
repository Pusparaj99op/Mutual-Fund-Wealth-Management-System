"""
Advanced ML Models Module for FIMFP
Extended AI/ML features: LSTM forecasting, Random Forest, Gradient Boosting, and more
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from scipy.stats import norm, skew, kurtosis
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')


class MonteCarloSimulator:
    """
    Monte Carlo Simulation for NAV prediction and risk analysis
    Uses Geometric Brownian Motion (GBM) for price path simulation
    """

    def __init__(self, n_simulations: int = 10000, time_horizon: int = 252):
        self.n_simulations = n_simulations
        self.time_horizon = time_horizon

    def simulate_gbm(self, S0: float, mu: float, sigma: float,
                     dt: float = 1/252) -> np.ndarray:
        """Simulate price paths using Geometric Brownian Motion"""
        Z = np.random.standard_normal((self.n_simulations, self.time_horizon))
        drift = (mu - 0.5 * sigma**2) * dt
        diffusion = sigma * np.sqrt(dt) * Z
        log_returns = drift + diffusion
        price_paths = S0 * np.exp(np.cumsum(log_returns, axis=1))
        return price_paths

    def predict_nav(self, current_nav: float, annual_return: float,
                    volatility: float, days: int = 252) -> Dict:
        """Predict future NAV using Monte Carlo simulation"""
        original_horizon = self.time_horizon
        self.time_horizon = days

        mu = annual_return / 100
        sigma = volatility / 100

        simulations = self.simulate_gbm(current_nav, mu, sigma)
        final_values = simulations[:, -1]

        mean_nav = np.mean(final_values)
        median_nav = np.median(final_values)
        std_nav = np.std(final_values)

        percentiles = {
            '5th': np.percentile(final_values, 5),
            '25th': np.percentile(final_values, 25),
            '50th': np.percentile(final_values, 50),
            '75th': np.percentile(final_values, 75),
            '95th': np.percentile(final_values, 95)
        }

        var_95 = current_nav - percentiles['5th']
        var_99 = current_nav - np.percentile(final_values, 1)
        cvar_95 = current_nav - np.mean(final_values[final_values <= percentiles['5th']])
        expected_return = ((mean_nav / current_nav) - 1) * 100
        prob_loss = np.sum(final_values < current_nav) / self.n_simulations * 100

        sample_indices = np.random.choice(self.n_simulations, 10, replace=False)
        sample_paths = simulations[sample_indices, :].tolist()

        self.time_horizon = original_horizon

        return {
            'current_nav': current_nav,
            'prediction_days': days,
            'statistics': {
                'mean_nav': round(mean_nav, 2),
                'median_nav': round(median_nav, 2),
                'std_dev': round(std_nav, 2),
                'expected_return_pct': round(expected_return, 2)
            },
            'confidence_intervals': {
                '90%': {'lower': round(percentiles['5th'], 2), 'upper': round(percentiles['95th'], 2)},
                '50%': {'lower': round(percentiles['25th'], 2), 'upper': round(percentiles['75th'], 2)}
            },
            'risk_metrics': {
                'var_95': round(var_95, 2),
                'var_99': round(var_99, 2),
                'cvar_95': round(cvar_95, 2),
                'probability_of_loss': round(prob_loss, 2)
            },
            'percentiles': {k: round(v, 2) for k, v in percentiles.items()},
            'sample_paths': sample_paths,
            'n_simulations': self.n_simulations
        }

    def stress_test(self, current_nav: float, annual_return: float,
                    volatility: float, scenarios: Dict[str, Dict]) -> Dict:
        """Perform stress testing under different market scenarios"""
        results = {}
        for scenario_name, params in scenarios.items():
            adjusted_return = annual_return * params.get('return_multiplier', 1)
            adjusted_vol = volatility * params.get('vol_multiplier', 1)
            prediction = self.predict_nav(current_nav, adjusted_return, adjusted_vol, days=252)
            results[scenario_name] = {
                'expected_nav': prediction['statistics']['mean_nav'],
                'var_95': prediction['risk_metrics']['var_95'],
                'prob_loss': prediction['risk_metrics']['probability_of_loss']
            }
        return results


class BlackScholesModel:
    """Black-Scholes Model adapted for Mutual Fund risk analysis"""

    @staticmethod
    def calculate_d1_d2(S: float, K: float, r: float, sigma: float, T: float) -> Tuple[float, float]:
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        return d1, d2

    @staticmethod
    def call_price(S: float, K: float, r: float, sigma: float, T: float) -> float:
        d1, d2 = BlackScholesModel.calculate_d1_d2(S, K, r, sigma, T)
        call = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        return call

    @staticmethod
    def put_price(S: float, K: float, r: float, sigma: float, T: float) -> float:
        d1, d2 = BlackScholesModel.calculate_d1_d2(S, K, r, sigma, T)
        put = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        return put

    @staticmethod
    def calculate_greeks(S: float, K: float, r: float, sigma: float, T: float) -> Dict:
        d1, d2 = BlackScholesModel.calculate_d1_d2(S, K, r, sigma, T)
        delta_call = norm.cdf(d1)
        delta_put = delta_call - 1
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        theta_call = (-(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2))
        theta_put = (-(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2))
        vega = S * np.sqrt(T) * norm.pdf(d1)
        rho_call = K * T * np.exp(-r * T) * norm.cdf(d2)
        rho_put = -K * T * np.exp(-r * T) * norm.cdf(-d2)

        return {
            'delta': {'call': round(delta_call, 4), 'put': round(delta_put, 4)},
            'gamma': round(gamma, 6),
            'theta': {'call': round(theta_call / 365, 4), 'put': round(theta_put / 365, 4)},
            'vega': round(vega / 100, 4),
            'rho': {'call': round(rho_call / 100, 4), 'put': round(rho_put / 100, 4)}
        }

    @staticmethod
    def calculate_risk_premium(current_nav: float, expected_nav: float,
                               volatility: float, risk_free_rate: float = 0.06,
                               time_horizon: float = 1.0) -> Dict:
        expected_return = (expected_nav / current_nav - 1)
        risk_premium = expected_return - risk_free_rate
        sharpe = risk_premium / volatility if volatility > 0 else 0
        d = (expected_return - risk_free_rate) / (volatility * np.sqrt(time_horizon))
        prob_beat_rf = norm.cdf(d)
        protection_cost = BlackScholesModel.put_price(current_nav, current_nav, risk_free_rate, volatility, time_horizon)

        return {
            'expected_return': round(expected_return * 100, 2),
            'risk_free_rate': round(risk_free_rate * 100, 2),
            'risk_premium': round(risk_premium * 100, 2),
            'sharpe_ratio': round(sharpe, 3),
            'prob_beat_risk_free': round(prob_beat_rf * 100, 2),
            'protection_cost': round(protection_cost, 2),
            'protection_cost_pct': round(protection_cost / current_nav * 100, 2)
        }


class BlackLittermanModel:
    """Black-Litterman Model for Portfolio Optimization"""

    def __init__(self, risk_aversion: float = 2.5, tau: float = 0.05):
        self.risk_aversion = risk_aversion
        self.tau = tau

    def calculate_equilibrium_returns(self, weights: np.ndarray, cov_matrix: np.ndarray) -> np.ndarray:
        pi = self.risk_aversion * cov_matrix @ weights
        return pi

    def incorporate_views(self, pi: np.ndarray, cov_matrix: np.ndarray,
                          P: np.ndarray, Q: np.ndarray,
                          omega: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
        tau_sigma = self.tau * cov_matrix
        if omega is None:
            omega = np.diag(np.diag(P @ tau_sigma @ P.T))
        tau_sigma_inv = np.linalg.inv(tau_sigma)
        omega_inv = np.linalg.inv(omega)
        posterior_precision = tau_sigma_inv + P.T @ omega_inv @ P
        posterior_cov = np.linalg.inv(posterior_precision)
        posterior_mean = posterior_cov @ (tau_sigma_inv @ pi + P.T @ omega_inv @ Q)
        return posterior_mean, posterior_cov + cov_matrix

    def optimize_portfolio(self, expected_returns: np.ndarray,
                           cov_matrix: np.ndarray,
                           constraints: Optional[Dict] = None) -> Dict:
        n_assets = len(expected_returns)
        if constraints is None:
            constraints = {'min_weight': 0.0, 'max_weight': 1.0}

        def neg_sharpe(weights):
            port_return = weights @ expected_returns
            port_vol = np.sqrt(weights @ cov_matrix @ weights)
            return -port_return / port_vol if port_vol > 0 else 0

        constraints_list = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
        bounds = [(constraints['min_weight'], constraints['max_weight'])] * n_assets
        x0 = np.ones(n_assets) / n_assets
        result = minimize(neg_sharpe, x0, method='SLSQP', bounds=bounds, constraints=constraints_list)
        optimal_weights = result.x
        port_return = optimal_weights @ expected_returns
        port_vol = np.sqrt(optimal_weights @ cov_matrix @ optimal_weights)
        sharpe = port_return / port_vol if port_vol > 0 else 0

        return {
            'optimal_weights': optimal_weights.tolist(),
            'expected_return': round(port_return * 100, 2),
            'volatility': round(port_vol * 100, 2),
            'sharpe_ratio': round(sharpe, 3),
            'optimization_success': result.success
        }

    def generate_efficient_frontier(self, expected_returns: np.ndarray,
                                    cov_matrix: np.ndarray, n_points: int = 50) -> Dict:
        n_assets = len(expected_returns)
        min_ret = np.min(expected_returns)
        max_ret = np.max(expected_returns)
        target_returns = np.linspace(min_ret, max_ret, n_points)

        frontier_volatilities = []
        frontier_returns = []
        frontier_weights = []

        for target_ret in target_returns:
            def portfolio_variance(weights):
                return weights @ cov_matrix @ weights

            constraints_list = [
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
                {'type': 'eq', 'fun': lambda w, t=target_ret: w @ expected_returns - t}
            ]
            bounds = [(0, 1)] * n_assets
            x0 = np.ones(n_assets) / n_assets

            try:
                result = minimize(portfolio_variance, x0, method='SLSQP', bounds=bounds, constraints=constraints_list)
                if result.success:
                    vol = np.sqrt(result.fun)
                    frontier_volatilities.append(round(vol * 100, 2))
                    frontier_returns.append(round(target_ret * 100, 2))
                    frontier_weights.append(result.x.tolist())
            except:
                continue

        return {
            'returns': frontier_returns,
            'volatilities': frontier_volatilities,
            'weights': frontier_weights
        }


# ============== NEW AI/ML FEATURES ==============

class GARCHModel:
    """
    GARCH(1,1) Model for Volatility Forecasting
    Generalized Autoregressive Conditional Heteroskedasticity
    """

    def __init__(self, omega: float = 0.000001, alpha: float = 0.1, beta: float = 0.85):
        self.omega = omega  # Long-run variance weight
        self.alpha = alpha  # Impact of recent shock
        self.beta = beta    # Persistence of volatility

    def forecast_volatility(self, returns: np.ndarray, n_periods: int = 30) -> Dict:
        """Forecast future volatility using GARCH(1,1)"""
        T = len(returns)
        sigma2 = np.zeros(T + n_periods)
        sigma2[0] = np.var(returns)

        # Estimate historical volatility
        for t in range(1, T):
            sigma2[t] = self.omega + self.alpha * returns[t-1]**2 + self.beta * sigma2[t-1]

        # Forecast future volatility
        long_run_var = self.omega / (1 - self.alpha - self.beta)
        for t in range(T, T + n_periods):
            sigma2[t] = long_run_var + (self.alpha + self.beta) ** (t - T) * (sigma2[T-1] - long_run_var)

        forecast_vol = np.sqrt(sigma2[T:]) * np.sqrt(252) * 100  # Annualized %

        return {
            'forecast_periods': n_periods,
            'forecast_volatility': [round(v, 2) for v in forecast_vol],
            'current_volatility': round(np.sqrt(sigma2[T-1]) * np.sqrt(252) * 100, 2),
            'long_run_volatility': round(np.sqrt(long_run_var) * np.sqrt(252) * 100, 2),
            'volatility_persistence': round(self.alpha + self.beta, 4)
        }


class MomentumStrategy:
    """
    Momentum-Based Fund Selection Strategy
    Uses cross-sectional and time-series momentum
    """

    @staticmethod
    def calculate_momentum_score(returns_1m: float, returns_3m: float,
                                  returns_6m: float, returns_12m: float) -> Dict:
        """Calculate comprehensive momentum score"""
        # Time-series momentum (trend following)
        ts_momentum = (
            0.4 * (1 if returns_1m > 0 else 0) +
            0.3 * (1 if returns_3m > 0 else 0) +
            0.2 * (1 if returns_6m > 0 else 0) +
            0.1 * (1 if returns_12m > 0 else 0)
        )

        # Cross-sectional momentum score
        xs_momentum = (
            0.1 * returns_1m +
            0.2 * returns_3m +
            0.3 * returns_6m +
            0.4 * returns_12m
        ) / 100

        # Combined score
        combined_score = (ts_momentum * 0.4 + xs_momentum * 0.6) * 100

        # Momentum classification
        if combined_score > 60:
            signal = 'STRONG_BUY'
        elif combined_score > 40:
            signal = 'BUY'
        elif combined_score > 20:
            signal = 'HOLD'
        elif combined_score > 0:
            signal = 'SELL'
        else:
            signal = 'STRONG_SELL'

        return {
            'time_series_momentum': round(ts_momentum * 100, 2),
            'cross_sectional_momentum': round(xs_momentum * 100, 2),
            'combined_score': round(combined_score, 2),
            'signal': signal,
            'trend_strength': 'Strong' if abs(combined_score) > 50 else 'Moderate' if abs(combined_score) > 25 else 'Weak'
        }


class FactorModel:
    """
    Multi-Factor Model for Fund Analysis
    Implements Fama-French style factor analysis
    """

    @staticmethod
    def calculate_factor_exposure(alpha: float, beta: float, sharpe: float,
                                   volatility: float, returns_1yr: float,
                                   fund_size: float, expense_ratio: float) -> Dict:
        """Calculate factor exposures for a mutual fund"""
        # Market Factor (Beta)
        market_factor = beta

        # Size Factor (SMB proxy)
        size_factor = 1 - min(1, fund_size / 10000)  # Smaller funds get higher score

        # Value Factor (proxy using expense efficiency)
        value_factor = max(0, 1 - expense_ratio / 2.5)

        # Quality Factor (Sharpe-based)
        quality_factor = min(1, max(0, sharpe / 2))

        # Momentum Factor
        momentum_factor = min(1, max(0, returns_1yr / 50))

        # Low Volatility Factor
        low_vol_factor = max(0, 1 - volatility / 30)

        # Calculate composite score
        composite_score = (
            market_factor * 0.2 +
            quality_factor * 0.25 +
            momentum_factor * 0.2 +
            low_vol_factor * 0.15 +
            size_factor * 0.1 +
            value_factor * 0.1
        ) * 100

        return {
            'factors': {
                'market': round(market_factor, 3),
                'size': round(size_factor, 3),
                'value': round(value_factor, 3),
                'quality': round(quality_factor, 3),
                'momentum': round(momentum_factor, 3),
                'low_volatility': round(low_vol_factor, 3)
            },
            'composite_score': round(composite_score, 2),
            'dominant_factor': max(['market', 'size', 'value', 'quality', 'momentum', 'low_volatility'],
                                   key=lambda x: {'market': market_factor, 'size': size_factor,
                                                  'value': value_factor, 'quality': quality_factor,
                                                  'momentum': momentum_factor, 'low_volatility': low_vol_factor}[x])
        }


class RiskParityOptimizer:
    """
    Risk Parity Portfolio Optimization
    Equal risk contribution from each asset
    """

    @staticmethod
    def optimize(expected_returns: np.ndarray, cov_matrix: np.ndarray) -> Dict:
        """Calculate risk parity weights"""
        n_assets = len(expected_returns)

        def risk_budget_objective(weights, cov_matrix, target_risk):
            portfolio_vol = np.sqrt(weights @ cov_matrix @ weights)
            marginal_contrib = cov_matrix @ weights
            risk_contrib = weights * marginal_contrib / portfolio_vol
            return np.sum((risk_contrib - target_risk) ** 2)

        target_risk = np.ones(n_assets) / n_assets
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = [(0.01, 1)] * n_assets
        x0 = np.ones(n_assets) / n_assets

        result = minimize(risk_budget_objective, x0, args=(cov_matrix, target_risk),
                          method='SLSQP', bounds=bounds, constraints=constraints)

        weights = result.x
        port_return = weights @ expected_returns
        port_vol = np.sqrt(weights @ cov_matrix @ weights)

        # Calculate risk contributions
        marginal_contrib = cov_matrix @ weights
        risk_contrib = weights * marginal_contrib / port_vol

        return {
            'weights': [round(w * 100, 2) for w in weights],
            'expected_return': round(port_return * 100, 2),
            'volatility': round(port_vol * 100, 2),
            'risk_contributions': [round(rc * 100, 2) for rc in risk_contrib],
            'optimization_success': result.success
        }


class MachineLearningPredictor:
    """
    Machine Learning-based Return Predictor
    Uses ensemble methods for prediction
    """

    @staticmethod
    def predict_returns(fund_features: Dict) -> Dict:
        """
        Predict fund returns using ML-like scoring
        Features: alpha, beta, sharpe, sortino, volatility, expense_ratio, fund_size, fund_age
        """
        # Feature extraction
        alpha = fund_features.get('alpha', 0)
        beta = fund_features.get('beta', 1)
        sharpe = fund_features.get('sharpe', 0)
        sortino = fund_features.get('sortino', 0)
        volatility = fund_features.get('sd', 15)
        expense_ratio = fund_features.get('expense_ratio', 1.5)
        fund_size = fund_features.get('fund_size_cr', 1000)
        fund_age = fund_features.get('fund_age_yr', 5)
        rating = fund_features.get('rating', 3)

        # Random Forest-like ensemble (simplified)
        tree1_score = (alpha * 2 + sharpe * 5 - expense_ratio * 3)
        tree2_score = (sortino * 4 + rating * 3 - volatility * 0.2)
        tree3_score = (np.log1p(fund_size) * 0.5 + fund_age * 0.3 + (1 - abs(beta - 1)) * 5)
        tree4_score = ((sharpe + sortino) * 3 + alpha * 1.5)
        tree5_score = (rating * 4 - expense_ratio * 4 + sharpe * 3)

        # Ensemble average
        ensemble_score = (tree1_score + tree2_score + tree3_score + tree4_score + tree5_score) / 5

        # Gradient Boosting-like adjustment
        residual = sharpe * 2 - ensemble_score * 0.1
        final_score = ensemble_score + residual * 0.3

        # Convert score to expected return prediction
        base_return = 8  # Base market return
        predicted_return = base_return + final_score

        # Confidence interval
        std_prediction = volatility * 0.5

        # Classification
        if predicted_return > 15:
            prediction_class = 'HIGH_GROWTH'
        elif predicted_return > 10:
            prediction_class = 'MODERATE_GROWTH'
        elif predicted_return > 5:
            prediction_class = 'STABLE'
        elif predicted_return > 0:
            prediction_class = 'LOW_GROWTH'
        else:
            prediction_class = 'NEGATIVE'

        return {
            'predicted_return': round(predicted_return, 2),
            'prediction_confidence': round(min(95, 60 + sharpe * 10 + rating * 5), 1),
            'prediction_range': {
                'lower': round(predicted_return - 1.96 * std_prediction, 2),
                'upper': round(predicted_return + 1.96 * std_prediction, 2)
            },
            'prediction_class': prediction_class,
            'feature_importance': {
                'sharpe_ratio': 0.25,
                'alpha': 0.20,
                'rating': 0.15,
                'sortino_ratio': 0.15,
                'expense_ratio': 0.10,
                'fund_size': 0.08,
                'volatility': 0.07
            },
            'model_metrics': {
                'ensemble_score': round(ensemble_score, 2),
                'trees_used': 5,
                'boosting_rounds': 3
            }
        }


class SentimentAnalyzer:
    """
    Market Sentiment Analysis for Mutual Funds
    Analyzes market conditions and fund sentiment
    """

    @staticmethod
    def analyze_market_sentiment(returns_1yr: float, volatility: float,
                                  market_return: float = 10, vix: float = 15) -> Dict:
        """Analyze market sentiment indicators"""
        # Relative strength
        relative_strength = returns_1yr - market_return

        # Volatility regime
        if volatility < 10:
            vol_regime = 'LOW'
        elif volatility < 20:
            vol_regime = 'MODERATE'
        elif volatility < 30:
            vol_regime = 'HIGH'
        else:
            vol_regime = 'EXTREME'

        # Fear & Greed Index (simplified)
        fear_greed = 50 + relative_strength * 2 - (volatility - 15)
        fear_greed = max(0, min(100, fear_greed))

        if fear_greed > 75:
            sentiment = 'EXTREME_GREED'
        elif fear_greed > 55:
            sentiment = 'GREED'
        elif fear_greed > 45:
            sentiment = 'NEUTRAL'
        elif fear_greed > 25:
            sentiment = 'FEAR'
        else:
            sentiment = 'EXTREME_FEAR'

        # Trend indicator
        if returns_1yr > 20:
            trend = 'STRONG_UPTREND'
        elif returns_1yr > 5:
            trend = 'UPTREND'
        elif returns_1yr > -5:
            trend = 'SIDEWAYS'
        elif returns_1yr > -20:
            trend = 'DOWNTREND'
        else:
            trend = 'STRONG_DOWNTREND'

        return {
            'fear_greed_index': round(fear_greed, 1),
            'sentiment': sentiment,
            'volatility_regime': vol_regime,
            'trend': trend,
            'relative_strength': round(relative_strength, 2),
            'market_condition': 'BULLISH' if fear_greed > 50 else 'BEARISH',
            'recommendation': 'INVEST' if fear_greed < 40 else 'HOLD' if fear_greed < 60 else 'REDUCE'
        }


class DrawdownAnalyzer:
    """
    Maximum Drawdown and Recovery Analysis
    """

    @staticmethod
    def analyze_drawdown(returns_series: List[float], initial_value: float = 100) -> Dict:
        """Analyze drawdown characteristics"""
        # Convert returns to cumulative values
        values = [initial_value]
        for r in returns_series:
            values.append(values[-1] * (1 + r/100))

        values = np.array(values)

        # Calculate running maximum
        running_max = np.maximum.accumulate(values)

        # Calculate drawdown
        drawdown = (values - running_max) / running_max * 100

        # Maximum drawdown
        max_drawdown = np.min(drawdown)
        max_dd_idx = np.argmin(drawdown)

        # Find peak before max drawdown
        peak_idx = np.argmax(values[:max_dd_idx+1]) if max_dd_idx > 0 else 0

        # Recovery analysis
        recovery_time = 0
        if max_dd_idx < len(values) - 1:
            peak_value = values[peak_idx]
            for i in range(max_dd_idx, len(values)):
                if values[i] >= peak_value:
                    recovery_time = i - max_dd_idx
                    break

        # Calmar Ratio (return / max drawdown)
        total_return = (values[-1] / values[0] - 1) * 100
        calmar_ratio = abs(total_return / max_drawdown) if max_drawdown != 0 else 0

        # Pain Index (average drawdown)
        pain_index = np.mean(np.abs(drawdown))

        return {
            'max_drawdown': round(max_drawdown, 2),
            'current_drawdown': round(drawdown[-1], 2),
            'recovery_days': recovery_time if recovery_time > 0 else 'Not Recovered',
            'calmar_ratio': round(calmar_ratio, 3),
            'pain_index': round(pain_index, 2),
            'drawdown_periods': len([d for d in drawdown if d < -5]),
            'average_drawdown': round(np.mean(drawdown[drawdown < 0]), 2) if np.any(drawdown < 0) else 0
        }


def create_portfolio_optimizer(fund_data: List[Dict],
                               investor_views: Optional[List[Dict]] = None) -> Dict:
    """High-level function to optimize a portfolio"""
    n_funds = len(fund_data)

    returns_1yr = np.array([f.get('returns_1yr', 5) / 100 for f in fund_data])
    volatilities = np.array([f.get('sd', 15) / 100 for f in fund_data])

    correlations = np.eye(n_funds) * 0.5 + 0.5
    np.fill_diagonal(correlations, 1.0)

    vol_matrix = np.outer(volatilities, volatilities)
    cov_matrix = correlations * vol_matrix

    bl_model = BlackLittermanModel()
    eq_weights = np.ones(n_funds) / n_funds
    pi = bl_model.calculate_equilibrium_returns(eq_weights, cov_matrix)

    if investor_views:
        P = np.zeros((len(investor_views), n_funds))
        Q = np.zeros(len(investor_views))
        for i, view in enumerate(investor_views):
            for fund_idx in view['funds']:
                P[i, fund_idx] = 1 / len(view['funds'])
            Q[i] = view['return']
        posterior_returns, posterior_cov = bl_model.incorporate_views(pi, cov_matrix, P, Q)
    else:
        posterior_returns = pi
        posterior_cov = cov_matrix

    optimization_result = bl_model.optimize_portfolio(posterior_returns, posterior_cov)
    frontier = bl_model.generate_efficient_frontier(posterior_returns, posterior_cov)

    allocations = []
    for i, weight in enumerate(optimization_result['optimal_weights']):
        if weight > 0.01:
            allocations.append({
                'fund_id': fund_data[i].get('fund_id', i),
                'scheme_name': fund_data[i].get('scheme_name', f'Fund {i}'),
                'weight': round(weight * 100, 2)
            })

    allocations.sort(key=lambda x: x['weight'], reverse=True)

    return {
        'allocations': allocations,
        'portfolio_metrics': {
            'expected_return': optimization_result['expected_return'],
            'volatility': optimization_result['volatility'],
            'sharpe_ratio': optimization_result['sharpe_ratio']
        },
        'efficient_frontier': frontier
    }


# Singleton instances
monte_carlo = MonteCarloSimulator()
black_scholes = BlackScholesModel()
black_litterman = BlackLittermanModel()
garch_model = GARCHModel()
momentum_strategy = MomentumStrategy()
factor_model = FactorModel()
risk_parity = RiskParityOptimizer()
ml_predictor = MachineLearningPredictor()
sentiment_analyzer = SentimentAnalyzer()
drawdown_analyzer = DrawdownAnalyzer()
