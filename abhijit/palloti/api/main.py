"""
FastAPI Backend for Federal Wealth Management System
RESTful API endpoints for predictions, forecasts, and recommendations
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import logging
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from configs.config import API_TITLE, API_VERSION, API_DESCRIPTION, DATASET_PATH
from services.recommendation_engine import RecommendationEngine, SHAPExplainer
from utils.helpers import setup_logging, MetricsCalculator

logger = setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Global recommendation engine instance
recommendation_engine = None

# ============ Pydantic Models ============

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str

class InvestorProfile(BaseModel):
    """Investor profile for recommendations"""
    investment_amount: float = Field(..., gt=0, description="Investment amount in INR")
    investment_type: str = Field(default="sip", description="'sip' or 'lumpsum'")
    tenure_months: int = Field(default=60, ge=6, le=360, description="Investment tenure in months")
    category: Optional[str] = Field(default=None, description="Fund category (optional)")
    risk_tolerance: Optional[int] = Field(default=None, ge=1, le=6, description="Risk tolerance 1-6")

class RecommendationResponse(BaseModel):
    """Recommendation response structure"""
    scheme_id: str
    scheme_name: str
    amc_name: str
    category: str
    sub_category: str
    rating: float
    risk_level: int
    recommendation_score: float
    predicted_return_5yr: float
    historical_return_5yr: float
    sharpe_ratio: float
    expense_ratio: float
    min_sip: int
    min_lumpsum: int
    explanation: dict

class RecommendationsResponse(BaseModel):
    """Complete recommendations response"""
    timestamp: str
    investor_profile: dict
    recommendations: List[RecommendationResponse]
    filtering_stats: dict

class ReturnPredictionRequest(BaseModel):
    """Request for return prediction"""
    scheme_id: str = Field(..., description="Fund scheme ID")
    investment_period_years: float = Field(default=5, gt=0, le=30)

class ReturnPredictionResponse(BaseModel):
    """Return prediction response"""
    scheme_id: str
    scheme_name: str
    predicted_return: float
    confidence_interval: dict
    risk_metrics: dict
    explanation: dict

class NAVForecastRequest(BaseModel):
    """Request for NAV forecasting"""
    scheme_id: str = Field(..., description="Fund scheme ID")
    forecast_months: int = Field(default=12, ge=1, le=60)
    confidence_level: float = Field(default=0.95, ge=0.90, le=0.99)

class NAVForecastResponse(BaseModel):
    """NAV forecast response"""
    scheme_id: str
    scheme_name: str
    forecast_data: List[dict]
    confidence_level: float
    methodology: str

# ============ Initialize Engine ============

@app.on_event("startup")
async def startup_event():
    """Initialize recommendation engine on startup"""
    global recommendation_engine
    try:
        logger.info("Initializing recommendation engine...")
        recommendation_engine = RecommendationEngine(str(DATASET_PATH))
        logger.info("Recommendation engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize recommendation engine: {str(e)}")
        raise

# ============ Health Check Endpoint ============

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns:
        Health status, timestamp, and API version
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version=API_VERSION
    )

# ============ Recommendation Endpoint ============

@app.post("/recommend_funds", response_model=RecommendationsResponse)
async def recommend_funds(profile: InvestorProfile):
    """
    Get personalized mutual fund recommendations
    
    Args:
        profile: Investor profile with investment parameters
    
    Returns:
        List of recommended funds with explanations
    """
    try:
        if recommendation_engine is None:
            raise HTTPException(status_code=503, detail="Recommendation engine not initialized")
        
        logger.info(f"Processing recommendation request: {profile.investment_amount} INR")
        
        # Get recommendations
        recommendations, filtering_stats = recommendation_engine.get_recommendations(
            investment_amount=profile.investment_amount,
            investment_type=profile.investment_type.lower(),
            tenure_months=profile.tenure_months,
            category=profile.category,
            k=5
        )
        
        # Format response
        response = RecommendationsResponse(
            timestamp=datetime.now().isoformat(),
            investor_profile={
                "investment_amount": profile.investment_amount,
                "investment_type": profile.investment_type,
                "tenure_months": profile.tenure_months,
                "category": profile.category or "All Categories"
            },
            recommendations=recommendations,
            filtering_stats=filtering_stats
        )
        
        return response
    
    except Exception as e:
        logger.error(f"Error in recommendation endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ Return Prediction Endpoint ============

@app.post("/predict_returns", response_model=ReturnPredictionResponse)
async def predict_returns(request: ReturnPredictionRequest):
    """
    Predict future returns for a specific fund
    
    Args:
        request: Fund ID and prediction period
    
    Returns:
        Predicted returns with confidence intervals
    """
    try:
        if recommendation_engine is None:
            raise HTTPException(status_code=503, detail="Recommendation engine not initialized")
        
        # Get fund data
        fund_data = recommendation_engine.df[
            recommendation_engine.df['scheme_id'] == request.scheme_id
        ]
        
        if fund_data.empty:
            raise HTTPException(status_code=404, detail=f"Fund {request.scheme_id} not found")
        
        fund = fund_data.iloc[0]
        
        # Calculate prediction (using historical returns + trend)
        base_return = fund['return_5yr']
        trend = MetricsCalculator.calculate_return_trend([
            fund['return_1yr'], fund['return_3yr'], fund['return_5yr']
        ])
        predicted_return = base_return + (trend * 2)  # Extrapolate trend
        
        # Confidence intervals
        std_dev = fund['std_deviation']
        confidence_interval = {
            "lower": round(predicted_return - (std_dev * 1.96), 2),
            "expected": round(predicted_return, 2),
            "upper": round(predicted_return + (std_dev * 1.96), 2)
        }
        
        # Risk metrics
        risk_metrics = {
            "volatility": round(fund['std_deviation'], 2),
            "beta": round(fund['beta'], 2),
            "alpha": round(fund['alpha'], 2),
            "sharpe_ratio": round(fund['sharpe_ratio'], 2),
            "sortino_ratio": round(fund['sortino_ratio'], 2),
            "risk_level": int(fund['risk_level'])
        }
        
        # Explanation
        explanation = SHAPExplainer.get_feature_contribution(fund.to_dict())
        
        response = ReturnPredictionResponse(
            scheme_id=request.scheme_id,
            scheme_name=fund['scheme_name'],
            predicted_return=confidence_interval['expected'],
            confidence_interval=confidence_interval,
            risk_metrics=risk_metrics,
            explanation=explanation
        )
        
        logger.info(f"Return prediction for {fund['scheme_name']}: {confidence_interval['expected']}%")
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in return prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ NAV Forecasting Endpoint ============

@app.post("/forecast_nav", response_model=NAVForecastResponse)
async def forecast_nav(request: NAVForecastRequest):
    """
    Forecast NAV (Net Asset Value) for a fund
    
    Args:
        request: Fund ID and forecast horizon
    
    Returns:
        NAV forecast with confidence intervals
    """
    try:
        if recommendation_engine is None:
            raise HTTPException(status_code=503, detail="Recommendation engine not initialized")
        
        # Get fund data
        fund_data = recommendation_engine.df[
            recommendation_engine.df['scheme_id'] == request.scheme_id
        ]
        
        if fund_data.empty:
            raise HTTPException(status_code=404, detail=f"Fund {request.scheme_id} not found")
        
        fund = fund_data.iloc[0]
        
        # Generate forecast data (simplified polynomial trend)
        current_nav = float(fund['nav'])
        monthly_return = (fund['return_1yr'] / 100) / 12
        
        forecast_data = []
        for month in range(1, request.forecast_months + 1):
            projected_nav = current_nav * ((1 + monthly_return) ** month)
            
            forecast_data.append({
                "date": f"Month {month}",
                "forecasted_nav": round(projected_nav, 2),
                "lower_bound": round(projected_nav * 0.95, 2),
                "upper_bound": round(projected_nav * 1.05, 2)
            })
        
        response = NAVForecastResponse(
            scheme_id=request.scheme_id,
            scheme_name=fund['scheme_name'],
            forecast_data=forecast_data,
            confidence_level=request.confidence_level,
            methodology="Exponential growth model based on historical returns"
        )
        
        logger.info(f"NAV forecast for {fund['scheme_name']}: {request.forecast_months} months")
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in NAV forecasting: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ Fund Information Endpoint ============

@app.get("/funds/{scheme_id}")
async def get_fund_info(scheme_id: str):
    """
    Get detailed information about a fund
    
    Args:
        scheme_id: Fund scheme ID
    
    Returns:
        Complete fund details
    """
    try:
        if recommendation_engine is None:
            raise HTTPException(status_code=503, detail="Recommendation engine not initialized")
        
        fund_data = recommendation_engine.df[
            recommendation_engine.df['scheme_id'] == scheme_id
        ]
        
        if fund_data.empty:
            raise HTTPException(status_code=404, detail=f"Fund {scheme_id} not found")
        
        fund = fund_data.iloc[0]
        
        return {
            "scheme_id": fund['scheme_id'],
            "scheme_name": fund['scheme_name'],
            "amc_name": fund['amc_name'],
            "category": fund['category'],
            "sub_category": fund['sub_category'],
            "rating": float(fund['rating']),
            "risk_level": int(fund['risk_level']),
            "returns": {
                "return_1yr": round(float(fund['return_1yr']), 2),
                "return_3yr": round(float(fund['return_3yr']), 2),
                "return_5yr": round(float(fund['return_5yr']), 2)
            },
            "metrics": {
                "sharpe_ratio": round(float(fund['sharpe_ratio']), 2),
                "sortino_ratio": round(float(fund['sortino_ratio']), 2),
                "alpha": round(float(fund['alpha']), 2),
                "beta": round(float(fund['beta']), 2),
                "std_deviation": round(float(fund['std_deviation']), 2)
            },
            "investment_info": {
                "min_sip": int(fund['min_sip']),
                "min_lumpsum": int(fund['min_lumpsum']),
                "expense_ratio": round(float(fund['expense_ratio']), 2)
            },
            "other": {
                "fund_size_cr": round(float(fund['fund_size_cr']), 2),
                "fund_age_years": int(fund['fund_age_years']),
                "nav": round(float(fund['nav']), 2),
                "inception_date": fund['inception_date']
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching fund info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ Fund Comparison Endpoint ============

@app.post("/compare_funds")
async def compare_funds(scheme_ids: List[str] = Query(..., description="List of scheme IDs to compare")):
    """
    Compare multiple funds side-by-side
    
    Args:
        scheme_ids: List of fund IDs to compare
    
    Returns:
        Comparative analysis of funds
    """
    try:
        if recommendation_engine is None:
            raise HTTPException(status_code=503, detail="Recommendation engine not initialized")
        
        comparison_df = recommendation_engine.get_fund_comparison(scheme_ids)
        
        if comparison_df.empty:
            raise HTTPException(status_code=404, detail="No matching funds found")
        
        # Convert to comparison format
        comparison_data = []
        for _, fund in comparison_df.iterrows():
            comparison_data.append({
                "scheme_id": fund['scheme_id'],
                "scheme_name": fund['scheme_name'],
                "rating": float(fund['rating']),
                "risk_level": int(fund['risk_level']),
                "return_5yr": round(float(fund['return_5yr']), 2),
                "sharpe_ratio": round(float(fund['sharpe_ratio']), 2),
                "expense_ratio": round(float(fund['expense_ratio']), 2)
            })
        
        return {
            "comparison": comparison_data,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing funds: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ Error Handlers ============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": datetime.now().isoformat()}
    )

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting {API_TITLE} v{API_VERSION}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
