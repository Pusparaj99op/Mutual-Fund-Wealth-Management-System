# Federal Wealth Management System
## Problem Statement Title:
AI-Based Mutual Fund Wealth Management System.

## Problem Statement Description:
Develop an AI/ML-powered system for middle-class investors using Indian mutual fund data to analyze historical trends, predict future performance, and recommend suitable funds based on AMC, category, investment amount, and tenure.

## Problem:
The problem domain concerns wealth management for the common middle class people, focusing on Mutual Funds. Now why this topic there are very limited technique or wealth management like FDs, Stocks Trading, Crypto, Estate Planning, Corporate Bonds etc. However, all of them require time, focus, significant capital, involve risk  factors, and offer limited interest rates. Mutual funds are investment vehicles that pool money from multiple investors to invest in a diversified portfolio of securities such as stocks, bonds, money market instruments, where they are managed by an asset management company (AMC).

## dataset: PS/dataset/MF_India_AI.json

## terms of dataset: Data Parameters for Mutual Funds India (MF_India_AI.json):
Scheme Name: Name of the mutual fund scheme
Min sip: Min sip amount required to start.
Min lumpsum: Min lumpsum amount required to start.
Expense ratio: calculated as a percentage of the Scheme's average Net Asset Value (NAV).
Fund size: the total amount of money that a mutual fund manager must oversee and invest.
Fund age: years since inception of scheme
Fund manager: A fund manager is responsible for implementing a fund's investment strategy and managing its trading activities.
Sortino : Sortino ratio measures the risk-adjusted return of an investment asset, portfolio, or strategy
Alpha: Alpha is the excess returns relative to market benchmark for a given amount of risk taken by the scheme
Standard deviation: A standard deviation is a number that can be used to show how much the returns of a mutual fund scheme are likely to deviate from its average annual returns.
Beta: Beta in a mutual fund is often used to convey the fund's volatility (gains or losses) in relation to its respective benchmark index
Sharpe: Sharpe Ratio of a mutual fund reveals its potential risk-adjusted returns
Risk level:
1- Low risk
2- Low to moderate
3- Moderate
4- Moderately High
5- High
6- Very High
AMC name: Mutual fund house managing the assets.
Rating: 0-5 rating assigned to scheme
Category: The category to which the mutual fund belongs (e.g. equity, debt, hybrid)
Sub-category : It includes category like Small cap, Large cap, ELSS, etc.
Return_1yr (%): The return percentage of the mutual fund scheme over 1 year.
Return_3yr (%): The return percentage of the mutual fund scheme over 3 year.
Return_5yr (%): The return percentage of the mutual fund scheme over 5year.

## Expected Outcomes:
We have live web scraped data of Mutual Funds India, our goal is to present descriptive analysis to understand this data and their patterns, then make predictions on the given data to forecast the future performance of specific mutual funds, develop a dashboard to display past data and projections Finally, create an AI-based recommendation system for selected inputs: AMC Name, Category, Amount Invested, Tenure.

## Topics: AI/ML ✅

### Understanding (Problem statement)
We aim to build an end-to-end AI/ML system to help middle-class investors with mutual fund selection and forecasting. The system will: (1) forecast scheme NAVs and returns, (2) recommend suitable schemes given investor constraints (AMC, category, amount, tenure), and (3) present explainable, auditable outputs for users.

### Data (what we have)
- Raw historical NAV CSVs are available under `data/raw/` (downloaded). These files contain per-scheme NAV timeseries that are the primary signal for forecasting.
- Supplementary metadata and engineered feature CSV/JSON files are in `data/` and `PS/dataset/` (e.g., `MF_India_AI.json`).
- Existing scripts that will help: `scripts/csv_to_json.py`, `scripts/clean_json_for_ml.py`, `scripts/feature_engineering.py`, `scripts/train_pipeline.py`, and evaluation utilities under `scripts/`.

### Preprocessing & Cleaning 🔧
- Parse and standardize dates, ensure consistent timezone/locale where needed.
- Sanity checks: remove duplicates, fix or drop malformed rows, and ensure monotonicity of dates per scheme.
- Missing values: impute or forward-fill NAVs carefully (or mark missing days explicitly and use models that support irregular time series).
- Outliers: detect using statistical rules (z-score, IQR) and time-series anomaly detectors — treat or clip where appropriate.
- Normalize and encode metadata (AMC, category, risk level) using label encoding or embedding tables for advanced models.

### Feature Engineering ✨
- Create rolling-window features (mean, std, median, skew) for multiple horizons (7d, 30d, 90d).
- Compute returns (daily, weekly, monthly) and log-returns where appropriate.
- Time features: day-of-week, month, quarter, time-since-inception, fund-age.
- Volatility and risk metrics (rolling volatility, drawdown, maximum consecutive losses).
- External covariates: macro indicators or market indices if available (can improve forecasting).

### Modeling Approaches (what we'll try) 🧠
- Baselines: naive (last value), simple moving averages, ETS/ARIMA.
- Classical ML: Random Forest, XGBoost, LightGBM on engineered features for short/medium horizon forecasts.
- Deep learning (time-series): LSTM/GRU, Temporal Convolutional Networks, Transformer-based models, Temporal Fusion Transformer for multivariate forecasting.
- Probabilistic/forecasting-specific: Prophet, DeepAR/DeepState for probabilistic forecasts.
- Recommendation layer: content-based ranking (AMC, category, risk), hybrid ranking with predicted returns and risk exposure, and re-ranking with business rules (minimum SIP, tenure compatibility).

### Training & Validation 🔁
- Use time-series-aware splitting (rolling-window / expanding window CV) to avoid leakage.
- Use walk-forward validation for hyperparameter search (Optuna) and early stopping for DL models.
- Optimize for business-relevant loss (e.g., MAE, RMSE, or custom loss that penalizes directional errors differently).

### Evaluation & Backtesting 📊
- Forecast metrics: MAE, RMSE, MAPE, and prediction intervals coverage for probabilistic models.
- Recommendation metrics: precision@k, recall@k, NDCG, and offline portfolio backtests (simulated returns, drawdowns) to measure economic impact.
- Model explainability: SHAP/feature importances for tree models and attention visualization for sequence models.

### Production & Deployment 🚀
- Package model artifacts with versioning (MLflow, DVC, or similar); store model metadata and training data hashes.
- Serve models via a lightweight API (FastAPI/Flask) with Docker containerization and simple autoscaling rules.
- Schedule inference and incremental retraining (cron / Airflow / Prefect) and keep retraining cadence aligned with data availability and concept drift.
- Monitoring: track request latency, prediction distributions, data drift, and performance regression; set alerts for drift threshold breaches.

### Reproducibility & Tooling 🔁
- Use `requirements-dev.txt` or pinned environment files to ensure reproducible environments.
- Experiment tracking with MLflow or Weights & Biases for hyperparameter search and model comparisons.
- Unit tests for data validation and model contracts; CI pipeline for tests and linting.

### Files & Next steps ✅
- Convert and clean `data/raw/csv/*.csv` using `scripts/csv_to_json.py` and `scripts/clean_json_for_ml.py`.
- Generate features with `scripts/feature_engineering.py` and store them under `data/features/`.
- Train baseline models using `scripts/train_pipeline.py`, add hyperparameter tuning, and produce evaluation reports under `reports/models/`.
- After validation, prepare a Docker image and FastAPI endpoint for serving forecasts and recommendations.

> **Note:** This README addition describes the full plan to get to a working AI/ML pipeline; if you want, I can also create templates for model training notebooks, CI configs, or a simple FastAPI serving scaffold.

## Details

### Team Workflow & Collaboration
To ensure efficiency during the hackathon, we will follow a structured workflow:
- **Version Control**: We will use Git for version control.
    - `main`: Production-ready code.
    - `dev`: Integration branch for testing.
    - `feature/<name>`: Individual branches for specific features or tasks.
- **Communication**: Regular sync-ups to track progress and blockers.
- **Task Management**: Using this README and the `task.md` artifact to track to-dos.

### Architecture Overview
The system consists of three main components:
1. **Data Pipeline**: Scripts to clean and engineer features from the mutual fund CSVs.
2. **AI/ML Core**: Models to predict NAV and recommend funds based on user inputs.
3. **Application Interface**: A web-based dashboard (likely using FastAPI for backend and a modern frontend) to interact with the models.

### Setup Guide
For step-by-step instructions on setting up the AI/ML environment on Ubuntu 22.04, please refer to [AI_ML_SETUP_GUIDE.md](AI_ML_SETUP_GUIDE.md).
