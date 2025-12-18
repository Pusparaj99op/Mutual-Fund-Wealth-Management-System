#!/usr/bin/env python3
"""Generate model comparison and forecast vs actual plots.

Saves outputs to reports/models/plots/.
"""
import os
import pandas as pd
import matplotlib
# Use Agg backend for headless environments (write files without a display)
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns


OUT_DIR = "reports/models/plots"


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def plot_forecast_metrics(baseline_metrics):
    ensure_dir(OUT_DIR)
    # Aggregate plot: mean RMSE per method
    agg = baseline_metrics.groupby('method')['RMSE'].mean().reset_index()
    plt.figure(figsize=(8, 5))
    sns.barplot(data=agg, x='method', y='RMSE', palette='muted')
    plt.title('Average RMSE across schemes (baseline forecasts)')
    plt.ylabel('RMSE')
    plt.xlabel('Method')
    plt.tight_layout()
    out = os.path.join(OUT_DIR, 'forecast_avg_rmse.png')
    plt.savefig(out)
    plt.close()

    # Per-scheme plots
    for code, grp in baseline_metrics.groupby('scheme_code'):
        plt.figure(figsize=(8, 5))
        sns.barplot(data=grp, x='method', y='RMSE', palette='pastel')
        plt.title(f'Forecast RMSE by method - scheme {code}')
        plt.ylabel('RMSE')
        plt.xlabel('Method')
        plt.tight_layout()
        out = os.path.join(OUT_DIR, f'forecast_rmse_{code}.png')
        plt.savefig(out)
        plt.close()


def plot_ml_metrics(ml_metrics):
    ensure_dir(OUT_DIR)
    agg = ml_metrics.groupby('model')['RMSE'].mean().reset_index()
    plt.figure(figsize=(6, 4))
    sns.barplot(data=agg, x='model', y='RMSE', palette='deep')
    plt.title('Average RMSE across schemes (ML models)')
    plt.ylabel('RMSE')
    plt.xlabel('Model')
    plt.tight_layout()
    out = os.path.join(OUT_DIR, 'ml_avg_rmse.png')
    plt.savefig(out)
    plt.close()

    for code, grp in ml_metrics.groupby('scheme_code'):
        plt.figure(figsize=(6, 4))
        sns.barplot(data=grp, x='model', y='RMSE', palette='cool')
        plt.title(f'ML RMSE by model - scheme {code}')
        plt.ylabel('RMSE')
        plt.xlabel('Model')
        plt.tight_layout()
        out = os.path.join(OUT_DIR, f'ml_rmse_{code}.png')
        plt.savefig(out)
        plt.close()


def plot_forecast_vs_actual(forecast_file, max_days=365):
    ensure_dir(OUT_DIR)
    df = pd.read_csv(forecast_file, parse_dates=['date'])
    if df.empty:
        return
    # pivot so each method is a column of preds, keep actual
    pivot = df.pivot_table(index='date', columns='method', values='pred')
    # actual is identical across methods; take the first
    actual = df.groupby('date')['actual'].first()

    # restrict to last `max_days` if possible
    pivot = pivot.sort_index()
    actual = actual.sort_index()
    if len(actual) > max_days:
        start = actual.index[-max_days]
        actual = actual.loc[start:]
        pivot = pivot.loc[start:]

    plt.figure(figsize=(12, 5))
    plt.plot(actual.index, actual.values, label='actual', color='black', linewidth=1.5)
    for col in pivot.columns:
        plt.plot(pivot.index, pivot[col].values, label=str(col), alpha=0.9)
    plt.title(f'Forecast vs Actual - {os.path.basename(forecast_file).replace("forecasts_", "").replace(".csv", "")}')
    plt.ylabel('NAV')
    plt.xlabel('Date')
    plt.legend()
    plt.tight_layout()
    out = os.path.join(OUT_DIR, f'forecast_vs_actual_{os.path.basename(forecast_file).replace(".csv", "")}.png')
    plt.savefig(out)
    plt.close()


def main():
    baseline_metrics_path = 'reports/models/baseline_forecast_metrics.csv'
    ml_metrics_path = 'reports/models/ml_baseline_metrics.csv'
    forecasts_dir = 'reports/models'

    if os.path.exists(baseline_metrics_path):
        baseline_metrics = pd.read_csv(baseline_metrics_path)
        plot_forecast_metrics(baseline_metrics)
    else:
        print('Missing baseline metrics:', baseline_metrics_path)

    if os.path.exists(ml_metrics_path):
        ml_metrics = pd.read_csv(ml_metrics_path)
        plot_ml_metrics(ml_metrics)
    else:
        print('Missing ML metrics:', ml_metrics_path)

    # Plot forecast vs actual for each forecasts_<code>.csv
    for fname in os.listdir(forecasts_dir):
        if fname.startswith('forecasts_') and fname.endswith('.csv'):
            plot_forecast_vs_actual(os.path.join(forecasts_dir, fname))


if __name__ == '__main__':
    main()
