# AI/ML Setup Guide for Ubuntu 22.04 LTS

This guide provides step-by-step instructions to set up the development environment for the Mutual Fund Wealth Management System on Ubuntu 22.04.

## Prerequisites

Ensure you have the following installed:
- **Ubuntu 22.04 LTS**
- **Git**
- **Python 3.10+** (Ubuntu 22.04 comes with Python 3.10 by default)

## Step 1: System Update

Open your terminal and update your package lists:

```bash
sudo apt update && sudo apt upgrade -y
```

## Step 2: Install Python and pip

Video ensuring Python and pip are installed:

```bash
sudo apt install python3 python3-pip python3-venv -y
```

Verify the installation:

```bash
python3 --version
pip3 --version
```

## Step 3: Clone the Repository

If you haven't already, clone the project repository:

```bash
git clone https://github.com/YourUsername/Mutual-Fund-Wealth-Management-System.git
cd Mutual-Fund-Wealth-Management-System
```

## Step 4: Create a Virtual Environment

It's best practice to use a virtual environment to manage dependencies.

```bash
# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

*Note: You should see `(venv)` appear at the start of your terminal prompt.*

## Step 5: Install Dependencies

Install the required Python libraries. If `requirements.txt` exists:

```bash
pip install -r requirements.txt
```

If you are starting fresh, install the core data science libraries:

```bash
pip install pandas numpy scikit-learn matplotlib seaborn jupyter notebook
# If you plan to use Deep Learning
pip install tensorflow torch
```

## Step 6: Data Setup

1.  **Raw Data**: Place your downloaded CSV files in `data/raw/csv/`.
2.  **Dataset**: Ensure `PS/dataset/Clean_MF_India_AI.csv` is present if you are using the provided dataset.

## Step 7: Running the Pipeline

### Data Cleaning
Run the script to convert and clean data:

```bash
python3 scripts/csv_to_json.py
python3 scripts/clean_json_for_ml.py
```

### Feature Engineering
Generate features for training:

```bash
python3 scripts/feature_engineering.py
```

### Model Training
Train the initial models:

```bash
python3 scripts/train_pipeline.py
```

## Troubleshooting

-   **Permission Issues**: If you get permission errors with pip, **do not** use sudo. Ensure you are in the virtual environment.
-   **Missing Packages**: If a script fails due to a missing module, install it using `pip install <module_name>`.

## Next Steps

Once the environment is set up, you can start exploring the `notebooks/` directory or developing new models in the `scripts/` folder.
