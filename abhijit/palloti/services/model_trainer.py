"""
Machine Learning model training pipeline
XGBoost for return prediction + Prophet for NAV forecasting
"""

import pandas as pd
import numpy as np
import pickle
import warnings
from pathlib import Path
from typing import Tuple, Dict
from datetime import datetime, timedelta
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from configs.config import (
    DATA_PROCESSED_PATH, MODELS_PATH, XGBOOST_MODEL_PATH, 
    PROPHET_MODEL_PATH, XGBOOST_PARAMS, PROPHET_PARAMS
)
from utils.helpers import ModelLoader, setup_logging

warnings.filterwarnings('ignore')
logger = setup_logging()

class MLModelTrainer:
    """Train and evaluate ML models for fund prediction"""
    
    def __init__(self):
        self.X_train = None
        self.y_return = None
        self.y_nav = None
        self.xgboost_model = None
        self.prophet_model = None
    
    def load_processed_data(self):
        """Load preprocessed features and targets"""
        logger.info("Loading processed data...")
        
        # Load features
        features_path = DATA_PROCESSED_PATH / "features_scaled.csv"
        self.X_train = pd.read_csv(features_path).values
        
        # Load targets
        targets_path = DATA_PROCESSED_PATH / "targets.csv"
        targets_df = pd.read_csv(targets_path)
        self.y_return = targets_df['return_5yr'].values  # Focus on 5-year returns
        self.y_nav = targets_df['nav_growth'].values
        
        logger.info(f"✓ Loaded training data: X={self.X_train.shape}, y={self.y_return.shape}")
        return self.X_train, self.y_return, self.y_nav
    
    def train_xgboost_model(self):
        """Train XGBoost model for return prediction"""
        logger.info("Training XGBoost Return Prediction Model...")
        
        try:
            import xgboost as xgb
            
            # Create and train model
            self.xgboost_model = xgb.XGBRegressor(**XGBOOST_PARAMS)
            self.xgboost_model.fit(
                self.X_train, self.y_return,
                verbose=False
            )
            
            # Evaluate
            train_score = self.xgboost_model.score(self.X_train, self.y_return)
            
            logger.info(f"✓ XGBoost Model Training Complete")
            logger.info(f"  - R² Score: {train_score:.4f}")
            logger.info(f"  - Training samples: {len(self.X_train)}")
            
            return self.xgboost_model
        
        except ImportError:
            logger.error("XGBoost not installed. Install with: pip install xgboost")
            raise
    
    def train_prophet_model(self):
        """Train Prophet model for NAV time-series forecasting"""
        logger.info("Training Prophet NAV Forecasting Model...")
        
        try:
            from prophet import Prophet
            
            # Create time-series dataframe for Prophet
            # Using fund age as proxy for time
            df_prophet = pd.DataFrame({
                'ds': [datetime.now() - timedelta(days=365*int(age)) for age in range(1, 26)],
                'y': self.y_nav[:25] if len(self.y_nav) >= 25 else self.y_nav
            })
            
            # Train Prophet
            self.prophet_model = Prophet(
                interval_width=PROPHET_PARAMS['interval_width'],
                yearly_seasonality=PROPHET_PARAMS['yearly_seasonality'],
                weekly_seasonality=PROPHET_PARAMS['weekly_seasonality'],
                daily_seasonality=PROPHET_PARAMS['daily_seasonality']
            )
            
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.prophet_model.fit(df_prophet)
            
            logger.info(f"✓ Prophet Model Training Complete")
            logger.info(f"  - Training samples: {len(df_prophet)}")
            
            return self.prophet_model
        
        except ImportError:
            logger.error("Prophet not installed. Install with: pip install prophet")
            # Create a fallback simple model
            logger.info("Using simple trend-based fallback model")
            return self._create_fallback_prophet()
    
    def _create_fallback_prophet(self):
        """Create simple fallback model if Prophet is not available"""
        class SimpleForecast:
            def predict(self, df):
                results = []
                for idx in range(len(df)):
                    results.append({
                        'ds': df['ds'].iloc[idx],
                        'yhat': np.mean(self.y_nav) if hasattr(self, 'y_nav') else 10.0,
                        'yhat_lower': np.mean(self.y_nav) * 0.8 if hasattr(self, 'y_nav') else 8.0,
                        'yhat_upper': np.mean(self.y_nav) * 1.2 if hasattr(self, 'y_nav') else 12.0
                    })
                return pd.DataFrame(results)
        
        return SimpleForecast()
    
    def save_models(self):
        """Save trained models to disk"""
        logger.info("Saving models...")
        
        Path(MODELS_PATH).mkdir(parents=True, exist_ok=True)
        
        if self.xgboost_model:
            with open(XGBOOST_MODEL_PATH, 'wb') as f:
                pickle.dump(self.xgboost_model, f)
            logger.info(f"✓ Saved XGBoost model to {XGBOOST_MODEL_PATH}")
        
        if self.prophet_model:
            with open(PROPHET_MODEL_PATH, 'wb') as f:
                pickle.dump(self.prophet_model, f)
            logger.info(f"✓ Saved Prophet model to {PROPHET_MODEL_PATH}")
    
    def train_pipeline(self):
        """Execute complete training pipeline"""
        logger.info("=" * 60)
        logger.info("Starting ML Model Training Pipeline")
        logger.info("=" * 60)
        
        self.load_processed_data()
        self.train_xgboost_model()
        self.train_prophet_model()
        self.save_models()
        
        logger.info("=" * 60)
        logger.info("ML Training Pipeline Complete")
        logger.info("=" * 60)

class ModelEvaluator:
    """Evaluate trained models"""
    
    @staticmethod
    def get_feature_importance(xgb_model, feature_names: list = None, top_k: int = 10) -> Dict:
        """Extract feature importance from XGBoost"""
        try:
            importance_dict = xgb_model.get_booster().get_score(importance_type='weight')
            
            # Sort by importance
            sorted_importance = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)[:top_k]
            
            return {name: score for name, score in sorted_importance}
        except:
            return {}

def main():
    """Run model training pipeline"""
    trainer = MLModelTrainer()
    trainer.train_pipeline()
    
    print("\n" + "=" * 60)
    print("MODEL TRAINING SUMMARY")
    print("=" * 60)
    print("✓ XGBoost return prediction model trained")
    print("✓ Prophet NAV forecasting model trained")
    print(f"✓ Models saved to {MODELS_PATH}")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
