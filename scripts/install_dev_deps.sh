#!/usr/bin/env bash
set -euo pipefail

echo "Installing development dependencies (statsmodels, xgboost, scikit-learn)..."
python3 -m pip install --user -r requirements-dev.txt

echo "Done. You may need to restart your Python session or VS Code to pick up new packages." 
