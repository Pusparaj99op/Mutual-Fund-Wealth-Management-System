"""
Utility functions for data processing, model loading, and helpers
"""

import json
import pickle
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DataLoader:
    """Load and manage mutual fund dataset"""
    
    @staticmethod
    def load_dataset(filepath: str) -> pd.DataFrame:
        """Load mutual fund dataset from JSON"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            logger.info(f" Loaded {len(df)} mutual funds from {filepath}")
            return df
        except FileNotFoundError:
            logger.error(f"Dataset not found at {filepath}")
            raise
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON format in {filepath}")
            raise
    
    @staticmethod
    def get_fund_by_id(df: pd.DataFrame, scheme_id: str) -> Optional[Dict]:
        """Get fund details by scheme ID"""
        result = df[df['scheme_id'] == scheme_id]
        if len(result) > 0:
            return result.iloc[0].to_dict()
        return None
    
    @staticmethod
    def get_funds_by_category(df: pd.DataFrame, category: str) -> pd.DataFrame:
        """Get all funds in a category"""
        return df[df['category'] == category]

class ModelLoader:
    """Load and cache trained ML models"""
    
    _models_cache = {}
    
    @staticmethod
    def load_model(model_path: str, model_name: str = None):
        """Load pickle-based ML model with caching"""
        try:
            if model_path in ModelLoader._models_cache:
                logger.info(f" Loaded {model_name or model_path} from cache")
                return ModelLoader._models_cache[model_path]
            
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            ModelLoader._models_cache[model_path] = model
            logger.info(f"Loaded {model_name or model_path}")
            return model
        except FileNotFoundError:
            logger.warning(f"Model not found at {model_path}. Model training may be required.")
            return None
        except Exception as e:
            logger.error(f"Error loading model from {model_path}: {str(e)}")
            return None
    
    @staticmethod
    def save_model(model, model_path: str, model_name: str = None):
        """Save ML model to pickle"""
        try:
            Path(model_path).parent.mkdir(parents=True, exist_ok=True)
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            logger.info(f"Saved {model_name or 'model'} to {model_path}")
        except Exception as e:
            logger.error(f"Error saving model to {model_path}: {str(e)}")
            raise

class FeatureEngineer:
    """Feature engineering and data transformation"""
    
    @staticmethod
    def extract_features(df: pd.DataFrame, feature_columns: List[str]) -> Tuple[pd.DataFrame, np.ndarray]:
        """Extract numerical features"""
        X = df[feature_columns].copy()
        X = X.fillna(X.mean(numeric_only=True))
        return X, X.values
    
    @staticmethod
    def encode_categorical(df: pd.DataFrame, categorical_columns: List[str], encoder=None) -> Tuple[pd.DataFrame, Any]:
        """Encode categorical features using OneHotEncoder"""
        from sklearn.preprocessing import OneHotEncoder
        
        if encoder is None:
            encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
            X_encoded = encoder.fit_transform(df[categorical_columns])
        else:
            X_encoded = encoder.transform(df[categorical_columns])
        
        encoded_df = pd.DataFrame(
            X_encoded,
            columns=encoder.get_feature_names_out(categorical_columns)
        )
        return encoded_df, encoder
    
    @staticmethod
    def combine_features(X_numerical: pd.DataFrame, X_categorical: pd.DataFrame) -> pd.DataFrame:
        """Combine numerical and categorical features"""
        return pd.concat([X_numerical.reset_index(drop=True), X_categorical.reset_index(drop=True)], axis=1)
    
    @staticmethod
    def scale_features(X: np.ndarray, scaler=None) -> Tuple[np.ndarray, Any]:
        """Standardize features"""
        from sklearn.preprocessing import StandardScaler
        
        if scaler is None:
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
        else:
            X_scaled = scaler.transform(X)
        
        return X_scaled, scaler

class MetricsCalculator:
    """Calculate risk and return metrics"""
    
    @staticmethod
    def calculate_return_trend(returns: List[float]) -> float:
        """Calculate trend in returns over time"""
        if len(returns) < 2:
            return 0.0
        x = np.arange(len(returns))
        y = np.array(returns)
        z = np.polyfit(x, y, 1)
        return float(z[0])
    
    @staticmethod
    def calculate_volatility_adjusted_return(return_val: float, volatility: float) -> float:
        """Calculate volatility-adjusted return"""
        if volatility == 0:
            return 0.0
        return return_val / volatility
    
    @staticmethod
    def calculate_risk_score(risk_level: int, std_dev: float, beta: float) -> float:
        """Calculate composite risk score (0-10)"""
        risk_score = (risk_level / 6.0) * 5 + (min(std_dev / 25.0, 1.0) * 3) + (min(abs(beta), 2.0) / 2.0 * 2)
        return min(max(risk_score, 0), 10)
    
    @staticmethod
    def calculate_overall_score(fund: Dict) -> float:
        """Calculate overall fund score for ranking"""
        rating_score = (fund.get('rating', 3) / 5.0) * 30
        return_score = min(max(fund.get('return_5yr', 0), 0), 30) / 30.0 * 30
        sharpe_score = min(fund.get('sharpe_ratio', 1) / 3.0, 1.0) * 25
        expense_score = (1 - min(fund.get('expense_ratio', 1.5) / 2.5, 1.0)) * 15
        
        total_score = rating_score + return_score + sharpe_score + expense_score
        return round(total_score, 2)

class ExplainabilityHelper:
    """Generate explanations for recommendations using SHAP-like logic"""
    
    @staticmethod
    def generate_fund_explanation(fund: Dict, predicted_return: float, score: float) -> Dict:
        """Generate human-readable explanation for a recommendation"""
        
        strengths = []
        weaknesses = []
        
        # Rating analysis
        if fund.get('rating', 0) >= 4.5:
            strengths.append(f"Excellent rating ({fund['rating']}/5)")
        elif fund.get('rating', 0) < 3.0:
            weaknesses.append(f"Lower rating ({fund['rating']}/5)")
        
        # Return analysis
        if fund.get('return_5yr', 0) > 15:
            strengths.append(f"Strong 5-year returns ({fund['return_5yr']}%)")
        elif fund.get('return_5yr', 0) < 5:
            weaknesses.append(f"Modest 5-year returns ({fund['return_5yr']}%)")
        
        # Risk analysis
        if fund.get('risk_level', 3) <= 3:
            strengths.append("Low-to-moderate risk profile")
        elif fund.get('risk_level', 3) >= 5:
            weaknesses.append("Higher risk - suitable for aggressive investors")
        
        # Expense ratio
        if fund.get('expense_ratio', 1.0) < 0.8:
            strengths.append(f"Low expense ratio ({fund['expense_ratio']}%)")
        elif fund.get('expense_ratio', 1.0) > 1.5:
            weaknesses.append(f"Higher expense ratio ({fund['expense_ratio']}%)")
        
        # Sharpe ratio
        if fund.get('sharpe_ratio', 1.0) > 2.0:
            strengths.append(f"Superior risk-adjusted returns (Sharpe: {fund['sharpe_ratio']})")
        
        explanation = {
            "recommendation_score": round(score, 2),
            "predicted_return_5yr": round(predicted_return, 2),
            "strengths": strengths if strengths else ["Meets selection criteria"],
            "weaknesses": weaknesses if weaknesses else [],
            "investment_rationale": f"This fund ranks in the top selections based on predicted returns "
                                   f"({predicted_return:.1f}%), risk-adjusted metrics, and historical performance."
        }
        
        return explanation

def setup_logging(log_file: Optional[str] = None) -> logging.Logger:
    """Setup application logging"""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # File handler
    handlers = [console_handler]
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    for handler in handlers:
        root_logger.addHandler(handler)
    
    return root_logger

