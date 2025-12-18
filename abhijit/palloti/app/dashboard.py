"""
Streamlit Dashboard for Federal Wealth Management System
Interactive UI for fund recommendations and analytics
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime
from typing import Dict, List
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.helpers import DataLoader, MetricsCalculator, setup_logging

logger = setup_logging()

# ============ Page Configuration ============

st.set_page_config(
    page_title="Federal Wealth Management System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .recommendation-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .success {
        color: #10B981;
        font-weight: bold;
    }
    .warning {
        color: #F59E0B;
        font-weight: bold;
    }
    .danger {
        color: #EF4444;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ============ Session State ============

if 'api_url' not in st.session_state:
    st.session_state.api_url = "http://localhost:8000"

if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None

if 'comparison_data' not in st.session_state:
    st.session_state.comparison_data = None

# ============ Sidebar Configuration ============

with st.sidebar:
    st.image("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext x='50' y='70' font-size='60' font-weight='bold' text-anchor='middle' fill='%23667eea'%3E💰%3C/text%3E%3C/svg%3E", 
             width=100)
    
    st.markdown("## ⚙️ Configuration")
    
    api_url = st.text_input(
        "API Base URL",
        value=st.session_state.api_url,
        help="FastAPI backend URL"
    )
    st.session_state.api_url = api_url
    
    # Test connection
    if st.button("🔗 Test Connection"):
        try:
            response = requests.get(f"{api_url}/health", timeout=2)
            if response.status_code == 200:
                st.success("✓ Connected to API")
            else:
                st.error("✗ API returned error")
        except:
            st.error("✗ Cannot reach API. Ensure backend is running on port 8000")
    
    st.divider()
    st.markdown("## 📊 About")
    st.info("""
    **Federal Wealth Management System**
    
    AI-powered mutual fund recommendation system for Indian investors.
    
    - 🤖 ML-driven predictions
    - 📈 Risk-adjusted rankings
    - 💡 Explainable recommendations
    """)

# ============ Main Title ============

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("# 💰 Federal Wealth Management System")
    st.markdown("### AI-Powered Mutual Fund Recommendation Platform")
with col2:
    st.metric("Status", "🟢 Active")

st.divider()

# ============ Tab Layout ============

tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Get Recommendations",
    "📊 Fund Analytics",
    "🔍 Fund Details",
    "📈 Comparison"
])

# ============ Tab 1: Recommendations ============

with tab1:
    st.markdown("## Find Your Perfect Investment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Investment Profile")
        
        investment_amount = st.number_input(
            "Investment Amount (₹)",
            min_value=500,
            value=100000,
            step=1000,
            help="Minimum investment amount"
        )
        
        investment_type = st.radio(
            "Investment Type",
            options=["sip", "lumpsum"],
            format_func=lambda x: "SIP (Systematic)" if x == "sip" else "Lumpsum (One-time)",
            horizontal=True
        )
        
        tenure_months = st.select_slider(
            "Investment Tenure",
            options=[6, 12, 24, 36, 60, 120],
            value=60,
            format_func=lambda x: f"{x} months ({x//12} years)" if x >= 12 else f"{x} months"
        )
        
        category = st.selectbox(
            "Fund Category (Optional)",
            options=[
                None, "Equity", "Debt", "Hybrid", 
                "Solution Oriented", "Other"
            ],
            format_func=lambda x: "All Categories" if x is None else x
        )
        
        risk_tolerance = st.slider(
            "Risk Tolerance (1-6)",
            min_value=1,
            max_value=6,
            value=3,
            help="1=Low Risk, 6=High Risk"
        )
    
    with col2:
        st.subheader("💡 Recommendation Info")
        
        st.info("""
        **How Recommendations Work:**
        
        Our AI system analyzes:
        - Historical fund performance
        - Risk metrics (Sharpe, Sortino ratios)
        - Expense ratios and fund size
        - Your investment profile
        
        **Filters Applied:**
        - Minimum SIP/Lumpsum requirements
        - Risk level vs tenure match
        - Minimum rating ≥ 3.0
        - Category preferences
        
        **Scoring:**
        - 25% Rating
        - 35% Predicted Returns
        - 20% Risk-Adjusted Returns
        - 10% Cost Efficiency
        - 10% Risk Profile
        """)
    
    st.divider()
    
    # Get Recommendations Button
    if st.button("🚀 Get Recommendations", use_container_width=True, type="primary"):
        try:
            with st.spinner("🔍 Analyzing funds and generating recommendations..."):
                
                payload = {
                    "investment_amount": investment_amount,
                    "investment_type": investment_type,
                    "tenure_months": int(tenure_months),
                    "category": category,
                    "risk_tolerance": risk_tolerance
                }
                
                response = requests.post(
                    f"{st.session_state.api_url}/recommend_funds",
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.recommendations = data
                    st.success("✓ Recommendations generated successfully!")
                else:
                    st.error(f"API Error: {response.status_code}")
        
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Ensure backend is running at http://localhost:8000")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    # Display Recommendations
    if st.session_state.recommendations:
        
        recommendations = st.session_state.recommendations
        
        # Summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Funds Analyzed", recommendations['filtering_stats']['total_funds_in_database'])
        with col2:
            st.metric("Funds Matched", recommendations['filtering_stats']['funds_after_filtering'])
        with col3:
            st.metric("Recommendations", recommendations['filtering_stats']['recommendations_provided'])
        with col4:
            st.metric("Generated", recommendations['timestamp'][:10])
        
        st.divider()
        
        # Recommendations List
        st.markdown("### 🏆 Top Recommendations")
        
        for idx, fund in enumerate(recommendations['recommendations'], 1):
            
            with st.container(border=True):
                
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.markdown(f"### #{idx}")
                    st.markdown(f"**Score:** {fund['recommendation_score']}/100")
                
                with col2:
                    st.markdown(f"### {fund['scheme_name'][:30]}...")
                    st.caption(f"AMC: {fund['amc_name']}")
                
                with col3:
                    st.markdown(f"**Category:** {fund['category']}")
                    st.markdown(f"**Risk:** {'🔴' * fund['risk_level']} {fund['risk_level']}/6")
                
                with col4:
                    st.markdown(f"**Return:** 📈 {fund['predicted_return_5yr']}%")
                    st.markdown(f"**Sharpe:** {fund['sharpe_ratio']}")
                
                with col5:
                    st.markdown(f"**Rating:** {'⭐' * int(fund['rating'])} {fund['rating']}/5")
                    st.markdown(f"**Expense:** {fund['expense_ratio']}%")
                
                st.divider()
                
                # Explanation
                if fund['explanation']:
                    exp = fund['explanation']
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if exp.get('strengths'):
                            st.markdown("**✓ Strengths:**")
                            for strength in exp['strengths']:
                                st.caption(f"• {strength}")
                    
                    with col2:
                        if exp.get('weaknesses'):
                            st.markdown("**⚠️ Considerations:**")
                            for weakness in exp['weaknesses']:
                                st.caption(f"• {weakness}")
                    
                    st.caption(f"💡 {exp.get('investment_rationale', '')}")

# ============ Tab 2: Fund Analytics ============

with tab2:
    st.markdown("## 📊 Fund Analytics Dashboard")
    
    try:
        # Load dataset
        from configs.config import DATASET_PATH
        df = DataLoader.load_dataset(str(DATASET_PATH))
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Funds", len(df))
        with col2:
            st.metric("Avg Rating", f"{df['rating'].mean():.2f}")
        with col3:
            st.metric("Avg Return (5Y)", f"{df['return_5yr'].mean():.2f}%")
        
        st.divider()
        
        # Category Distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Distribution by Category")
            category_counts = df['category'].value_counts()
            fig = go.Figure(data=[go.Pie(
                labels=category_counts.index,
                values=category_counts.values,
                hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>"
            )])
            fig.update_layout(height=400, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Average Rating by Category")
            rating_by_cat = df.groupby('category')['rating'].mean().sort_values(ascending=False)
            fig = go.Figure(data=[go.Bar(
                y=rating_by_cat.index,
                x=rating_by_cat.values,
                orientation='h',
                marker_color='#667eea',
                hovertemplate="<b>%{y}</b><br>Avg Rating: %{x:.2f}<extra></extra>"
            )])
            fig.update_layout(height=400, xaxis_title="Average Rating", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Risk vs Return Scatter
        st.subheader("Risk vs Return Analysis")
        
        fig = go.Figure(data=[go.Scatter(
            x=df['std_deviation'],
            y=df['return_5yr'],
            mode='markers',
            marker=dict(
                size=df['rating'] * 3,
                color=df['risk_level'],
                colorscale='RdYlGn_r',
                showscale=True,
                colorbar=dict(title="Risk Level")
            ),
            text=df['scheme_name'],
            hovertemplate="<b>%{text}</b><br>Volatility: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>"
        )])
        fig.update_layout(
            title="Risk (Volatility) vs Return (5Y)",
            xaxis_title="Standard Deviation (%)",
            yaxis_title="5-Year Return (%)",
            height=500,
            hovermode='closest'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Return Comparison
        st.subheader("Historical Returns Comparison")
        
        returns_data = {
            '1-Year': df['return_1yr'].mean(),
            '3-Year': df['return_3yr'].mean(),
            '5-Year': df['return_5yr'].mean()
        }
        
        fig = go.Figure(data=[go.Bar(
            x=list(returns_data.keys()),
            y=list(returns_data.values()),
            marker_color=['#667eea', '#764ba2', '#f093fb'],
            hovertemplate="<b>%{x}</b><br>Avg Return: %{y:.2f}%<extra></extra>"
        )])
        fig.update_layout(
            title="Average Returns by Period",
            yaxis_title="Return (%)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")

# ============ Tab 3: Fund Details ============

with tab3:
    st.markdown("## 🔍 Fund Information Search")
    
    try:
        from configs.config import DATASET_PATH
        df = DataLoader.load_dataset(str(DATASET_PATH))
        
        # Search options
        col1, col2 = st.columns(2)
        
        with col1:
            search_type = st.radio(
                "Search By",
                options=["Scheme Name", "Fund ID", "AMC Name"],
                horizontal=True
            )
        
        with col2:
            if search_type == "Scheme Name":
                search_term = st.selectbox(
                    "Select Fund",
                    options=df['scheme_name'].tolist()
                )
                fund = df[df['scheme_name'] == search_term].iloc[0]
            elif search_type == "Fund ID":
                search_term = st.selectbox(
                    "Select Fund ID",
                    options=df['scheme_id'].tolist()
                )
                fund = df[df['scheme_id'] == search_term].iloc[0]
            else:  # AMC
                amc_name = st.selectbox(
                    "Select AMC",
                    options=df['amc_name'].unique().tolist()
                )
                amc_funds = df[df['amc_name'] == amc_name]
                search_term = st.selectbox(
                    "Select Fund",
                    options=amc_funds['scheme_name'].tolist()
                )
                fund = amc_funds[amc_funds['scheme_name'] == search_term].iloc[0]
        
        st.divider()
        
        # Fund Details Display
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Rating", f"{'⭐' * int(fund['rating'])} {fund['rating']}")
        with col2:
            st.metric("Risk Level", f"{fund['risk_level']}/6")
        with col3:
            st.metric("Fund Age", f"{fund['fund_age_years']} years")
        with col4:
            st.metric("Fund Size", f"₹{fund['fund_size_cr']:.0f}Cr")
        with col5:
            st.metric("Expense", f"{fund['expense_ratio']}%")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Performance Metrics")
            metrics_df = pd.DataFrame({
                'Metric': ['1-Year Return', '3-Year Return', '5-Year Return', 
                          'Sharpe Ratio', 'Sortino Ratio', 'Alpha', 'Beta', 
                          'Std Deviation'],
                'Value': [
                    f"{fund['return_1yr']:.2f}%",
                    f"{fund['return_3yr']:.2f}%",
                    f"{fund['return_5yr']:.2f}%",
                    f"{fund['sharpe_ratio']:.2f}",
                    f"{fund['sortino_ratio']:.2f}",
                    f"{fund['alpha']:.2f}",
                    f"{fund['beta']:.2f}",
                    f"{fund['std_deviation']:.2f}%"
                ]
            })
            st.dataframe(metrics_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.subheader("💼 Investment Info")
            invest_df = pd.DataFrame({
                'Information': ['AMC', 'Category', 'Sub-Category', 'Min SIP', 
                               'Min Lumpsum', 'NAV', 'Inception Date'],
                'Details': [
                    fund['amc_name'],
                    fund['category'],
                    fund['sub_category'],
                    f"₹{fund['min_sip']:.0f}",
                    f"₹{fund['min_lumpsum']:.0f}",
                    f"₹{fund['nav']:.2f}",
                    fund['inception_date']
                ]
            })
            st.dataframe(invest_df, use_container_width=True, hide_index=True)
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

# ============ Tab 4: Comparison ============

with tab4:
    st.markdown("## 📈 Fund Comparison")
    
    try:
        from configs.config import DATASET_PATH
        df = DataLoader.load_dataset(str(DATASET_PATH))
        
        st.subheader("Select Funds to Compare")
        
        selected_funds = st.multiselect(
            "Choose up to 5 funds",
            options=df['scheme_name'].tolist(),
            max_selections=5,
            placeholder="Select funds..."
        )
        
        if selected_funds and len(selected_funds) >= 2:
            comparison_df = df[df['scheme_name'].isin(selected_funds)].copy()
            
            st.divider()
            
            # Comparison Table
            st.markdown("### Detailed Comparison")
            
            comparison_cols = [
                'scheme_name', 'amc_name', 'category', 'rating', 'risk_level',
                'return_5yr', 'sharpe_ratio', 'expense_ratio', 'fund_size_cr'
            ]
            
            display_df = comparison_df[comparison_cols].copy()
            display_df.columns = ['Fund Name', 'AMC', 'Category', 'Rating', 'Risk',
                                 'Return 5Y', 'Sharpe', 'Expense', 'Size(Cr)']
            
            st.dataframe(
                display_df.style.format({
                    'Return 5Y': '{:.2f}%',
                    'Sharpe': '{:.2f}',
                    'Expense': '{:.2f}%',
                    'Size(Cr)': '{:.0f}'
                }),
                use_container_width=True,
                hide_index=True
            )
            
            st.divider()
            
            # Visual Comparison
            col1, col2 = st.columns(2)
            
            with col1:
                fig = go.Figure()
                for _, row in comparison_df.iterrows():
                    fig.add_trace(go.Bar(
                        name=row['scheme_name'][:20],
                        x=['1Y', '3Y', '5Y'],
                        y=[row['return_1yr'], row['return_3yr'], row['return_5yr']]
                    ))
                fig.update_layout(
                    title="Returns Comparison",
                    barmode='group',
                    xaxis_title="Period",
                    yaxis_title="Return (%)",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure()
                for _, row in comparison_df.iterrows():
                    fig.add_trace(go.Scatterpolar(
                        r=[
                            row['rating'] / 5 * 100,
                            (1 - row['risk_level'] / 6) * 100,
                            min(row['sharpe_ratio'] / 3 * 100, 100),
                            (1 - min(row['expense_ratio'] / 2.5, 1.0)) * 100
                        ],
                        theta=['Rating', 'Low Risk', 'Sharpe', 'Low Cost'],
                        fill='toself',
                        name=row['scheme_name'][:15]
                    ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    title="Multi-Dimensional Score",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        
        elif selected_funds:
            st.info("Please select at least 2 funds to compare")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

# ============ Footer ============

st.divider()
st.markdown("""
    <div style="text-align: center; color: #999; margin-top: 2rem;">
    <p>Federal Wealth Management System | AI-Powered Mutual Fund Recommendations</p>
    <p>Disclaimer: This system is for educational and informational purposes. 
    Always consult a certified financial advisor before making investment decisions.</p>
    </div>
""", unsafe_allow_html=True)
