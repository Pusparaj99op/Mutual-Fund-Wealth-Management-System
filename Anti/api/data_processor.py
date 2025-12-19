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

# AMC to NSE Stock Symbol Mapping for TradingView widgets
AMC_STOCK_SYMBOLS = {
    'HDFC Mutual Fund': 'NSE:HDFCAMC',
    'ICICI Prudential Mutual Fund': 'NSE:ICICIPRULI',
    'SBI Mutual Fund': 'NSE:SBILIFE',
    'Aditya Birla Sun Life Mutual Fund': 'NSE:ABSLAMC',
    'Kotak Mahindra Mutual Fund': 'NSE:KOTAKBANK',
    'Axis Mutual Fund': 'NSE:AXISBANK',
    'Nippon India Mutual Fund': 'NSE:NAM-INDIA',
    'UTI Mutual Fund': 'NSE:UTIAMC',
    'DSP Mutual Fund': 'NSE:DSPBR',
    'Franklin Templeton Mutual Fund': 'NYSE:BEN',
    'Tata Mutual Fund': 'NSE:TATASTEEL',
    'L&T Mutual Fund': 'NSE:LT',
    'Mirae Asset Mutual Fund': 'NSE:MIRAEASSET',
    'Motilal Oswal Mutual Fund': 'NSE:MOTILALOFS',
    'Edelweiss Mutual Fund': 'NSE:EDELWEISS',
    'HSBC Mutual Fund': 'NYSE:HSBC',
    'Invesco Mutual Fund': 'NYSE:IVZ',
    'Canara Robeco Mutual Fund': 'NSE:CANBK',
    'LIC Mutual Fund': 'NSE:LICI',
    'Bank of India Mutual Fund': 'NSE:BANKINDIA',
    'IDBI Mutual Fund': 'NSE:IDBI',
    'Bandhan Mutual Fund': 'NSE:BANDHANBNK',
    'Mahindra Manulife Mutual Fund': 'NSE:M&M',
    'IIFL Mutual Fund': 'NSE:IIFL',
    'JM Financial Mutual Fund': 'NSE:JMFINANCIL',
}

class MutualFundDataProcessor:
    """
    Processes mutual fund data from CSV and historical data sources
    """

    def __init__(self):
        self.mf_data = None
        self.historical_data = {}
        self.scheme_code_mapping = {}  # Maps fund_id to scheme_code
        self.amc_stock_symbols = AMC_STOCK_SYMBOLS  # AMC to stock symbol mapping
        self.data_path = os.path.join(BASE_DIR, 'PS', 'dataset', 'cleaned dataset', 'Cleaned_MF_India_AI.csv')
        self.raw_data_path = os.path.join(BASE_DIR, 'data', 'raw')
        self.nav_json_path = os.path.join(BASE_DIR, 'data', 'raw', 'json')

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

        amc_name = fund.get('amc_name', '')
        amc_stock_symbol = self.amc_stock_symbols.get(amc_name, None)

        return {
            'fund_id': fund_id,
            'scheme_name': fund.get('scheme_name', ''),
            'amc_name': amc_name,
            'amc_stock_symbol': amc_stock_symbol,  # For TradingView widgets
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

    def build_scheme_code_mapping(self) -> Dict[int, int]:
        """Build a mapping from fund_id to scheme_code by matching scheme names"""
        if not os.path.exists(self.nav_json_path):
            return {}

        if self.mf_data is None:
            self.load_mutual_fund_data()

        if self.scheme_code_mapping:
            return self.scheme_code_mapping

        # Load all NAV JSON files and extract scheme names
        nav_files = {}
        for filename in os.listdir(self.nav_json_path):
            if filename.startswith('nav_') and filename.endswith('.json'):
                try:
                    scheme_code = int(filename.replace('nav_', '').replace('.json', ''))
                    filepath = os.path.join(self.nav_json_path, filename)
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        scheme_name = data.get('meta', {}).get('scheme_name', '')
                        if scheme_name:
                            nav_files[scheme_code] = scheme_name.lower().strip()
                except (ValueError, json.JSONDecodeError):
                    continue

        # Match scheme names from CSV to NAV files
        for _, row in self.mf_data.iterrows():
            fund_id = row['fund_id']
            scheme_name = row['scheme_name'].lower().strip()

            # Try exact match first
            for scheme_code, nav_name in nav_files.items():
                if scheme_name == nav_name or scheme_name in nav_name or nav_name in scheme_name:
                    self.scheme_code_mapping[fund_id] = scheme_code
                    break

            # Try fuzzy match on key words
            if fund_id not in self.scheme_code_mapping:
                scheme_words = set(scheme_name.replace('-', ' ').replace('–', ' ').split()[:4])
                for scheme_code, nav_name in nav_files.items():
                    nav_words = set(nav_name.replace('-', ' ').replace('–', ' ').split()[:4])
                    if len(scheme_words & nav_words) >= 3:
                        self.scheme_code_mapping[fund_id] = scheme_code
                        break

        return self.scheme_code_mapping

    def get_historical_nav(self, fund_id: int, period: str = '1Y') -> Dict:
        """
        Get historical NAV data for a fund from JSON files.

        Args:
            fund_id: The fund ID
            period: Time period - 1M, 3M, 6M, 1Y, 3Y, 5Y, MAX

        Returns:
            Dict with dates, values, and metadata
        """
        if self.mf_data is None:
            self.load_mutual_fund_data()

        fund = self.get_fund_by_id(fund_id)
        if fund is None:
            return {'error': 'Fund not found'}

        # Build mapping if not already done
        if not self.scheme_code_mapping:
            self.build_scheme_code_mapping()

        scheme_code = self.scheme_code_mapping.get(fund_id)

        if scheme_code:
            # Try to load actual historical data
            filepath = os.path.join(self.nav_json_path, f'nav_{scheme_code}.json')
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r') as f:
                        nav_data = json.load(f)

                    data_points = nav_data.get('data', [])
                    if data_points:
                        # Parse dates and NAV values
                        parsed_data = []
                        for point in data_points:
                            try:
                                date_str = point.get('date', '')
                                nav_val = float(point.get('nav', 0))
                                # Parse date (format: DD-MM-YYYY)
                                date_obj = datetime.strptime(date_str, '%d-%m-%Y')
                                parsed_data.append({'date': date_obj, 'nav': nav_val})
                            except (ValueError, TypeError):
                                continue

                        if parsed_data:
                            # Sort by date ascending
                            parsed_data.sort(key=lambda x: x['date'])

                            # Filter by period
                            period_days = {
                                '1M': 30, '3M': 90, '6M': 180,
                                '1Y': 365, '3Y': 1095, '5Y': 1825, 'MAX': 99999
                            }
                            days = period_days.get(period.upper(), 365)
                            cutoff_date = datetime.now() - timedelta(days=days)
                            filtered = [p for p in parsed_data if p['date'] >= cutoff_date]

                            if not filtered:
                                filtered = parsed_data[-min(len(parsed_data), 252):]  # Fallback to last 252 points

                            # Sample to max 250 points for performance
                            if len(filtered) > 250:
                                step = len(filtered) // 250
                                filtered = filtered[::step]

                            return {
                                'success': True,
                                'fund_id': fund_id,
                                'scheme_name': fund.get('scheme_name', ''),
                                'scheme_code': scheme_code,
                                'period': period,
                                'dates': [p['date'].strftime('%Y-%m-%d') for p in filtered],
                                'values': [round(p['nav'], 2) for p in filtered],
                                'start_nav': round(filtered[0]['nav'], 2) if filtered else 0,
                                'end_nav': round(filtered[-1]['nav'], 2) if filtered else 0,
                                'change_pct': round(((filtered[-1]['nav'] - filtered[0]['nav']) / filtered[0]['nav'] * 100), 2) if filtered and filtered[0]['nav'] > 0 else 0
                            }
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Error loading NAV data: {e}")

        # Fallback to synthetic data
        synthetic = self._generate_synthetic_historical(fund.get('scheme_name', ''))
        if isinstance(synthetic, pd.DataFrame) and not synthetic.empty:
            # Filter by period
            period_days = {'1M': 30, '3M': 90, '6M': 180, '1Y': 252, '3Y': 756, '5Y': 1260, 'MAX': 99999}
            days = period_days.get(period.upper(), 252)
            data = synthetic.tail(min(days, len(synthetic)))

            return {
                'success': True,
                'fund_id': fund_id,
                'scheme_name': fund.get('scheme_name', ''),
                'scheme_code': None,
                'period': period,
                'dates': data['date'].tolist(),
                'values': [round(v, 2) for v in data['nav'].tolist()],
                'start_nav': round(data['nav'].iloc[0], 2),
                'end_nav': round(data['nav'].iloc[-1], 2),
                'change_pct': round(((data['nav'].iloc[-1] - data['nav'].iloc[0]) / data['nav'].iloc[0] * 100), 2) if data['nav'].iloc[0] > 0 else 0,
                'synthetic': True
            }

        return {'error': 'No historical data available'}


# Singleton instance
data_processor = MutualFundDataProcessor()


def get_processor() -> MutualFundDataProcessor:
    """Get the data processor singleton"""
    return data_processor
