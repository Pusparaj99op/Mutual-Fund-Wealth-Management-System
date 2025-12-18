# Raptor — Prototype for AI/ML Mutual Fund Workflow

This folder contains a working prototype showing ingestion, preprocessing, forecasting and recommendation components for the Mutual Fund Wealth Management System. It includes:

- src/: Python modules for data loading, preprocessing, models, and financial methods (Monte Carlo, Black–Scholes, Black–Litterman)
- web/: A simple GSAP-based demo page that can call the API and visualize results
- tests/: Basic unit tests to validate core functionality

Quickstart:
1. Create a virtualenv and install dependencies: `pip install -r raptor/requirements.txt`.
2. Run tests: `pytest raptor/tests`.
3. Start the API: `uvicorn raptor.src.api:app --reload --port 8000` and open `raptor/web/index.html`.

Notes:
- Paths expect the repository layout to remain unchanged. The cleaned dataset is at `PS/dataset/cleaned dataset/Cleaned_MF_India_AI.csv` and NAV time series are under `data/raw/csv/`.
- This is a prototype scaffold — more sophisticated validation, training, and production hardening will be added in subsequent steps.
