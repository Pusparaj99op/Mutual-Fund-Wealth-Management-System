# 📋 PROJECT STRUCTURE & FILE MANIFEST

## Federal Wealth Management System - Complete File List

---

## 📂 Root Directory Files

| File | Purpose | Size |
|------|---------|------|
| `main.py` | **Entry point** - Orchestrates initialization and services | ~4 KB |
| `requirements.txt` | **Dependencies** - All Python packages needed | ~1 KB |
| `.env.example` | **Config template** - Environment variables | ~1 KB |
| `.gitignore` | **Git config** - Files to ignore in version control | ~2 KB |
| `README.md` | **Main documentation** - Complete guide | ~25 KB |
| `API_REFERENCE.md` | **API docs** - Endpoint specifications | ~20 KB |
| `STARTUP_GUIDE.md` | **Setup instructions** - Quick start guide | ~15 KB |
| `quickstart.bat` | **Batch script** - Windows auto-setup | ~2 KB |
| `quickstart.sh` | **Shell script** - Mac/Linux auto-setup | ~2 KB |

---

## 🗂️ Directory Structure

### `data/` - Data Management
```
data/
├── __init__.py
├── generate_dataset.py          [Dataset generator - 150 synthetic funds]
├── raw/
│   └── MF_India_AI.json        [Generated: mutual fund data]
└── processed/
    ├── processed_funds.csv     [Generated: cleaned data]
    ├── features_scaled.csv     [Generated: normalized features]
    └── targets.csv             [Generated: ML targets]
```

**Key Files:**
- `generate_dataset.py` - Creates realistic Indian MF data with:
  - 15+ AMCs (asset management companies)
  - 5 main categories + subcategories
  - Realistic returns, risk metrics, ratings
  - 150 different fund options

---

### `models/` - Trained ML Models
```
models/
├── xgboost_returns.pkl         [Trained: Return prediction model]
├── prophet_nav_forecast.pkl    [Trained: Time-series forecast model]
├── feature_scaler.pkl          [Trained: Feature standardizer]
└── categorical_encoder.pkl     [Trained: Category encoder]
```

**Files Generated During Training:**
- `xgboost_returns.pkl` - XGBoost regressor for 5-year return prediction
- `prophet_nav_forecast.pkl` - Prophet model for NAV forecasting
- `feature_scaler.pkl` - StandardScaler for feature normalization
- `categorical_encoder.pkl` - OneHotEncoder for categorical features

---

### `services/` - Business Logic & Pipelines
```
services/
├── __init__.py
├── data_preprocessing.py        [Feature engineering pipeline - 350 lines]
├── model_trainer.py             [ML model training - 280 lines]
└── recommendation_engine.py     [Recommendation logic - 450 lines]
```

**Key Modules:**

1. **data_preprocessing.py** - DataPreprocessor class
   - `load_data()` - Load JSON dataset
   - `clean_data()` - Remove duplicates, handle missing values
   - `extract_features()` - Extract 15+ numerical features
   - `encode_categorical()` - One-hot encode 3 categorical columns
   - `scale_features()` - Standardize with StandardScaler
   - `prepare_targets()` - Create ML target variables
   - `save_processed_data()` - Save to CSV and pickle artifacts

2. **model_trainer.py** - MLModelTrainer class
   - `train_xgboost_model()` - XGBoost with 200 estimators
   - `train_prophet_model()` - Prophet time-series model
   - `save_models()` - Pickle serialization
   - Features: max_depth=7, learning_rate=0.1

3. **recommendation_engine.py** - RecommendationEngine class
   - `filter_by_investment_amount()` - SIP/Lumpsum filtering
   - `filter_by_tenure()` - Risk-tenure alignment
   - `filter_by_category()` - Category preference
   - `filter_by_rating()` - Minimum rating check
   - `predict_returns()` - ML return prediction
   - `rank_funds()` - Composite scoring (25/35/20/10/10 weights)
   - `get_recommendations()` - Main entry point (returns top-K with explanations)
   - **SHAPExplainer** - Feature contribution analysis

---

### `api/` - FastAPI Backend
```
api/
├── __init__.py
└── main.py                      [FastAPI application - 500+ lines]
```

**API Endpoints:**
1. `GET /health` - Server status check
2. `POST /recommend_funds` - Top-5 personalized recommendations
3. `POST /predict_returns` - Return forecasting with confidence
4. `POST /forecast_nav` - NAV projections for 12+ months
5. `GET /funds/{scheme_id}` - Detailed fund information
6. `POST /compare_funds` - Multi-fund comparison

**Features:**
- Pydantic input validation
- CORS middleware enabled
- Global recommendation engine initialization
- Structured response models
- Comprehensive error handling
- 20+ status codes and error messages

---

### `app/` - Streamlit Frontend
```
app/
├── __init__.py
└── dashboard.py                 [Streamlit UI - 600+ lines]
```

**Dashboard Tabs:**

1. **Get Recommendations**
   - Investment amount slider
   - SIP/Lumpsum toggle
   - Tenure selector (6-120 months)
   - Category dropdown
   - Risk tolerance (1-6)
   - Generate button → Top-5 with explanations

2. **Fund Analytics**
   - Total fund statistics
   - Category distribution (pie chart)
   - Rating by category (bar chart)
   - Risk vs Return scatter
   - Historical returns comparison

3. **Fund Details**
   - Fund search (by name/ID/AMC)
   - Performance metrics table
   - Investment info table
   - Complete fund information

4. **Comparison**
   - Multi-select up to 5 funds
   - Comparison table
   - Returns trends (grouped bar)
   - Multi-dimensional radar chart

**UI Features:**
- Responsive layout
- Plotly interactive charts
- Custom CSS styling
- Session state management
- Error handling
- API integration

---

### `configs/` - Configuration
```
configs/
├── __init__.py
└── config.py                    [Settings & constants - 100+ lines]
```

**Configuration Items:**
- Project paths (DATA, MODELS)
- Model parameters (XGBoost, Prophet)
- API settings (HOST, PORT)
- Feature columns (15 numerical + 3 categorical)
- Recommendation settings (TOP_K, MIN_RATING)
- Risk tolerance mappings
- Logging configuration

---

### `utils/` - Utility Functions
```
utils/
├── __init__.py
└── helpers.py                   [Helper classes - 350+ lines]
```

**Key Classes:**

1. **DataLoader**
   - `load_dataset()` - JSON to DataFrame
   - `get_fund_by_id()` - Scheme lookup
   - `get_funds_by_category()` - Category filtering

2. **ModelLoader**
   - `load_model()` - Load pickle with caching
   - `save_model()` - Save pickle files
   - Model cache dictionary for performance

3. **FeatureEngineer**
   - `extract_features()` - Numerical feature extraction
   - `encode_categorical()` - One-hot encoding
   - `combine_features()` - Merge feature sets
   - `scale_features()` - Standardization

4. **MetricsCalculator**
   - `calculate_return_trend()` - Trend analysis
   - `calculate_volatility_adjusted_return()` - Risk-return ratio
   - `calculate_risk_score()` - Composite risk metric
   - `calculate_overall_score()` - Fund ranking score

5. **ExplainabilityHelper**
   - `generate_fund_explanation()` - Reasoning for recommendation
   - Strengths/weaknesses extraction
   - Investment rationale generation

6. **Logging**
   - `setup_logging()` - Configure logger with console + file

---

### `notebooks/` - Jupyter Notebooks
```
notebooks/
└── [Empty - Ready for exploration]
```

---

## 📊 Data Flow

```
┌─────────────────────────────────────────────────────────┐
│ 1. DATASET GENERATION                                   │
│    data/generate_dataset.py → data/raw/MF_India_AI.json│
│    Creates 150 realistic mutual funds with metrics      │
└───────────────┬─────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────┐
│ 2. DATA PREPROCESSING                                   │
│    services/data_preprocessing.py                       │
│    - Clean & validate                                   │
│    - Extract features                                   │
│    - Encode categoricals                                │
│    - Scale features                                     │
│    Output: data/processed/ + models/scaler.pkl          │
└───────────────┬─────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────┐
│ 3. MODEL TRAINING                                       │
│    services/model_trainer.py                            │
│    - XGBoost (return prediction)                        │
│    - Prophet (NAV forecasting)                          │
│    Output: models/xgboost.pkl, models/prophet.pkl       │
└───────────────┬─────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────┐
│ 4. API SERVER (FastAPI)                                 │
│    api/main.py                                          │
│    - Load models                                        │
│    - Serve 6 endpoints                                  │
│    Port: 8000                                           │
└───────────────┬─────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────┐
│ 5. DASHBOARD (Streamlit)                                │
│    app/dashboard.py                                     │
│    - 4 interactive tabs                                 │
│    - Calls API endpoints                                │
│    - Displays results                                   │
│    Port: 8501                                           │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 File Dependencies

```
main.py
├── configs/config.py
├── services/data_preprocessing.py
│   ├── configs/config.py
│   ├── utils/helpers.py
│   └── sklearn
├── services/model_trainer.py
│   ├── configs/config.py
│   ├── utils/helpers.py
│   ├── xgboost
│   └── prophet
├── api/main.py
│   ├── configs/config.py
│   ├── services/recommendation_engine.py
│   │   ├── configs/config.py
│   │   └── utils/helpers.py
│   └── fastapi
└── app/dashboard.py
    ├── utils/helpers.py
    ├── streamlit
    ├── plotly
    └── requests

data/generate_dataset.py
└── (standalone - generates JSON)

utils/helpers.py
└── sklearn, logging, pickle, pandas

services/recommendation_engine.py
├── configs/config.py
└── utils/helpers.py
```

---

## 📈 Code Statistics

| Component | Files | Lines | Functions | Classes |
|-----------|-------|-------|-----------|---------|
| Services | 3 | ~1100 | 35+ | 8 |
| API | 1 | ~500 | 6 | 10+ |
| Dashboard | 1 | ~600 | 50+ | - |
| Utils | 1 | ~350 | 25+ | 6 |
| Config | 1 | ~100 | 0 | 0 |
| Data Gen | 1 | ~100 | 1 | 0 |
| **Total** | **~10** | **~2750** | **100+** | **25+** |

---

## 🔑 Key Files to Understand

### 1. **Start Here**
- `README.md` - Overview and features
- `STARTUP_GUIDE.md` - Installation steps

### 2. **Configuration**
- `configs/config.py` - All settings
- `.env.example` - Environment variables

### 3. **Data Pipeline**
- `data/generate_dataset.py` - Data generation
- `services/data_preprocessing.py` - Feature engineering

### 4. **ML Models**
- `services/model_trainer.py` - Model training
- `services/recommendation_engine.py` - Prediction & recommendations

### 5. **Backend API**
- `api/main.py` - FastAPI endpoints

### 6. **Frontend**
- `app/dashboard.py` - Streamlit UI

### 7. **API Reference**
- `API_REFERENCE.md` - Endpoint documentation

---

## 📦 Package Dependencies

### Core ML Packages
- `scikit-learn` - Feature scaling, encoding
- `xgboost` - Return prediction
- `prophet` - Time-series forecasting
- `shap` - Model explainability (imported but not heavily used)

### Web Framework
- `fastapi` - API framework
- `uvicorn` - ASGI server
- `streamlit` - Dashboard framework

### Data Processing
- `pandas` - Data manipulation
- `numpy` - Numerical computing

### Visualization
- `plotly` - Interactive charts
- `matplotlib` - Static plots

### Utilities
- `python-dotenv` - Environment config
- `requests` - HTTP client
- `pydantic` - Data validation

---

## 🎯 Project Milestones

✅ **Phase 1: Foundation** - Folder structure, config, utilities  
✅ **Phase 2: Data Pipeline** - Dataset generation, preprocessing  
✅ **Phase 3: ML Models** - XGBoost, Prophet training  
✅ **Phase 4: Backend API** - FastAPI with 6 endpoints  
✅ **Phase 5: Frontend** - Streamlit dashboard with 4 tabs  
✅ **Phase 6: Documentation** - README, API ref, startup guide  

---

## 🚀 Ready to Deploy!

All files are production-ready with:
- ✅ Comprehensive error handling
- ✅ Type hints throughout
- ✅ Detailed docstrings
- ✅ Configuration management
- ✅ Logging setup
- ✅ API documentation
- ✅ User guide

---

**Total Project Size:** ~15 MB (including dependencies)  
**Python Files:** ~2,750 lines of code  
**Documentation:** ~60 KB  
**Time to Setup:** 5-10 minutes  
**Time to Demo:** < 1 minute after setup  

---

*Generated: December 18, 2025*  
*Version: 1.0.0 - Production Ready*
