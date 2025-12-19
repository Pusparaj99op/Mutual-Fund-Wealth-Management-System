"""
Configuration settings for the Federal Wealth Management System
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW_PATH = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_PATH = PROJECT_ROOT / "data" / "processed"
MODELS_PATH = PROJECT_ROOT / "models"

# Dataset paths - Updated to use existing dataset
DATASET_PATH = Path(__file__).parent.parent.parent.parent / "PS" / "dataset" / "MF_India_AI.json"

# Model paths
XGBOOST_MODEL_PATH = MODELS_PATH / "xgboost_returns.pkl"
PROPHET_MODEL_PATH = MODELS_PATH / "prophet_nav_forecast.pkl"
SCALER_PATH = MODELS_PATH / "feature_scaler.pkl"
ENCODER_PATH = MODELS_PATH / "categorical_encoder.pkl"

# FastAPI settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
API_TITLE = "Federal Wealth Management System API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "AI-powered mutual fund recommendation and prediction system"

# Streamlit settings
STREAMLIT_THEME = "light"
STREAMLIT_LAYOUT = "wide"

# ML Model settings
XGBOOST_PARAMS = {
    "max_depth": 7,
    "learning_rate": 0.1,
    "n_estimators": 200,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "random_state": 42,
    "objective": "reg:squarederror"
}

PROPHET_PARAMS = {
    "interval_width": 0.95,
    "yearly_seasonality": True,
    "weekly_seasonality": False,
    "daily_seasonality": False
}

# Recommendation engine settings
TOP_K_RECOMMENDATIONS = 5
MIN_RATING_FILTER = 3.0
MAX_RISK_TOLERANCE_MONTHS = {
    6: 2,
    12: 3,
    36: 4,
    60: 5,
    120: 6
}

# Feature engineering
FEATURE_COLUMNS = [
    'min_sip', 'min_lumpsum', 'expense_ratio', 'fund_size_cr',
    'fund_age_yr', 'risk_level', 'alpha', 'beta', 'sharpe',
    'sortino', 'sd', 'rating', 'returns_1yr',
    'returns_3yr', 'returns_5yr'
]

CATEGORICAL_COLUMNS = ['amc_name', 'category', 'sub_category']

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = PROJECT_ROOT / "logs" / "app.log"

# API defaults
DEFAULT_INVESTMENT_TENURE_MONTHS = 60
DEFAULT_INVESTMENT_AMOUNT = 100000
DEFAULT_RISK_TOLERANCE = 4
