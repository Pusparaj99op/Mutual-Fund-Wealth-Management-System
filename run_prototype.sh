#!/bin/bash

# Prototype Workflow Script for Mutual Fund Wealth Management System

# Set strict error handling
set -e

echo "========================================================"
echo "   Mutual Fund Wealth Management System - Prototype"
echo "========================================================"

# Step 1: Check/Install Dependencies
echo ""
echo "[1/3] Checking Dependencies..."
echo "Ideally, you should run this in a virtual environment."
echo "Installing dependencies from requirements-dev.txt..."
python3 -m pip install -r requirements-dev.txt --quiet
echo "Dependencies installed."

# Step 2: Check for Models / Train if missing
echo ""
echo "[2/3] Checking Models..."
MODEL_DIR="models"
RF_MODEL="$MODEL_DIR/rf_return_1yr.pkl"
KMEANS_MODEL="$MODEL_DIR/kmeans_risk.pkl"

if [[ -f "$RF_MODEL" && -f "$KMEANS_MODEL" ]]; then
    echo "Models found in $MODEL_DIR. Skipping training."
else
    echo "Models missing. Starting training pipeline..."
    echo "Running: python3 scripts/train_and_recommend.py --train"
    python3 scripts/train_and_recommend.py --train
    echo "Training complete."
fi

# Step 3: Run Recommendation
echo ""
echo "[3/3] Generating Recommendations..."
echo "Scenario: Equity Fund, Tenure 5 Years, Amount 100000"
echo "Running: python3 scripts/train_and_recommend.py --recommend --category Equity --tenure 5 --amount 100000"
echo "--------------------------------------------------------"
python3 scripts/train_and_recommend.py --recommend --category Equity --tenure 5 --amount 100000

echo "--------------------------------------------------------"
echo "Prototype run complete!"
