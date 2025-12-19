"""
Data preprocessing and feature engineering pipeline
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from typing import Tuple
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from configs.config import (
    DATASET_PATH, DATA_PROCESSED_PATH, FEATURE_COLUMNS,
    CATEGORICAL_COLUMNS, SCALER_PATH, ENCODER_PATH
)
from utils.helpers import DataLoader, FeatureEngineer, ModelLoader, setup_logging

logger = setup_logging()

class DataPreprocessor:
    """Complete data preprocessing pipeline"""

    def __init__(self):
        self.data_loader = DataLoader()
        self.feature_engineer = FeatureEngineer()
        self.df = None
        self.X_numerical = None
        self.X_categorical = None
        self.X_combined = None
        self.X_scaled = None
        self.y_targets = {}
        self.scaler = None
        self.encoder = None

    def load_data(self):
        """Load raw dataset"""
        logger.info("Loading dataset...")
        self.df = self.data_loader.load_dataset(str(DATASET_PATH))
        return self.df

    def clean_data(self):
        """Clean and validate data"""
        logger.info("Cleaning dataset...")

        # Remove duplicates
        initial_size = len(self.df)
        self.df = self.df.drop_duplicates(subset=['scheme_id'])
        logger.info(f"Removed {initial_size - len(self.df)} duplicates")

        # Handle missing values for numerical columns
        numerical_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numerical_cols:
            if self.df[col].isnull().any():
                self.df[col].fillna(self.df[col].mean(), inplace=True)

        # Handle missing values for categorical columns
        categorical_cols = self.df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if self.df[col].isnull().any():
                self.df[col].fillna(self.df[col].mode()[0] if len(self.df[col].mode()) > 0 else 'Unknown', inplace=True)

        logger.info(f"✓ Data cleaning complete. {len(self.df)} records remaining")
        return self.df

    def extract_features(self):
        """Extract numerical features"""
        logger.info("Extracting numerical features...")

        # Ensure all feature columns exist
        missing_cols = [col for col in FEATURE_COLUMNS if col not in self.df.columns]
        if missing_cols:
            logger.warning(f"Missing columns: {missing_cols}")

        available_cols = [col for col in FEATURE_COLUMNS if col in self.df.columns]
        self.X_numerical = self.df[available_cols].copy()

        logger.info(f"✓ Extracted {self.X_numerical.shape[1]} numerical features")
        return self.X_numerical

    def encode_categorical(self, fit=True):
        """Encode categorical features"""
        logger.info("Encoding categorical features...")

        available_cat_cols = [col for col in CATEGORICAL_COLUMNS if col in self.df.columns]

        if fit:
            self.encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
            X_encoded = self.encoder.fit_transform(self.df[available_cat_cols])
            logger.info(f"✓ Fitted encoder with {self.encoder.get_feature_names_out().shape[0]} categorical features")
        else:
            X_encoded = self.encoder.transform(self.df[available_cat_cols])

        self.X_categorical = pd.DataFrame(
            X_encoded,
            columns=self.encoder.get_feature_names_out(available_cat_cols)
        )

        return self.X_categorical

    def combine_features(self):
        """Combine numerical and categorical features"""
        logger.info("Combining feature sets...")

        self.X_combined = pd.concat(
            [self.X_numerical.reset_index(drop=True),
             self.X_categorical.reset_index(drop=True)],
            axis=1
        )

        logger.info(f"✓ Combined feature matrix shape: {self.X_combined.shape}")
        return self.X_combined

    def scale_features(self, fit=True):
        """Scale features using StandardScaler"""
        logger.info("Scaling features...")

        if fit:
            self.scaler = StandardScaler()
            self.X_scaled = self.scaler.fit_transform(self.X_combined)
            logger.info("✓ Fitted and scaled features")
        else:
            self.X_scaled = self.scaler.transform(self.X_combined)

        return self.X_scaled

    def prepare_targets(self):
        """Prepare target variables for ML models"""
        logger.info("Preparing target variables...")

        # Return prediction targets
        self.y_targets['return_1yr'] = self.df['returns_1yr'].values
        self.y_targets['return_3yr'] = self.df['returns_3yr'].values
        self.y_targets['return_5yr'] = self.df['returns_5yr'].values

        # NAV forecasting target (use average return as proxy for NAV growth)
        self.y_targets['nav_growth'] = (self.df['returns_1yr'] + self.df['returns_3yr'] + self.df['returns_5yr']) / 3.0

        logger.info(f"✓ Prepared {len(self.y_targets)} target variables")
        return self.y_targets

    def save_processed_data(self):
        """Save processed data and artifacts"""
        logger.info("Saving processed data and artifacts...")

        Path(DATA_PROCESSED_PATH).mkdir(parents=True, exist_ok=True)

        # Save dataframe
        self.df.to_csv(DATA_PROCESSED_PATH / "processed_funds.csv", index=False)

        # Save feature matrices
        pd.DataFrame(self.X_scaled, columns=self.X_combined.columns).to_csv(
            DATA_PROCESSED_PATH / "features_scaled.csv", index=False
        )

        # Save targets
        pd.DataFrame(self.y_targets).to_csv(
            DATA_PROCESSED_PATH / "targets.csv", index=False
        )

        # Save sklearn artifacts
        Path(SCALER_PATH).parent.mkdir(parents=True, exist_ok=True)
        with open(SCALER_PATH, 'wb') as f:
            pickle.dump(self.scaler, f)

        with open(ENCODER_PATH, 'wb') as f:
            pickle.dump(self.encoder, f)

        logger.info(f"✓ Saved processed data to {DATA_PROCESSED_PATH}")
        logger.info(f"✓ Saved scaler to {SCALER_PATH}")
        logger.info(f"✓ Saved encoder to {ENCODER_PATH}")

    def run_pipeline(self) -> Tuple[pd.DataFrame, np.ndarray, dict, object, object]:
        """Run complete preprocessing pipeline"""
        logger.info("=" * 60)
        logger.info("Starting Data Preprocessing Pipeline")
        logger.info("=" * 60)

        self.load_data()
        self.clean_data()
        self.extract_features()
        self.encode_categorical(fit=True)
        self.combine_features()
        self.scale_features(fit=True)
        self.prepare_targets()
        self.save_processed_data()

        logger.info("=" * 60)
        logger.info("Data Preprocessing Pipeline Complete")
        logger.info("=" * 60)

        return self.df, self.X_scaled, self.y_targets, self.scaler, self.encoder

def main():
    """Run preprocessing pipeline"""
    preprocessor = DataPreprocessor()
    df, X_scaled, y_targets, scaler, encoder = preprocessor.run_pipeline()

    print("\n" + "=" * 60)
    print("PREPROCESSING SUMMARY")
    print("=" * 60)
    print(f"Total funds processed: {len(df)}")
    print(f"Feature matrix shape: {X_scaled.shape}")
    print(f"Target variables: {list(y_targets.keys())}")
    print(f"\nDataset columns: {df.columns.tolist()}")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
