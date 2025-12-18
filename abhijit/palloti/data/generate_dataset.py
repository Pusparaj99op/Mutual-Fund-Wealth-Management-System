"""
Synthetic Mutual Fund Dataset Generator
Generates realistic Indian mutual fund data for the wealth management system.
"""

import json
import random
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

def generate_mutual_fund_dataset(num_funds=150, output_path="data/raw/MF_India_AI.json"):
    """
    Generate synthetic mutual fund data with realistic characteristics.
    
    Args:
        num_funds: Number of mutual funds to generate
        output_path: Path to save the JSON dataset
    """
    
    # Ensure output directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    amcs = [
        "HDFC AMC", "ICICI Prudential", "Axis Mutual Fund", "SBI Mutual Fund",
        "Aditya Birla Sun Life", "Reliance Mutual Fund", "Kotak Mahindra",
        "Franklin Templeton", "T. Rowe Price", "DSP BlackRock", "UTI Mutual Fund",
        "BNP Paribas", "Principal Mutual Fund", "LIC Mutual Fund", "BOI AXA"
    ]
    
    categories = {
        "Equity": ["Large Cap", "Mid Cap", "Small Cap", "Multi Cap", "Dividend Yield"],
        "Debt": ["Liquid", "Money Market", "Short Duration", "Medium Duration", "Long Duration"],
        "Hybrid": ["Conservative Hybrid", "Balanced Hybrid", "Aggressive Hybrid"],
        "Solution Oriented": ["Retirement", "Education"],
        "Other": ["Gold", "International"]
    }
    
    funds = []
    
    for i in range(num_funds):
        category = random.choice(list(categories.keys()))
        sub_category = random.choice(categories[category])
        
        # Risk level based on category
        if category == "Equity":
            risk_level = random.randint(4, 6)
            base_return_1yr = random.uniform(-15, 35)
            base_return_3yr = random.uniform(5, 25)
            base_return_5yr = random.uniform(8, 22)
            min_sip = random.randint(500, 5000)
            min_lumpsum = random.randint(5000, 50000)
            expense_ratio = round(random.uniform(0.5, 2.5), 2)
        elif category == "Debt":
            risk_level = random.randint(1, 3)
            base_return_1yr = random.uniform(3, 10)
            base_return_3yr = random.uniform(5, 9)
            base_return_5yr = random.uniform(5, 8)
            min_sip = random.randint(500, 1000)
            min_lumpsum = random.randint(5000, 25000)
            expense_ratio = round(random.uniform(0.2, 1.0), 2)
        elif category == "Hybrid":
            risk_level = random.randint(2, 5)
            base_return_1yr = random.uniform(0, 20)
            base_return_3yr = random.uniform(5, 15)
            base_return_5yr = random.uniform(6, 14)
            min_sip = random.randint(500, 2000)
            min_lumpsum = random.randint(5000, 35000)
            expense_ratio = round(random.uniform(0.4, 1.5), 2)
        else:
            risk_level = random.randint(2, 4)
            base_return_1yr = random.uniform(0, 15)
            base_return_3yr = random.uniform(5, 12)
            base_return_5yr = random.uniform(5, 11)
            min_sip = random.randint(500, 1000)
            min_lumpsum = random.randint(5000, 25000)
            expense_ratio = round(random.uniform(0.3, 1.2), 2)
        
        # Realistic metrics
        fund_size = round(random.uniform(100, 50000), 2)  # In crores
        fund_age = random.randint(1, 25)  # Years
        
        # Alpha, Beta, Sharpe, Sortino
        alpha = round(random.uniform(-5, 15), 2)
        beta = round(random.uniform(0.5, 1.8), 2) if "Equity" in category else round(random.uniform(0.1, 0.5), 2)
        sharpe = round(random.uniform(0.5, 3.0), 2)
        sortino = round(random.uniform(1.0, 4.5), 2)
        std_dev = round(random.uniform(2, 25), 2)
        
        # Rating (0-5)
        rating = round(random.uniform(2.5, 5.0), 1)
        
        # AUM (Assets Under Management)
        aum_nav = round(random.uniform(10, 500), 2)
        
        fund = {
            "scheme_id": f"FUND_{i+1:04d}",
            "scheme_name": f"{random.choice(amcs)} {sub_category} Fund {i+1}",
            "amc_name": random.choice(amcs),
            "category": category,
            "sub_category": sub_category,
            "min_sip": min_sip,
            "min_lumpsum": min_lumpsum,
            "expense_ratio": expense_ratio,
            "fund_size_cr": fund_size,
            "fund_age_years": fund_age,
            "risk_level": risk_level,
            "alpha": alpha,
            "beta": beta,
            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,
            "std_deviation": std_dev,
            "rating": rating,
            "return_1yr": round(base_return_1yr, 2),
            "return_3yr": round(base_return_3yr, 2),
            "return_5yr": round(base_return_5yr, 2),
            "aum_nav": aum_nav,
            "inception_date": (datetime.now() - timedelta(days=365*fund_age)).strftime("%Y-%m-%d"),
            "nav": round(random.uniform(10, 200), 2),
            "nav_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        funds.append(fund)
    
    # Save dataset
    with open(output_path, 'w') as f:
        json.dump(funds, f, indent=2)
    
    print(f"✓ Generated {num_funds} mutual funds and saved to {output_path}")
    return funds

if __name__ == "__main__":
    generate_mutual_fund_dataset(num_funds=150)
    print("Dataset generation complete!")
