# 🏗️ System Architecture & Data Flow

## Federal Wealth Management System - Technical Architecture

---

## 📐 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FEDERAL WEALTH MANAGEMENT SYSTEM              │
│                     (AI-Powered Fund Recommendations)            │
└─────────────────────────────────────────────────────────────────┘

                           ┌─────────────┐
                           │   User      │
                           │  Browser    │
                           └──────┬──────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
            ┌───────▼────────┐        ┌────────▼──────────┐
            │                │        │                   │
        ┌───▼──────┐    ┌────▼───┐   │   ┌──────────┐    │
        │ Streamlit │    │ cURL / │   │   │ Swagger  │    │
        │ Dashboard │    │Python/ │   │   │ UI (/docs)
        │(localhost:│    │JS      │   │   │          │    │
        │   8501)   │    │Clients │   │   └──────────┘    │
        └────┬──────┘    └────┬───┘   │                   │
             │                │       └───────┬───────────┘
             └────────────────┼───────────────┘
                              │
                    ┌─────────▼──────────┐
                    │   FastAPI Backend  │
                    │  (localhost:8000)  │
                    │                    │
                    │  6 Endpoints:      │
                    │  - /health         │
                    │  - /recommend_*    │
                    │  - /predict_*      │
                    │  - /forecast_*     │
                    │  - /funds/*        │
                    │  - /compare_*      │
                    └─────────┬──────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼──────┐      ┌──────▼────┐       ┌───────▼──────┐
   │  Models   │      │    Data   │       │   Services   │
   │           │      │           │       │              │
   │ - XGBoost │      │ - Dataset │       │ - Recommend  │
   │   (pkl)   │      │ - Features│       │ - Predict    │
   │ - Prophet │      │ - Scaler  │       │ - Explain    │
   │   (pkl)   │      │ - Encoder │       │              │
   └───────────┘      └───────────┘       └──────────────┘
```

---

## 🔄 Data Flow Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│ PHASE 1: DATA GENERATION                                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   generate_dataset.py                                           │
│   ├─ Generate 150 synthetic mutual funds                        │
│   ├─ Add realistic metrics (returns, risk, rating)             │
│   ├─ Distribute across 15+ AMCs                                │
│   ├─ Multiple categories/subcategories                         │
│   └─ Output: MF_India_AI.json                                  │
│                                                                  │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                    (150 funds)
                         │
┌────────────────────────▼─────────────────────────────────────────┐
│ PHASE 2: DATA PREPROCESSING                                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   data_preprocessing.py (DataPreprocessor class)               │
│   │                                                             │
│   ├─ Load JSON dataset                                         │
│   │  └─ 150 funds × ~20 columns                               │
│   │                                                             │
│   ├─ Clean data                                                │
│   │  ├─ Remove duplicates                                      │
│   │  ├─ Handle missing values                                  │
│   │  └─ Validate metrics                                       │
│   │                                                             │
│   ├─ Feature extraction (numerical)                            │
│   │  ├─ min_sip, min_lumpsum                                   │
│   │  ├─ expense_ratio, fund_size_cr                            │
│   │  ├─ risk_level, alpha, beta                                │
│   │  ├─ sharpe_ratio, sortino_ratio                            │
│   │  ├─ std_deviation, rating                                  │
│   │  └─ return_1yr, return_3yr, return_5yr (15 features)      │
│   │                                                             │
│   ├─ Categorical encoding (One-Hot)                            │
│   │  ├─ amc_name (15 categories)                               │
│   │  ├─ category (5 categories)                                │
│   │  └─ sub_category (10+ categories)                          │
│   │                                                             │
│   ├─ Feature combination                                       │
│   │  └─ 15 numerical + encoded categories = 30+ features      │
│   │                                                             │
│   ├─ Feature scaling (StandardScaler)                          │
│   │  ├─ Mean = 0, Std = 1                                      │
│   │  └─ Fitted on training data                                │
│   │                                                             │
│   ├─ Target preparation                                        │
│   │  ├─ return_1yr (for training)                              │
│   │  ├─ return_3yr (for training)                              │
│   │  ├─ return_5yr (main target)                               │
│   │  └─ nav_growth (for Prophet)                               │
│   │                                                             │
│   └─ Save artifacts                                            │
│      ├─ processed_funds.csv (cleaned data)                     │
│      ├─ features_scaled.csv (normalized features)              │
│      ├─ targets.csv (target variables)                         │
│      ├─ feature_scaler.pkl (sklearn scaler)                    │
│      └─ categorical_encoder.pkl (sklearn encoder)              │
│                                                                  │
│   Output: Processed data + sklearn artifacts                   │
│                                                                  │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                (150×30+ matrix)
                         │
┌────────────────────────▼─────────────────────────────────────────┐
│ PHASE 3: MODEL TRAINING                                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   model_trainer.py (MLModelTrainer class)                      │
│   │                                                             │
│   ├─ Load processed features & targets                         │
│   │  └─ X_train: (150, 30) features                            │
│   │  └─ y_train: (150,) targets                                │
│   │                                                             │
│   ├─ XGBoost Training                                          │
│   │  ├─ Model: XGBRegressor                                    │
│   │  ├─ Hyperparameters:                                       │
│   │  │  ├─ max_depth: 7                                        │
│   │  │  ├─ learning_rate: 0.1                                  │
│   │  │  ├─ n_estimators: 200                                   │
│   │  │  └─ subsample: 0.8                                      │
│   │  ├─ Target: 5-year returns                                 │
│   │  ├─ Task: Regression                                       │
│   │  └─ Output: xgboost_returns.pkl                            │
│   │                                                             │
│   ├─ Prophet Training                                          │
│   │  ├─ Model: Prophet (Facebook)                              │
│   │  ├─ Data: Time-series (fund age as time)                   │
│   │  ├─ Seasonality: Yearly enabled                            │
│   │  ├─ Confidence: 95% intervals                              │
│   │  ├─ Target: NAV growth trends                              │
│   │  └─ Output: prophet_nav_forecast.pkl                       │
│   │                                                             │
│   └─ Save models & scalers                                     │
│      ├─ xgboost_returns.pkl                                    │
│      ├─ prophet_nav_forecast.pkl                               │
│      ├─ feature_scaler.pkl                                     │
│      └─ categorical_encoder.pkl                                │
│                                                                  │
│   Output: Trained models ready for inference                   │
│                                                                  │
└────────────────────────┬─────────────────────────────────────────┘
                         │
            (4 pickle artifacts)
                         │
┌────────────────────────▼─────────────────────────────────────────┐
│ PHASE 4: API SERVER (FastAPI)                                    │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   api/main.py                                                   │
│   │                                                             │
│   ├─ Load dataset (MF_India_AI.json)                            │
│   │  └─ In-memory DataFrame (150 funds)                        │
│   │                                                             │
│   ├─ Load models (from pickle files)                           │
│   │  ├─ xgboost_returns                                        │
│   │  ├─ prophet_nav_forecast                                   │
│   │  ├─ feature_scaler                                         │
│   │  └─ categorical_encoder                                    │
│   │                                                             │
│   ├─ Endpoint 1: GET /health                                   │
│   │  └─ Return: {status, timestamp, version}                   │
│   │                                                             │
│   ├─ Endpoint 2: POST /recommend_funds                         │
│   │  ├─ Input: {investment_amount, type, tenure, category}     │
│   │  ├─ Logic:                                                 │
│   │  │  ├─ Filter by investment amount                         │
│   │  │  ├─ Filter by tenure/risk alignment                     │
│   │  │  ├─ Filter by category                                  │
│   │  │  ├─ Filter by minimum rating                            │
│   │  │  ├─ Predict returns (XGBoost)                           │
│   │  │  ├─ Calculate composite score                           │
│   │  │  ├─ Rank and select top-5                               │
│   │  │  ├─ Generate SHAP explanations                          │
│   │  │  └─ Format response                                     │
│   │  └─ Output: {recommendations[], filtering_stats}           │
│   │                                                             │
│   ├─ Endpoint 3: POST /predict_returns                         │
│   │  ├─ Input: {scheme_id, period_years}                       │
│   │  ├─ Logic:                                                 │
│   │  │  ├─ Look up fund in database                            │
│   │  │  ├─ Use historical data + trend                         │
│   │  │  ├─ Calculate confidence interval                       │
│   │  │  └─ Extract SHAP explanations                           │
│   │  └─ Output: {prediction, confidence, risk_metrics}         │
│   │                                                             │
│   ├─ Endpoint 4: POST /forecast_nav                            │
│   │  ├─ Input: {scheme_id, forecast_months}                    │
│   │  ├─ Logic:                                                 │
│   │  │  ├─ Get current NAV                                     │
│   │  │  ├─ Use Prophet model                                   │
│   │  │  ├─ Generate monthly projections                        │
│   │  │  └─ Add confidence bounds                               │
│   │  └─ Output: {forecast_data[], confidence_level}            │
│   │                                                             │
│   ├─ Endpoint 5: GET /funds/{scheme_id}                        │
│   │  ├─ Input: scheme_id                                       │
│   │  └─ Output: {all_fund_details}                             │
│   │                                                             │
│   ├─ Endpoint 6: POST /compare_funds                           │
│   │  ├─ Input: [scheme_ids]                                    │
│   │  └─ Output: {comparison_table}                             │
│   │                                                             │
│   └─ Running on: http://localhost:8000                         │
│                                                                  │
└────────────────────────┬─────────────────────────────────────────┘
                         │
            (HTTP JSON API)
                         │
┌────────────────────────▼─────────────────────────────────────────┐
│ PHASE 5: STREAMLIT DASHBOARD                                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   app/dashboard.py                                              │
│   │                                                             │
│   ├─ Tab 1: Get Recommendations                               │
│   │  ├─ Form inputs:                                           │
│   │  │  ├─ Investment amount slider                            │
│   │  │  ├─ SIP/Lumpsum toggle                                  │
│   │  │  ├─ Tenure selector (6-120m)                            │
│   │  │  ├─ Category dropdown                                   │
│   │  │  └─ Risk tolerance (1-6)                                │
│   │  └─ Display:                                               │
│   │     ├─ API call → /recommend_funds                         │
│   │     ├─ Show top-5 cards with scores                        │
│   │     ├─ Display explanations                                │
│   │     ├─ Show metrics (rating, sharpe, expense)              │
│   │     └─ Link to details                                     │
│   │                                                             │
│   ├─ Tab 2: Fund Analytics                                    │
│   │  ├─ Summary metrics                                        │
│   │  ├─ Category distribution (pie chart)                      │
│   │  ├─ Rating by category (bar chart)                         │
│   │  ├─ Risk vs Return (scatter plot)                          │
│   │  └─ Returns comparison (grouped bars)                      │
│   │                                                             │
│   ├─ Tab 3: Fund Details                                      │
│   │  ├─ Search inputs:                                         │
│   │  │  ├─ Scheme name dropdown                                │
│   │  │  ├─ Scheme ID selector                                  │
│   │  │  └─ AMC name filter                                     │
│   │  ├─ Display:                                               │
│   │  │  ├─ Fund metrics table                                  │
│   │  │  ├─ Risk indicators                                     │
│   │  │  ├─ Performance metrics                                 │
│   │  │  └─ Investment info                                     │
│   │  └─ API call → /funds/{id}                                 │
│   │                                                             │
│   ├─ Tab 4: Comparison                                        │
│   │  ├─ Multi-select (up to 5 funds)                          │
│   │  ├─ Display:                                               │
│   │  │  ├─ Comparison table                                    │
│   │  │  ├─ Returns trend chart                                 │
│   │  │  ├─ Risk metrics radar                                  │
│   │  │  └─ Side-by-side visualization                          │
│   │  └─ API call → /compare_funds                              │
│   │                                                             │
│   └─ Running on: http://localhost:8501                         │
│                                                                  │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                  (Web UI)
                         │
                    User Views
                    Results & Acts
```

---

## 🔀 Recommendation Algorithm Flow

```
User Input (Investment Profile)
        │
        ├─ investment_amount: ₹100,000
        ├─ investment_type: "sip"
        ├─ tenure_months: 60
        ├─ category: null
        └─ risk_tolerance: 4
        │
        ▼
┌───────────────────────────────────────┐
│   FILTERING LAYER                     │
│   (Reduce 150 → ~80 candidates)       │
├───────────────────────────────────────┤
│                                       │
│  1. Investment Amount Filter          │
│     └─ min_sip <= 100,000 ✓          │
│        Keep: funds with low min       │
│                                       │
│  2. Tenure/Risk Filter                │
│     └─ For 60 months → max risk ≤ 4  │
│        Keep: moderate risk funds      │
│                                       │
│  3. Category Filter                   │
│     └─ No restriction → all OK        │
│                                       │
│  4. Rating Filter                     │
│     └─ rating >= 3.0                  │
│        Keep: decent quality funds     │
│                                       │
└─────────────────┬─────────────────────┘
                  │
            (~80 candidates)
                  │
                  ▼
┌───────────────────────────────────────┐
│   ML PREDICTION LAYER                 │
│   (Score & Rank)                      │
├───────────────────────────────────────┤
│                                       │
│  For each candidate fund:             │
│  ├─ Features extraction:              │
│  │  └─ [expense_ratio, risk, alpha..] │
│  │                                    │
│  ├─ XGBoost prediction:               │
│  │  └─ Predicted return: +14.2%       │
│  │                                    │
│  ├─ Composite score calculation:      │
│  │  ├─ Return score: +14.2% → 28.5/100│
│  │  ├─ Rating score: 4.5/5 → 25.3/100 │
│  │  ├─ Sharpe score: 2.15 → 22.1/100  │
│  │  ├─ Expense score: 0.65% → 15.8/100│
│  │  └─ Risk score: level 4 → 18.2/100 │
│  │     TOTAL: 87.5/100                │
│  │                                    │
│  └─ Add explanation:                  │
│     ├─ Strengths: rating, returns...  │
│     ├─ Weaknesses: none               │
│     └─ Rationale text                 │
│                                       │
└─────────────────┬─────────────────────┘
                  │
        (80 candidates with scores)
                  │
                  ▼
┌───────────────────────────────────────┐
│   RANKING & SELECTION                 │
│   (Keep top-5)                        │
├───────────────────────────────────────┤
│                                       │
│  1. Sort by composite score (DESC)    │
│  2. Select top-5 funds                │
│  3. Return with full details          │
│                                       │
│  Recommendation #1: 87.5/100          │
│  Recommendation #2: 85.2/100          │
│  Recommendation #3: 82.8/100          │
│  Recommendation #4: 80.5/100          │
│  Recommendation #5: 78.9/100          │
│                                       │
└─────────────────┬─────────────────────┘
                  │
                  ▼
        RESPONSE: Top-5 with
        {name, explanation,
         metrics, score, rating}
```

---

## 📊 Data Structures

### Input Request
```json
{
  "investment_amount": 100000,
  "investment_type": "sip",
  "tenure_months": 60,
  "category": null,
  "risk_tolerance": 4
}
```

### Recommendation Response
```json
{
  "timestamp": "2024-12-15T10:30:45.123456",
  "investor_profile": {...},
  "recommendations": [
    {
      "scheme_id": "FUND_0045",
      "scheme_name": "HDFC AMC Large Cap Fund 45",
      "amc_name": "HDFC AMC",
      "category": "Equity",
      "rating": 4.7,
      "risk_level": 4,
      "recommendation_score": 87.5,
      "predicted_return_5yr": 14.25,
      "sharpe_ratio": 2.15,
      "expense_ratio": 0.65,
      "min_sip": 500,
      "min_lumpsum": 5000,
      "explanation": {
        "strengths": [...],
        "weaknesses": [...],
        "investment_rationale": "..."
      }
    }
  ],
  "filtering_stats": {...}
}
```

---

## 🔗 Component Interactions

```
Dashboard (Streamlit)
    │
    ├─ User fills form
    ├─ Click button
    └─ Call API
        │
        ▼
FastAPI Backend
    │
    ├─ Validate input (Pydantic)
    ├─ Load recommendation engine
    ├─ Apply filters
    ├─ Predict returns (XGBoost)
    ├─ Calculate scores
    ├─ Generate explanations (SHAP)
    ├─ Format JSON response
    └─ Return to dashboard
        │
        ▼
Dashboard
    │
    ├─ Receive JSON
    ├─ Parse data
    ├─ Display cards
    ├─ Show charts
    └─ User reads & acts
```

---

## 🚀 Deployment Architecture

```
Developer Machine
├─ Python 3.10
├─ Virtual Env
├─ Dependencies
├─ Data files
├─ Models
├─ Backend (Port 8000)
└─ Dashboard (Port 8501)
     │
     ├─ Test locally
     └─ Works! ✅
     
Production Server
├─ Docker container
├─ Python runtime
├─ All dependencies
├─ Models & data
├─ FastAPI + Uvicorn
└─ Nginx reverse proxy
     │
     ├─ HTTPS enabled
     ├─ Rate limiting
     ├─ Authentication
     └─ Monitoring
```

---

This architecture ensures:
✅ **Scalability** - Stateless backend
✅ **Maintainability** - Clear separation of concerns
✅ **Performance** - Caching and efficient algorithms
✅ **Reliability** - Error handling throughout
✅ **Extensibility** - Easy to add new features
