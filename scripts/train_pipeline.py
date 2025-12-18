"""
Complete AI Training Pipeline for Mutual Fund Recommendation.

Steps:
1. Feature Engineering (Load/Generate)
2. RandomForest Regression (Train Model)
3. KMeans Clustering (Risk Profiling)
4. Rule-Based Recommendation
5. Top 3 Fund Suggestions
"""

import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Ensure local scripts can be imported
sys.path.append(str(Path(__file__).parent.parent))
from scripts import feature_engineering

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('train_pipeline')

FEATURES_FILE = Path('data/features/all_nav_features.parquet')

def load_or_generate_features():
    """Step 1: Feature Engineering"""
    if not FEATURES_FILE.exists():
        logger.info("Features file not found. Running feature engineering...")
        feature_engineering.run_all()
    else:
        logger.info("Loading existing features from %s", FEATURES_FILE)

    return pd.read_parquet(FEATURES_FILE)

def train_return_prediction_model(df):
    """Step 2: RandomForest Regression to predict next-day return"""
    logger.info("Training RandomForest Regression model...")

    # Prepare data: Shift target (next day log return)
    # We will train specific models per scheme or one global model with scheme encoding?
    # For simplicity and robustness with limited data, let's train a global model
    # but strictly it should be time-series aware.
    # Here we stick to a simplified approach: Predict next day return using recent lags.

    df = df.sort_values(['scheme_code', 'date']).reset_index(drop=True)
    df['target'] = df.groupby('scheme_code')['logret_1d'].shift(-1)

    # Features
    feature_cols = [c for c in df.columns if 'roll_' in c or 'ann_' in c]
    # Also add some lags of logret
    for i in range(1, 4):
        col = f'lag_logret_{i}'
        df[col] = df.groupby('scheme_code')['logret_1d'].shift(i)
        feature_cols.append(col)

    df = df.dropna(subset=['target'] + feature_cols)

    X = df[feature_cols]
    y = df['target']

    # Train-Test Split (Time-based split ideally, but for final model we train on all)
    # For this pipeline, we train on all available data to get the "best" current predictor
    rf = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    rf.fit(X, y)

    logger.info("Model trained. Feature importances: %s",
                dict(zip(feature_cols[:5], rf.feature_importances_[:5])))

    # Predict on the LATEST available data point for each scheme to get "Expected Future Return"
    latest_data = df.groupby('scheme_code').tail(1).copy()
    latest_data['predicted_next_return'] = rf.predict(latest_data[feature_cols])

    # Annualize the predicted log return for easier interpretation (approx)
    latest_data['predicted_ann_return'] = latest_data['predicted_next_return'] * 252

    return latest_data[['scheme_code', 'date', 'predicted_ann_return']]

def cluster_risk_profiles(df_features, latest_preds):
    """Step 3: KMeans Clustering for Risk Profiling"""
    logger.info("Clustering funds into Risk Profiles...")

    # meaningful risk metrics: annualized volatility, max drawdown
    # We take the average of these metrics for each scheme over recent history (or just latest rolling)
    # Let's take the mean of rolling metrics to characterize the fund's general behavior

    risk_cols = ['ann_vol_252', 'max_dd_252']
    # Filter for valid data
    risk_df = df_features.groupby('scheme_code')[risk_cols].mean().dropna()

    # Normalize features
    scaler = StandardScaler()
    X_risk = scaler.fit_transform(risk_df)

    # KMeans - adjust clusters for small datasets
    n_samples = len(risk_df)
    n_clusters = min(3, n_samples)

    if n_samples < 1:
        logger.warning("No data for clustering.")
        latest_preds['risk_profile'] = 'Unknown'
        return latest_preds

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    risk_df['cluster'] = kmeans.fit_predict(X_risk)

    # Interpret clusters: Calculate mean vol/dd per cluster to label them Low/Med/High
    cluster_stats = risk_df.groupby('cluster').mean()
    # Sort clusters by volatility (or DD)
    sorted_clusters = cluster_stats.sort_values('ann_vol_252').index

    # Dynamic mapping based on number of clusters
    if n_clusters == 3:
        risk_map = {
            sorted_clusters[0]: 'Low Risk',
            sorted_clusters[1]: 'Medium Risk',
            sorted_clusters[2]: 'High Risk'
        }
    elif n_clusters == 2:
        risk_map = {
            sorted_clusters[0]: 'Low Risk',
            sorted_clusters[1]: 'High Risk'
        }
    else:
        risk_map = {sorted_clusters[0]: 'Medium Risk'}

    risk_df['risk_profile'] = risk_df['cluster'].map(risk_map)

    # Merge back to preds
    result = latest_preds.merge(risk_df[['risk_profile', 'ann_vol_252', 'max_dd_252']], on='scheme_code')
    return result

def rule_based_recommendation(scored_df, target_risk='High Risk'):
    """Step 4 & 5: Rule-Based Recommendation & Top 3"""
    logger.info("Applying Rule-Based Recommendations (Target: %s)...", target_risk)

    # Rule 1: Filter by Risk Profile
    # If we don't have enough in target risk, fallback? For now, strict filter.
    candidates = scored_df[scored_df['risk_profile'] == target_risk].copy()

    if candidates.empty:
        logger.warning("No candidates found for risk profile: %s", target_risk)
        return candidates

    # Rule 2: Sort by Predicted Return (Descending)
    candidates = candidates.sort_values('predicted_ann_return', ascending=False)

    return candidates.head(3)

def run_pipeline():
    # 1. Feature Engineering
    df_all = load_or_generate_features()
    if df_all.empty:
        logger.error("No data available.")
        return

    # 2. RandomForest Regression (Returns)
    latest_preds = train_return_prediction_model(df_all)

    # 3. KMeans Risk Profiling
    # usage of df_all to get historical risk averages
    scored_funds = cluster_risk_profiles(df_all, latest_preds)

    # 4 & 5. Recommendations
    # Let's generate recommendations for all profiles just to show output
    print("\n" + "="*50)
    print("AI MODEL TRAINING & RECOMMENDATION REPORT")
    print("="*50 + "\n")

    for profile in ['Low Risk', 'Medium Risk', 'High Risk']:
        top_3 = rule_based_recommendation(scored_funds, target_risk=profile)
        print(f"--- Top 3 suggestions for {profile} ---")
        if top_3.empty:
            print("  No funds found.")
        else:
            for _, row in top_3.iterrows():
                print(f"  Scheme {row['scheme_code']}: "
                      f"Pred Ret: {row['predicted_ann_return']:.2%}, "
                      f"Vol: {row['ann_vol_252']:.2%}, "
                      f"MaxDD: {row['max_dd_252']:.2%}")
        print("")

if __name__ == "__main__":
    run_pipeline()
