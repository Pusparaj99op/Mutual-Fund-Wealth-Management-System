"""
Hybrid Recommendation Engine with ML ranking and SHAP explainability
"""

import pandas as pd
import numpy as np
import warnings
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from configs.config import (
    TOP_K_RECOMMENDATIONS, MIN_RATING_FILTER,
    MAX_RISK_TOLERANCE_MONTHS, SCALER_PATH, ENCODER_PATH
)
from utils.helpers import (
    DataLoader, ModelLoader, MetricsCalculator,
    ExplainabilityHelper, setup_logging
)

warnings.filterwarnings('ignore')
logger = setup_logging()

class RecommendationEngine:
    """Hybrid recommendation system combining rules and ML"""

    def __init__(self, dataset_path: str):
        self.df = DataLoader.load_dataset(dataset_path)
        self.model_loader = ModelLoader()
        self.xgb_model = None
        self.scaler = None
        self.encoder = None
        self.load_models()

    def load_models(self):
        """Load trained models and transformers"""
        self.xgb_model = self.model_loader.load_model(str(SCALER_PATH), "Scaler")
        self.scaler = self.model_loader.load_model(str(SCALER_PATH), "Feature Scaler")
        self.encoder = self.model_loader.load_model(str(ENCODER_PATH), "Categorical Encoder")

    def filter_by_investment_amount(
        self,
        investment_amount: float,
        investment_type: str = "sip"  # "sip" or "lumpsum"
    ) -> pd.DataFrame:
        """Filter funds by minimum investment requirement"""
        if investment_type.lower() == "sip":
            return self.df[self.df['min_sip'] <= investment_amount]
        else:  # lumpsum
            return self.df[self.df['min_lumpsum'] <= investment_amount]

    def filter_by_tenure(self, tenure_months: int) -> pd.DataFrame:
        """Filter funds based on investment tenure and risk tolerance"""
        max_risk = MAX_RISK_TOLERANCE_MONTHS.get(tenure_months, 3)
        return self.df[self.df['risk_level'] <= max_risk]

    def filter_by_category(self, category: Optional[str] = None) -> pd.DataFrame:
        """Filter funds by category preference"""
        if category is None:
            return self.df
        return self.df[self.df['category'] == category]

    def filter_by_rating(self, min_rating: float = MIN_RATING_FILTER) -> pd.DataFrame:
        """Filter funds with minimum rating"""
        return self.df[self.df['rating'] >= min_rating]

    def predict_returns(self, funds_df: pd.DataFrame) -> np.ndarray:
        """Predict fund returns using trained XGBoost model"""
        try:
            from configs.config import XGBOOST_MODEL_PATH
            xgb_model = self.model_loader.load_model(str(XGBOOST_MODEL_PATH), "XGBoost")

            if xgb_model is None:
                logger.warning("XGBoost model not found, using historical returns")
                return funds_df['returns_5yr'].values

            # Prepare features (simplified - using key metrics)
            features_for_prediction = funds_df[[
                'expense_ratio', 'risk_level', 'alpha', 'sharpe', 'rating'
            ]].fillna(0).values

            # Predict
            predictions = xgb_model.predict(features_for_prediction)
            return predictions

        except Exception as e:
            logger.warning(f"Error in model prediction: {str(e)}. Using historical returns.")
            return funds_df['returns_5yr'].values

    def rank_funds(self, funds_df: pd.DataFrame, predicted_returns: np.ndarray) -> pd.DataFrame:
        """Rank funds using composite scoring"""

        funds_copy = funds_df.copy()
        scores = []

        for idx, (_, fund) in enumerate(funds_copy.iterrows()):
            # Composite score calculation
            predicted_return = predicted_returns[idx] if idx < len(predicted_returns) else fund['returns_5yr']

            # Component scores (each 0-100)
            rating_score = (fund['rating'] / 5.0) * 100
            return_score = min(max(predicted_return, 0), 50) / 50.0 * 100
            sharpe_score = min(fund['sharpe'] / 3.0, 1.0) * 100
            expense_score = (1 - min(fund['expense_ratio'] / 2.5, 1.0)) * 100
            risk_score = (1 - (fund['risk_level'] / 6.0)) * 100

            # Weighted composite score
            composite_score = (
                rating_score * 0.25 +
                return_score * 0.35 +
                sharpe_score * 0.20 +
                expense_score * 0.10 +
                risk_score * 0.10
            )

            scores.append(composite_score)

        funds_copy['recommendation_score'] = scores
        funds_copy['predicted_return_5yr'] = predicted_returns

        # Sort by score
        return funds_copy.sort_values('recommendation_score', ascending=False)

    def get_recommendations(
        self,
        investment_amount: float,
        investment_type: str = "sip",
        tenure_months: int = 60,
        category: Optional[str] = None,
        k: int = TOP_K_RECOMMENDATIONS
    ) -> Tuple[List[Dict], Dict]:
        """
        Get top-K fund recommendations with explanations

        Args:
            investment_amount: Investment amount in rupees
            investment_type: "sip" or "lumpsum"
            tenure_months: Investment tenure in months
            category: Fund category (optional)
            k: Number of recommendations to return

        Returns:
            Tuple of (recommendations list, filtering stats)
        """

        logger.info(f"Generating recommendations for ₹{investment_amount:,} {investment_type.upper()}")

        # Apply filters sequentially
        filtered_df = self.df.copy()
        initial_count = len(filtered_df)

        filtered_df = self.filter_by_investment_amount(investment_amount, investment_type)
        logger.info(f"After investment filter: {len(filtered_df)} funds")

        filtered_df = filtered_df[filtered_df.index.isin(self.filter_by_tenure(tenure_months).index)]
        logger.info(f"After tenure/risk filter: {len(filtered_df)} funds")

        filtered_df = filtered_df[filtered_df.index.isin(self.filter_by_category(category).index)]
        logger.info(f"After category filter: {len(filtered_df)} funds")

        filtered_df = filtered_df[filtered_df.index.isin(self.filter_by_rating().index)]
        logger.info(f"After rating filter: {len(filtered_df)} funds")

        if len(filtered_df) == 0:
            logger.warning("No funds match criteria. Returning top-rated funds.")
            filtered_df = self.df.nlargest(k, 'rating')

        # Predict returns and rank
        predicted_returns = self.predict_returns(filtered_df)
        ranked_df = self.rank_funds(filtered_df, predicted_returns)

        # Get top-K
        top_funds = ranked_df.head(k)

        # Generate recommendations with explanations
        recommendations = []
        for _, fund in top_funds.iterrows():
            recommendation = {
                "scheme_id": fund['scheme_id'],
                "scheme_name": fund['scheme_name'],
                "amc_name": fund['amc_name'],
                "category": fund['category'],
                "sub_category": fund['sub_category'],
                "rating": float(fund['rating']),
                "risk_level": int(fund['risk_level']),
                "recommendation_score": round(float(fund['recommendation_score']), 2),
                "predicted_return_5yr": round(float(fund['predicted_return_5yr']), 2),
                "historical_return_5yr": round(float(fund['returns_5yr']), 2),
                "sharpe_ratio": round(float(fund['sharpe']), 2),
                "expense_ratio": round(float(fund['expense_ratio']), 2),
                "min_sip": int(fund['min_sip']),
                "min_lumpsum": int(fund['min_lumpsum']),
                "explanation": ExplainabilityHelper.generate_fund_explanation(
                    fund.to_dict(),
                    float(fund['predicted_return_5yr']),
                    float(fund['recommendation_score'])
                )
            }
            recommendations.append(recommendation)

        # Generate filtering stats
        stats = {
            "total_funds_in_database": initial_count,
            "funds_after_filtering": len(filtered_df),
            "recommendations_provided": len(recommendations),
            "filters_applied": {
                "investment_amount": f"₹{investment_amount:,}",
                "investment_type": investment_type.upper(),
                "tenure_months": tenure_months,
                "category": category or "All",
                "min_rating": MIN_RATING_FILTER
            }
        }

        logger.info(f"✓ Generated {len(recommendations)} recommendations")

        return recommendations, stats

    def get_fund_comparison(self, scheme_ids: List[str]) -> pd.DataFrame:
        """Get comparison data for selected funds"""
        comparison_data = []
        for scheme_id in scheme_ids:
            fund = self.df[self.df['scheme_id'] == scheme_id]
            if len(fund) > 0:
                comparison_data.append(fund.iloc[0])

        return pd.DataFrame(comparison_data) if comparison_data else pd.DataFrame()

class SHAPExplainer:
    """Generate SHAP-like explainability for recommendations"""

    @staticmethod
    def get_feature_contribution(fund: Dict, top_features: int = 5) -> Dict:
        """
        Get feature contribution scores for a fund's recommendation
        Simulates SHAP values
        """

        # Normalize features to 0-1
        features_impact = {
            "Rating": min(fund.get('rating', 3) / 5.0, 1.0) * 25,
            "Sharpe Ratio": min(fund.get('sharpe', 1) / 3.0, 1.0) * 20,
            "Return (5yr)": min(max(fund.get('returns_5yr', 0), 0), 30) / 30.0 * 25,
            "Expense Ratio": (1 - min(fund.get('expense_ratio', 1) / 2.5, 1.0)) * 15,
            "Risk Adjusted": (1 - (fund.get('risk_level', 3) / 6.0)) * 15
        }

        # Sort and return top features
        sorted_features = sorted(features_impact.items(), key=lambda x: x[1], reverse=True)

        return {
            "top_contributing_factors": {name: round(score, 2) for name, score in sorted_features[:top_features]},
            "total_impact_score": round(sum([score for _, score in sorted_features]), 2)
        }

def main():
    """Test recommendation engine"""
    from configs.config import DATASET_PATH

    logger.info("Initializing Recommendation Engine")
    engine = RecommendationEngine(str(DATASET_PATH))

    # Test recommendation
    recommendations, stats = engine.get_recommendations(
        investment_amount=100000,
        investment_type="sip",
        tenure_months=60,
        category=None,
        k=5
    )

    print("\n" + "=" * 60)
    print("RECOMMENDATION ENGINE TEST")
    print("=" * 60)
    print(f"Total recommendations: {len(recommendations)}")
    print(f"Filtering stats: {stats['filters_applied']}")
    if recommendations:
        print(f"\nTop recommendation: {recommendations[0]['scheme_name']}")
        print(f"Score: {recommendations[0]['recommendation_score']}")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
