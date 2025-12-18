"""
Main entry point for Federal Wealth Management System
Orchestrates data pipeline, model training, and service startup
"""

import sys
import os
from pathlib import Path
import argparse
import subprocess
import time

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.helpers import setup_logging

logger = setup_logging()

def run_data_generation():
    """Generate synthetic mutual fund dataset"""
    logger.info("=" * 60)
    logger.info("STEP 1: Generating Synthetic Mutual Fund Dataset")
    logger.info("=" * 60)
    
    from data.generate_dataset import generate_mutual_fund_dataset
    from configs.config import DATASET_PATH
    
    try:
        generate_mutual_fund_dataset(num_funds=150, output_path=str(DATASET_PATH))
        logger.info("✓ Dataset generation complete\n")
        return True
    except Exception as e:
        logger.error(f"✗ Dataset generation failed: {str(e)}\n")
        return False

def run_data_preprocessing():
    """Run data preprocessing pipeline"""
    logger.info("=" * 60)
    logger.info("STEP 2: Data Preprocessing & Feature Engineering")
    logger.info("=" * 60)
    
    from services.data_preprocessing import DataPreprocessor
    
    try:
        preprocessor = DataPreprocessor()
        df, X_scaled, y_targets, scaler, encoder = preprocessor.run_pipeline()
        logger.info("✓ Data preprocessing complete\n")
        return True
    except Exception as e:
        logger.error(f"✗ Data preprocessing failed: {str(e)}\n")
        return False

def run_model_training():
    """Train ML models"""
    logger.info("=" * 60)
    logger.info("STEP 3: Training ML Models (XGBoost + Prophet)")
    logger.info("=" * 60)
    
    from services.model_trainer import MLModelTrainer
    
    try:
        trainer = MLModelTrainer()
        trainer.train_pipeline()
        logger.info("✓ Model training complete\n")
        return True
    except Exception as e:
        logger.error(f"✗ Model training failed: {str(e)}\n")
        logger.warning("Continuing with recommendation engine initialization...\n")
        return True  # Non-critical, continue

def run_fastapi_backend():
    """Start FastAPI backend server"""
    logger.info("=" * 60)
    logger.info("STEP 4: Starting FastAPI Backend Server")
    logger.info("=" * 60)
    
    try:
        logger.info("Starting server on http://localhost:8000")
        logger.info("API Docs available at http://localhost:8000/docs")
        logger.info("Press Ctrl+C to stop the server\n")
        
        # Run FastAPI app using subprocess to ensure proper environment
        import subprocess
        subprocess.call([sys.executable, "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])
        
    except KeyboardInterrupt:
        logger.info("Backend server stopped")
        return False
    except Exception as e:
        logger.error(f"✗ Backend startup failed: {str(e)}\n")
        return False

def run_streamlit_dashboard():
    """Start Streamlit dashboard"""
    logger.info("=" * 60)
    logger.info("STEP 4: Starting Streamlit Dashboard")
    logger.info("=" * 60)
    
    try:
        logger.info("Starting Streamlit dashboard on http://localhost:8501")
        logger.info("Press Ctrl+C to stop the dashboard\n")
        
        # Run Streamlit app using subprocess to ensure proper environment
        import subprocess
        subprocess.call([sys.executable, "-m", "streamlit", "run", "app/dashboard.py"])
        
    except KeyboardInterrupt:
        logger.info("Dashboard stopped")
        return False
    except Exception as e:
        logger.error(f"✗ Dashboard startup failed: {str(e)}\n")
        return False

def initialize_all():
    """Initialize all components"""
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║ Federal Wealth Management System - Full Initialization  ║")
    logger.info("╚" + "=" * 58 + "╝")
    logger.info("")
    
    # Step 1: Data Generation
    if not run_data_generation():
        return False
    
    # Step 2: Data Preprocessing
    if not run_data_preprocessing():
        return False
    
    # Step 3: Model Training
    if not run_model_training():
        pass  # Non-critical
    
    logger.info("=" * 60)
    logger.info("✓ All initialization steps complete!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("📌 NEXT STEPS:")
    logger.info("   1. Start FastAPI Backend:")
    logger.info("      python main.py --backend")
    logger.info("")
    logger.info("   2. Start Streamlit Dashboard (in new terminal):")
    logger.info("      python main.py --dashboard")
    logger.info("")
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Federal Wealth Management System - Main Entry Point"
    )
    
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize all components (data, preprocessing, models)"
    )
    
    parser.add_argument(
        "--backend",
        action="store_true",
        help="Start FastAPI backend server only"
    )
    
    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="Start Streamlit dashboard only"
    )
    
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run complete initialization and start backend"
    )
    
    args = parser.parse_args()
    
    # Default behavior: full initialization
    if not any([args.init, args.backend, args.dashboard, args.full]):
        args.full = True
    
    # Full mode: init + backend
    if args.full:
        if initialize_all():
            logger.info("\nStarting FastAPI Backend Server...")
            time.sleep(2)
            run_fastapi_backend()
    
    # Init only
    elif args.init:
        initialize_all()
    
    # Backend only
    elif args.backend:
        logger.info("Starting FastAPI Backend (assuming initialization complete)...")
        run_fastapi_backend()
    
    # Dashboard only
    elif args.dashboard:
        logger.info("Starting Streamlit Dashboard (ensure backend is running)...")
        run_streamlit_dashboard()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n✓ Application terminated by user")
    except Exception as e:
        logger.error(f"\n✗ Fatal error: {str(e)}")
        sys.exit(1)
