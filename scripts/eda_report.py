"""Run quick EDA and write data-quality report and plots."""
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

ROOT = Path('.')
DATA_DIR = Path('PS/dataset')
OUT_DIR = Path('reports')
OUT_DIR.mkdir(parents=True, exist_ok=True)


def run_eda():
    master = pd.read_csv(DATA_DIR / 'MF_India_AI.csv')
    report_lines = []

    report_lines.append(f'Total schemes: {len(master):,}')
    report_lines.append('\nMissing values (top 20):')
    report_lines.append(str(master.isnull().sum().sort_values(ascending=False).head(20)))

    # numeric conversions
    num_cols = ['min_sip','min_lumpsum','expense_ratio','fund_size_cr','fund_age_yr','sortino','alpha','sd','beta','sharpe','rating','returns_1yr','returns_3yr','returns_5yr']
    for c in num_cols:
        if c in master.columns:
            master[c] = pd.to_numeric(master[c], errors='coerce')

    # summary stats
    report_lines.append('\nSummary statistics (numeric):')
    report_lines.append(str(master.describe().T))

    with open(OUT_DIR / 'data_quality_report_eda.txt', 'w') as f:
        f.write('\n'.join(report_lines))

    # plots: returns histograms
    plt.figure(figsize=(10,4))
    cols = ['returns_1yr','returns_3yr','returns_5yr']
    for i,c in enumerate(cols,1):
        plt.subplot(1,3,i)
        if c in master.columns:
            master[c].dropna().hist(bins=40)
        plt.title(c)
    plt.tight_layout()
    plt.savefig(OUT_DIR / 'returns_histograms.png')

    # top AMCs
    top_amc = master['amc_name'].value_counts().head(20)
    plt.figure(figsize=(8,6))
    top_amc.plot(kind='barh')
    plt.title('Top 20 AMCs by count')
    plt.savefig(OUT_DIR / 'top_amcs.png')

    print('EDA report written to', OUT_DIR)


if __name__ == '__main__':
    run_eda()
