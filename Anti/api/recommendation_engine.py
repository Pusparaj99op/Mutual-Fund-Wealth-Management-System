"""
Recommendation Engine for FIMFP
AI-powered fund recommendations based on user risk profile and preferences
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from data_processor import MutualFundDataProcessor, get_processor
from ml_models import monte_carlo, black_scholes, create_portfolio_optimizer


class RiskProfiler:
    """
    Determines investor risk profile based on questionnaire responses
    """

    RISK_PROFILES = {
        1: {'name': 'Conservative', 'equity_range': (0, 30), 'volatility_tolerance': 10},
        2: {'name': 'Moderately Conservative', 'equity_range': (20, 50), 'volatility_tolerance': 15},
        3: {'name': 'Moderate', 'equity_range': (40, 60), 'volatility_tolerance': 20},
        4: {'name': 'Moderately Aggressive', 'equity_range': (50, 80), 'volatility_tolerance': 25},
        5: {'name': 'Aggressive', 'equity_range': (70, 100), 'volatility_tolerance': 30}
    }

    @staticmethod
    def calculate_risk_score(age: int, income: float, investment_horizon: int,
                             loss_tolerance: int, investment_experience: int) -> Dict:
        """
        Calculate risk score based on investor profile

        Args:
            age: Investor age
            income: Annual income in lakhs
            investment_horizon: Investment horizon in years
            loss_tolerance: 1-5 scale (how much loss can tolerate)
            investment_experience: 1-5 scale (experience level)

        Returns:
            Risk profile with recommended allocation
        """
        # Age factor (younger = higher risk)
        age_score = max(1, min(5, (60 - age) // 8 + 1))

        # Income factor (higher income = more risk capacity)
        income_score = min(5, int(income // 5) + 1)

        # Horizon factor (longer = higher risk)
        horizon_score = min(5, investment_horizon // 3 + 1)

        # Weighted average
        risk_score = (
            age_score * 0.2 +
            income_score * 0.15 +
            horizon_score * 0.25 +
            loss_tolerance * 0.25 +
            investment_experience * 0.15
        )

        risk_level = max(1, min(5, round(risk_score)))
        profile = RiskProfiler.RISK_PROFILES[risk_level]

        return {
            'risk_level': risk_level,
            'risk_profile': profile['name'],
            'recommended_equity_allocation': profile['equity_range'],
            'volatility_tolerance': profile['volatility_tolerance'],
            'scores': {
                'age_score': age_score,
                'income_score': income_score,
                'horizon_score': horizon_score,
                'loss_tolerance': loss_tolerance,
                'experience_score': investment_experience
            }
        }


class FundRecommendationEngine:
    """
    AI-powered recommendation engine for mutual funds
    """

    def __init__(self):
        self.data_processor = get_processor()
        self.risk_profiler = RiskProfiler()

    def get_recommendations(self, risk_profile: Dict = None,
                            investment_amount: float = 100000,
                            investment_horizon: int = 5,
                            categories: List[str] = None,
                            exclude_funds: List[int] = None,
                            top_n: int = 10) -> Dict:
        """
        Generate fund recommendations based on user profile

        Args:
            risk_profile: Risk profile from RiskProfiler
            investment_amount: Amount to invest in INR
            investment_horizon: Investment horizon in years
            categories: Preferred fund categories
            exclude_funds: Fund IDs to exclude
            top_n: Number of recommendations to return
        """
        # Load fund data
        funds, _ = self.data_processor.get_all_funds(limit=1000)

        if not funds:
            return {'error': 'No fund data available'}

        # Default risk profile (moderate)
        if risk_profile is None:
            risk_profile = {
                'risk_level': 3,
                'risk_profile': 'Moderate',
                'volatility_tolerance': 20
            }

        # Filter by categories if specified
        if categories:
            funds = [f for f in funds if f.get('category', '').lower() in
                     [c.lower() for c in categories]]

        # Exclude specific funds
        if exclude_funds:
            funds = [f for f in funds if f.get('fund_id') not in exclude_funds]

        # Score each fund
        scored_funds = []
        risk_level = risk_profile.get('risk_level', 3)
        vol_tolerance = risk_profile.get('volatility_tolerance', 20)

        for fund in funds:
            score = self._calculate_fund_score(fund, risk_level, vol_tolerance,
                                                investment_horizon)
            fund['recommendation_score'] = score
            scored_funds.append(fund)

        # Sort by score descending
        scored_funds.sort(key=lambda x: x['recommendation_score'], reverse=True)

        # Get top N recommendations
        top_funds = scored_funds[:top_n]

        # Generate insights for each fund
        recommendations = []
        for fund in top_funds:
            recommendation = self._generate_fund_insight(fund, investment_amount,
                                                          investment_horizon)
            recommendations.append(recommendation)

        return {
            'risk_profile': risk_profile,
            'investment_amount': investment_amount,
            'investment_horizon': investment_horizon,
            'recommendations': recommendations,
            'total_funds_analyzed': len(funds)
        }

    def _calculate_fund_score(self, fund: Dict, risk_level: int,
                               vol_tolerance: float, horizon: int) -> float:
        """Calculate recommendation score for a fund"""
        score = 0

        # Rating contribution (0-25 points)
        rating = fund.get('rating', 0)
        score += rating * 5

        # Sharpe ratio contribution (0-25 points)
        sharpe = fund.get('sharpe', 0)
        score += min(25, sharpe * 10)

        # Sortino ratio contribution (0-15 points)
        sortino = fund.get('sortino', 0)
        score += min(15, sortino * 5)

        # Alpha contribution (0-15 points)
        alpha = fund.get('alpha', 0)
        score += min(15, max(0, alpha * 2))

        # Returns contribution based on horizon (0-20 points)
        if horizon <= 1:
            returns = fund.get('returns_1yr', 0)
        elif horizon <= 3:
            returns = fund.get('returns_3yr', 0)
        else:
            returns = fund.get('returns_5yr', 0)
        score += min(20, max(0, returns * 0.5))

        # Risk alignment penalty
        fund_risk = fund.get('risk_level', 3)
        risk_diff = abs(fund_risk - risk_level)
        score -= risk_diff * 5

        # Volatility alignment
        fund_vol = fund.get('sd', 20)
        if fund_vol > vol_tolerance:
            score -= (fund_vol - vol_tolerance) * 0.5

        # Expense ratio penalty
        expense = fund.get('expense_ratio', 1)
        score -= expense * 3

        # Fund size bonus (larger funds are more stable)
        fund_size = fund.get('fund_size_cr', 0)
        if fund_size > 1000:
            score += 5
        elif fund_size > 500:
            score += 3

        # Fund age bonus
        fund_age = fund.get('fund_age_yr', 0)
        if fund_age >= 5:
            score += 3

        return max(0, score)

    def _generate_fund_insight(self, fund: Dict, investment_amount: float,
                                horizon: int) -> Dict:
        """Generate detailed insights for a recommended fund"""

        # Monte Carlo prediction
        current_nav = 100  # Normalized NAV
        annual_return = fund.get('returns_1yr', 10)
        volatility = fund.get('sd', 15)

        # Predict for investment horizon
        prediction = monte_carlo.predict_nav(
            current_nav=investment_amount,
            annual_return=annual_return,
            volatility=volatility,
            days=horizon * 252
        )

        # Risk metrics
        risk_premium = black_scholes.calculate_risk_premium(
            current_nav=100,
            expected_nav=100 * (1 + annual_return/100),
            volatility=volatility/100
        )

        return {
            'fund_id': fund.get('fund_id'),
            'scheme_name': fund.get('scheme_name', ''),
            'amc_name': fund.get('amc_name', ''),
            'category': fund.get('category', ''),
            'sub_category': fund.get('sub_category', ''),
            'recommendation_score': round(fund.get('recommendation_score', 0), 2),
            'rating': fund.get('rating', 0),
            'metrics': {
                'returns': {
                    '1yr': fund.get('returns_1yr', 0),
                    '3yr': fund.get('returns_3yr', 0),
                    '5yr': fund.get('returns_5yr', 0)
                },
                'risk': {
                    'alpha': fund.get('alpha', 0),
                    'beta': fund.get('beta', 0),
                    'sharpe': fund.get('sharpe', 0),
                    'sortino': fund.get('sortino', 0),
                    'std_dev': fund.get('sd', 0),
                    'risk_level': fund.get('risk_level', 0)
                }
            },
            'prediction': {
                'expected_value': prediction['statistics']['mean_nav'],
                'expected_return_pct': prediction['statistics']['expected_return_pct'],
                'confidence_90': prediction['confidence_intervals']['90%'],
                'probability_of_loss': prediction['risk_metrics']['probability_of_loss'],
                'var_95': prediction['risk_metrics']['var_95']
            },
            'risk_analysis': risk_premium,
            'fund_details': {
                'expense_ratio': fund.get('expense_ratio', 0),
                'fund_size_cr': fund.get('fund_size_cr', 0),
                'fund_age_yr': fund.get('fund_age_yr', 0),
                'fund_manager': fund.get('fund_manager', ''),
                'min_sip': fund.get('min_sip', 0),
                'min_lumpsum': fund.get('min_lumpsum', 0)
            },
            'insights': self._generate_text_insights(fund, prediction, risk_premium)
        }

    def _generate_text_insights(self, fund: Dict, prediction: Dict,
                                 risk_premium: Dict) -> List[str]:
        """Generate human-readable insights for a fund"""
        insights = []

        # Return insights
        returns_1yr = fund.get('returns_1yr', 0)
        if returns_1yr > 15:
            insights.append(f"Strong 1-year returns of {returns_1yr}%")
        elif returns_1yr > 10:
            insights.append(f"Good 1-year returns of {returns_1yr}%")

        # Risk-adjusted return insight
        sharpe = fund.get('sharpe', 0)
        if sharpe > 1.5:
            insights.append("Excellent risk-adjusted returns (Sharpe > 1.5)")
        elif sharpe > 1:
            insights.append("Good risk-adjusted returns (Sharpe > 1)")

        # Consistency insight
        alpha = fund.get('alpha', 0)
        if alpha > 2:
            insights.append(f"Consistently outperforms benchmark (Alpha: {alpha})")

        # Risk insight
        prob_loss = prediction['risk_metrics']['probability_of_loss']
        if prob_loss < 20:
            insights.append(f"Low probability of loss ({prob_loss}%)")
        elif prob_loss > 40:
            insights.append(f"Higher probability of loss ({prob_loss}%) - suitable for aggressive investors")

        # Fund quality insight
        rating = fund.get('rating', 0)
        if rating >= 4:
            insights.append(f"Highly rated fund ({rating}/5 stars)")

        # Experience insight
        fund_age = fund.get('fund_age_yr', 0)
        if fund_age >= 10:
            insights.append(f"Well-established fund with {fund_age} years track record")

        return insights

    def get_category_recommendations(self, category: str, top_n: int = 5) -> Dict:
        """Get top recommendations within a specific category"""
        return self.get_recommendations(categories=[category], top_n=top_n)

    def get_sip_recommendations(self, monthly_amount: float,
                                risk_level: int = 3,
                                horizon: int = 5) -> Dict:
        """Get SIP-focused recommendations"""
        funds, _ = self.data_processor.get_all_funds(limit=1000)

        # Filter funds suitable for SIP
        sip_suitable = [f for f in funds if f.get('min_sip', 0) <= monthly_amount]

        # Score and sort
        for fund in sip_suitable:
            score = self._calculate_fund_score(fund, risk_level, 20, horizon)
            fund['recommendation_score'] = score

        sip_suitable.sort(key=lambda x: x['recommendation_score'], reverse=True)

        return {
            'monthly_amount': monthly_amount,
            'risk_level': risk_level,
            'horizon': horizon,
            'recommendations': sip_suitable[:10]
        }

    def optimize_portfolio(self, fund_ids: List[int],
                           investment_amount: float = 100000,
                           investor_views: Optional[List[Dict]] = None) -> Dict:
        """
        Optimize portfolio allocation for selected funds using Black-Litterman
        """
        # Get fund data
        funds = [self.data_processor.get_fund_by_id(fid) for fid in fund_ids]
        funds = [f for f in funds if f is not None]

        if len(funds) < 2:
            return {'error': 'At least 2 funds required for portfolio optimization'}

        # Run Black-Litterman optimization
        optimization_result = create_portfolio_optimizer(funds, investor_views)

        # Add investment amounts
        for alloc in optimization_result['allocations']:
            alloc['investment_amount'] = round(investment_amount * alloc['weight'] / 100, 2)

        return optimization_result

    def compare_funds(self, fund_ids: List[int]) -> Dict:
        """Compare multiple funds side by side"""
        funds = [self.data_processor.get_fund_by_id(fid) for fid in fund_ids]
        funds = [f for f in funds if f is not None]

        if not funds:
            return {'error': 'No valid funds found'}

        comparison = []
        for fund in funds:
            comparison.append({
                'fund_id': fund.get('fund_id'),
                'scheme_name': fund.get('scheme_name'),
                'amc_name': fund.get('amc_name'),
                'category': fund.get('category'),
                'rating': fund.get('rating'),
                'returns_1yr': fund.get('returns_1yr'),
                'returns_3yr': fund.get('returns_3yr'),
                'returns_5yr': fund.get('returns_5yr'),
                'sharpe': fund.get('sharpe'),
                'sortino': fund.get('sortino'),
                'alpha': fund.get('alpha'),
                'beta': fund.get('beta'),
                'std_dev': fund.get('sd'),
                'expense_ratio': fund.get('expense_ratio'),
                'fund_size_cr': fund.get('fund_size_cr')
            })

        # Determine best in each category
        metrics = ['returns_1yr', 'returns_3yr', 'returns_5yr', 'sharpe', 'sortino', 'alpha']
        best_in = {}

        for metric in metrics:
            valid_funds = [f for f in comparison if f.get(metric) is not None]
            if valid_funds:
                best_fund = max(valid_funds, key=lambda x: x.get(metric, 0))
                best_in[metric] = best_fund['fund_id']

        return {
            'funds': comparison,
            'best_in_category': best_in
        }


# Singleton instance
recommendation_engine = FundRecommendationEngine()


def get_engine() -> FundRecommendationEngine:
    """Get the recommendation engine singleton"""
    return recommendation_engine
