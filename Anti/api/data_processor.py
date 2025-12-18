"""
Data Processor Module for FIMFP
Handles loading, preprocessing, and feature engineering for mutual fund data
"""

import pandas as pd
import numpy as np
import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

# Get the base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MutualFundDataProcessor:
    """
    Processes mutual fund data from CSV and historical data sources
    """

    def __init__(self):
        self.mf_data = None
        self.historical_data = {}
        self.data_path = os.path.join(BASE_DIR, 'PS', 'dataset', 'cleaned dataset', 'Cleaned_MF_India_AI.csv')
        self.raw_data_path = os.path.join(BASE_DIR, 'data', 'raw')

    def load_mutual_fund_data(self) -> pd.DataFrame:
        """Load the main mutual fund dataset"""
        try:
            self.mf_data = pd.read_csv(self.data_path)
            # Clean column names
            self.mf_data.columns = self.mf_data.columns.str.strip()
            # Add unique ID based on index
            self.mf_data['fund_id'] = range(1, len(self.mf_data) + 1)
            return self.mf_data
        except Exception as e:
            print(f"Error loading mutual fund data: {e}")
            return pd.DataFrame()

    def get_fund_by_id(self, fund_id: int) -> Optional[Dict]:
        """Get fund details by ID"""
        if self.mf_data is None:
            self.load_mutual_fund_data()

        fund = self.mf_data[self.mf_data['fund_id'] == fund_id]
        if fund.empty:
            return None
        return fund.iloc[0].to_dict()

    def search_funds(self, query: str = "", category: str = "",
                     risk_level: int = None, min_rating: int = None) -> List[Dict]:
        """Search and filter mutual funds"""
        if self.mf_data is None:
            self.load_mutual_fund_data()

        filtered_data = self.mf_data.copy()

        # Text search in scheme name and AMC
        if query:
            query_lower = query.lower()
            filtered_data = filtered_data[
                filtered_data['scheme_name'].str.lower().str.contains(query_lower, na=False) |
                filtered_data['amc_name'].str.lower().str.contains(query_lower, na=False)
            ]

        # Category filter
        if category:
            filtered_data = filtered_data[
                filtered_data['category'].str.lower() == category.lower()
            ]

        # Risk level filter
        if risk_level is not None:
            filtered_data = filtered_data[filtered_data['risk_level'] == risk_level]

        # Rating filter
        if min_rating is not None:
            filtered_data = filtered_data[filtered_data['rating'] >= min_rating]

        return filtered_data.to_dict('records')

    def get_all_funds(self, limit: int = 100, offset: int = 0) -> Tuple[List[Dict], int]:
        """Get all funds with pagination"""
        if self.mf_data is None:
            self.load_mutual_fund_data()

        total = len(self.mf_data)
        funds = self.mf_data.iloc[offset:offset+limit].to_dict('records')
        return funds, total

    def get_categories(self) -> List[str]:
        """Get list of unique categories"""
        if self.mf_data is None:
            self.load_mutual_fund_data()
        return self.mf_data['category'].unique().tolist()

    def get_sub_categories(self) -> List[str]:
        """Get list of unique sub-categories"""
        if self.mf_data is None:
            self.load_mutual_fund_data()
        return self.mf_data['sub_category'].unique().tolist()

    def get_amcs(self) -> List[str]:
        """Get list of unique AMCs"""
        if self.mf_data is None:
            self.load_mutual_fund_data()
        return self.mf_data['amc_name'].unique().tolist()

    def load_historical_data(self, fund_name: str) -> pd.DataFrame:
        """Load historical NAV data for a specific fund"""
        try:
            # Try to find matching CSV file in raw data folder
            csv_path = os.path.join(self.raw_data_path, 'csv')
            if os.path.exists(csv_path):
                # Search for matching file
                for file in os.listdir(csv_path):
                    if file.endswith('.csv'):
                        file_lower = file.lower()
                        fund_lower = fund_name.lower().replace(' ', '_')
                        if any(word in file_lower for word in fund_lower.split('_')[:3]):
                            hist_data = pd.read_csv(os.path.join(csv_path, file))
                            self.historical_data[fund_name] = hist_data
                            return hist_data

            # Return synthetic historical data if no match found
            return self._generate_synthetic_historical(fund_name)
        except Exception as e:
            print(f"Error loading historical data: {e}")
            return self._generate_synthetic_historical(fund_name)

    def _generate_synthetic_historical(self, fund_name: str) -> pd.DataFrame:
        """Generate synthetic historical data based on fund metrics"""
        if self.mf_data is None:
            self.load_mutual_fund_data()

        # Get fund details
        fund = self.mf_data[self.mf_data['scheme_name'] == fund_name]
        if fund.empty:
            # Default values
            returns_1yr = 10
            sd = 15
        else:
            returns_1yr = fund.iloc[0].get('returns_1yr', 10)
            sd = fund.iloc[0].get('sd', 15)

        # Generate 252 trading days (1 year) of synthetic data
        np.random.seed(42)  # For reproducibility
        n_days = 252

        # Calculate daily return parameters
        daily_return = (1 + returns_1yr/100) ** (1/252) - 1
        daily_vol = sd / 100 / np.sqrt(252)

        # Generate daily returns using geometric Brownian motion
        dt = 1/252
        returns = np.random.normal(daily_return, daily_vol, n_days)

        # Generate NAV series (starting from 100)
        nav = 100 * np.exp(np.cumsum(returns))

        # Generate date series
        end_date = datetime.now()
        dates = [(end_date - timedelta(days=i)).strftime('%Y-%m-%d')
                 for i in range(n_days-1, -1, -1)]

        return pd.DataFrame({
            'date': dates,
            'nav': nav,
            'returns': np.concatenate([[0], returns[1:] * 100])
        })

    def get_fund_statistics(self, fund_id: int) -> Dict:
        """Calculate comprehensive statistics for a fund"""
        fund = self.get_fund_by_id(fund_id)
        if fund is None:
            return {}

        return {
            'fund_id': fund_id,
            'scheme_name': fund.get('scheme_name', ''),
            'amc_name': fund.get('amc_name', ''),
            'category': fund.get('category', ''),
            'sub_category': fund.get('sub_category', ''),
            'returns': {
                '1yr': fund.get('returns_1yr', 0),
                '3yr': fund.get('returns_3yr', 0),
                '5yr': fund.get('returns_5yr', 0)
            },
            'risk_metrics': {
                'alpha': fund.get('alpha', 0),
                'beta': fund.get('beta', 0),
                'sharpe': fund.get('sharpe', 0),
                'sortino': fund.get('sortino', 0),
                'std_dev': fund.get('sd', 0),
                'risk_level': fund.get('risk_level', 0)
            },
            'fund_details': {
                'rating': fund.get('rating', 0),
                'expense_ratio': fund.get('expense_ratio', 0),
                'fund_size_cr': fund.get('fund_size_cr', 0),
                'fund_age_yr': fund.get('fund_age_yr', 0),
                'fund_manager': fund.get('fund_manager', ''),
                'min_sip': fund.get('min_sip', 0),
                'min_lumpsum': fund.get('min_lumpsum', 0)
            }
        }

    def get_top_funds_by_category(self, category: str, n: int = 10) -> List[Dict]:
        """Get top N funds in a category by Sharpe ratio"""
        if self.mf_data is None:
            self.load_mutual_fund_data()

        filtered = self.mf_data[self.mf_data['category'] == category]
        top_funds = filtered.nlargest(n, 'sharpe')
        return top_funds.to_dict('records')

    def get_fund_comparison(self, fund_ids: List[int]) -> List[Dict]:
        """Compare multiple funds"""
        if self.mf_data is None:
            self.load_mutual_fund_data()

        funds = self.mf_data[self.mf_data['fund_id'].isin(fund_ids)]
        return funds.to_dict('records')


# Singleton instance
data_processor = MutualFundDataProcessor()


def get_processor() -> MutualFundDataProcessor:
    """Get the data processor singleton"""
    return data_processor
