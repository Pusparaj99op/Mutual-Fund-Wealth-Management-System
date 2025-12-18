"""
Flask API Server for FIMFP - Federal Indian Mutual Fund Portal
Main application entry point with all REST API endpoints
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_processor import get_processor
from ml_models import (monte_carlo, black_scholes, black_litterman, create_portfolio_optimizer,
                       garch_model, momentum_strategy, factor_model, risk_parity,
                       ml_predictor, sentiment_analyzer, drawdown_analyzer)
from recommendation_engine import get_engine, RiskProfiler
import numpy as np

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Initialize components
data_processor = get_processor()
recommendation_engine = get_engine()

# Load data on startup
data_processor.load_mutual_fund_data()


# ============== Static File Routes ==============

@app.route('/')
def serve_frontend():
    """Serve the main frontend page"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/css/<path:filename>')
def serve_css(filename):
    """Serve CSS files"""
    return send_from_directory(os.path.join(app.static_folder, 'css'), filename)


@app.route('/js/<path:filename>')
def serve_js(filename):
    """Serve JavaScript files"""
    return send_from_directory(os.path.join(app.static_folder, 'js'), filename)


# ============== API Routes ==============

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'FIMFP - Federal Indian Mutual Fund Portal',
        'version': '1.0.0'
    })


# -------------- Fund Data Endpoints --------------

@app.route('/api/funds')
def get_funds():
    """Get all mutual funds with pagination and filtering"""
    # Query parameters
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    risk_level = request.args.get('risk_level', None, type=int)
    min_rating = request.args.get('min_rating', None, type=int)

    if query or category or risk_level or min_rating:
        # Search with filters
        funds = data_processor.search_funds(
            query=query,
            category=category,
            risk_level=risk_level,
            min_rating=min_rating
        )
        total = len(funds)
        funds = funds[offset:offset+limit]
    else:
        # Get all with pagination
        funds, total = data_processor.get_all_funds(limit=limit, offset=offset)

    return jsonify({
        'success': True,
        'data': funds,
        'total': total,
        'limit': limit,
        'offset': offset
    })


@app.route('/api/fund/<int:fund_id>')
def get_fund(fund_id):
    """Get detailed information for a specific fund"""
    fund = data_processor.get_fund_by_id(fund_id)

    if fund is None:
        return jsonify({
            'success': False,
            'error': 'Fund not found'
        }), 404

    # Get comprehensive statistics
    stats = data_processor.get_fund_statistics(fund_id)

    return jsonify({
        'success': True,
        'data': stats
    })


@app.route('/api/categories')
def get_categories():
    """Get all available fund categories"""
    categories = data_processor.get_categories()
    sub_categories = data_processor.get_sub_categories()

    return jsonify({
        'success': True,
        'categories': categories,
        'sub_categories': sub_categories
    })


@app.route('/api/amcs')
def get_amcs():
    """Get all Asset Management Companies"""
    amcs = data_processor.get_amcs()
    return jsonify({
        'success': True,
        'amcs': amcs
    })


@app.route('/api/top-funds')
def get_top_funds():
    """Get top funds by category"""
    category = request.args.get('category', 'Equity')
    n = request.args.get('n', 10, type=int)

    top_funds = data_processor.get_top_funds_by_category(category, n)

    return jsonify({
        'success': True,
        'category': category,
        'data': top_funds
    })


# -------------- Prediction Endpoints --------------

@app.route('/api/predict/<int:fund_id>')
def predict_fund(fund_id):
    """Get Monte Carlo prediction for a fund"""
    # Get fund data
    fund = data_processor.get_fund_by_id(fund_id)

    if fund is None:
        return jsonify({
            'success': False,
            'error': 'Fund not found'
        }), 404

    # Query parameters
    investment = request.args.get('investment', 100000, type=float)
    days = request.args.get('days', 252, type=int)

    # Run Monte Carlo simulation
    prediction = monte_carlo.predict_nav(
        current_nav=investment,
        annual_return=fund.get('returns_1yr', 10),
        volatility=fund.get('sd', 15),
        days=days
    )

    # Add fund info to response
    prediction['fund'] = {
        'fund_id': fund_id,
        'scheme_name': fund.get('scheme_name', ''),
        'category': fund.get('category', '')
    }

    return jsonify({
        'success': True,
        'data': prediction
    })


@app.route('/api/stress-test/<int:fund_id>')
def stress_test(fund_id):
    """Perform stress testing on a fund"""
    fund = data_processor.get_fund_by_id(fund_id)

    if fund is None:
        return jsonify({
            'success': False,
            'error': 'Fund not found'
        }), 404

    investment = request.args.get('investment', 100000, type=float)

    # Define stress scenarios
    scenarios = {
        'baseline': {'return_multiplier': 1.0, 'vol_multiplier': 1.0},
        'mild_recession': {'return_multiplier': 0.5, 'vol_multiplier': 1.3},
        'severe_recession': {'return_multiplier': -0.5, 'vol_multiplier': 2.0},
        'bull_market': {'return_multiplier': 1.5, 'vol_multiplier': 0.8},
        'high_volatility': {'return_multiplier': 1.0, 'vol_multiplier': 2.0}
    }

    results = monte_carlo.stress_test(
        current_nav=investment,
        annual_return=fund.get('returns_1yr', 10),
        volatility=fund.get('sd', 15),
        scenarios=scenarios
    )

    return jsonify({
        'success': True,
        'fund': {
            'fund_id': fund_id,
            'scheme_name': fund.get('scheme_name', '')
        },
        'stress_test_results': results
    })


@app.route('/api/risk-analysis/<int:fund_id>')
def risk_analysis(fund_id):
    """Get Black-Scholes based risk analysis"""
    fund = data_processor.get_fund_by_id(fund_id)

    if fund is None:
        return jsonify({
            'success': False,
            'error': 'Fund not found'
        }), 404

    time_horizon = request.args.get('horizon', 1.0, type=float)

    # Calculate risk premium
    annual_return = fund.get('returns_1yr', 10)
    volatility = fund.get('sd', 15) / 100

    risk_analysis = black_scholes.calculate_risk_premium(
        current_nav=100,
        expected_nav=100 * (1 + annual_return/100),
        volatility=volatility,
        time_horizon=time_horizon
    )

    # Calculate Greeks
    greeks = black_scholes.calculate_greeks(
        S=100,
        K=100,
        r=0.06,
        sigma=volatility,
        T=time_horizon
    )

    return jsonify({
        'success': True,
        'fund': {
            'fund_id': fund_id,
            'scheme_name': fund.get('scheme_name', '')
        },
        'risk_analysis': risk_analysis,
        'greeks': greeks
    })


# -------------- Recommendation Endpoints --------------

@app.route('/api/recommend', methods=['GET', 'POST'])
def get_recommendations():
    """Get AI-powered fund recommendations"""
    if request.method == 'POST':
        data = request.get_json() or {}
    else:
        data = request.args.to_dict()

    # Parse risk profile parameters
    risk_profile = None
    if any(k in data for k in ['age', 'income', 'horizon', 'loss_tolerance', 'experience']):
        risk_profile = RiskProfiler.calculate_risk_score(
            age=int(data.get('age', 35)),
            income=float(data.get('income', 10)),
            investment_horizon=int(data.get('horizon', 5)),
            loss_tolerance=int(data.get('loss_tolerance', 3)),
            investment_experience=int(data.get('experience', 3))
        )

    # Get recommendations
    investment_amount = float(data.get('investment', 100000))
    horizon = int(data.get('horizon', 5))
    categories = data.get('categories', '').split(',') if data.get('categories') else None
    top_n = int(data.get('top_n', 10))

    recommendations = recommendation_engine.get_recommendations(
        risk_profile=risk_profile,
        investment_amount=investment_amount,
        investment_horizon=horizon,
        categories=categories,
        top_n=top_n
    )

    return jsonify({
        'success': True,
        'data': recommendations
    })


@app.route('/api/sip-recommend')
def sip_recommendations():
    """Get SIP-focused recommendations"""
    monthly_amount = request.args.get('monthly', 5000, type=float)
    risk_level = request.args.get('risk_level', 3, type=int)
    horizon = request.args.get('horizon', 5, type=int)

    recommendations = recommendation_engine.get_sip_recommendations(
        monthly_amount=monthly_amount,
        risk_level=risk_level,
        horizon=horizon
    )

    return jsonify({
        'success': True,
        'data': recommendations
    })


@app.route('/api/risk-profile', methods=['POST'])
def calculate_risk_profile():
    """Calculate investor risk profile"""
    data = request.get_json()

    if not data:
        return jsonify({
            'success': False,
            'error': 'Request body required'
        }), 400

    profile = RiskProfiler.calculate_risk_score(
        age=int(data.get('age', 35)),
        income=float(data.get('income', 10)),
        investment_horizon=int(data.get('investment_horizon', 5)),
        loss_tolerance=int(data.get('loss_tolerance', 3)),
        investment_experience=int(data.get('investment_experience', 3))
    )

    return jsonify({
        'success': True,
        'data': profile
    })


# -------------- Portfolio Optimization Endpoints --------------

@app.route('/api/optimize', methods=['POST'])
def optimize_portfolio():
    """Optimize portfolio using Black-Litterman model"""
    data = request.get_json()

    if not data or 'fund_ids' not in data:
        return jsonify({
            'success': False,
            'error': 'fund_ids array required in request body'
        }), 400

    fund_ids = data.get('fund_ids', [])
    investment_amount = float(data.get('investment', 100000))
    views = data.get('views', None)

    result = recommendation_engine.optimize_portfolio(
        fund_ids=fund_ids,
        investment_amount=investment_amount,
        investor_views=views
    )

    if 'error' in result:
        return jsonify({
            'success': False,
            'error': result['error']
        }), 400

    return jsonify({
        'success': True,
        'data': result
    })


@app.route('/api/compare', methods=['POST'])
def compare_funds():
    """Compare multiple funds side by side"""
    data = request.get_json()

    if not data or 'fund_ids' not in data:
        return jsonify({
            'success': False,
            'error': 'fund_ids array required in request body'
        }), 400

    fund_ids = data.get('fund_ids', [])

    result = recommendation_engine.compare_funds(fund_ids)

    if 'error' in result:
        return jsonify({
            'success': False,
            'error': result['error']
        }), 400

    return jsonify({
        'success': True,
        'data': result
    })


@app.route('/api/efficient-frontier', methods=['POST'])
def efficient_frontier():
    """Generate efficient frontier for given funds"""
    data = request.get_json()

    if not data or 'fund_ids' not in data:
        return jsonify({
            'success': False,
            'error': 'fund_ids array required in request body'
        }), 400

    fund_ids = data.get('fund_ids', [])

    # Get fund data
    funds = [data_processor.get_fund_by_id(fid) for fid in fund_ids]
    funds = [f for f in funds if f is not None]

    if len(funds) < 2:
        return jsonify({
            'success': False,
            'error': 'At least 2 valid funds required'
        }), 400

    # Generate frontier using Black-Litterman
    result = create_portfolio_optimizer(funds)

    return jsonify({
        'success': True,
        'data': {
            'efficient_frontier': result.get('efficient_frontier', {}),
            'optimal_portfolio': {
                'allocations': result.get('allocations', []),
                'metrics': result.get('portfolio_metrics', {})
            }
        }
    })


# -------------- Analytics Endpoints --------------

@app.route('/api/analytics/summary')
def analytics_summary():
    """Get overall analytics summary"""
    funds, total = data_processor.get_all_funds(limit=1000)

    if not funds:
        return jsonify({
            'success': False,
            'error': 'No fund data available'
        }), 500

    # Calculate summary statistics
    import statistics

    returns_1yr = [f.get('returns_1yr', 0) for f in funds if f.get('returns_1yr') is not None]
    sharpe_ratios = [f.get('sharpe', 0) for f in funds if f.get('sharpe') is not None]

    # Category distribution
    categories = {}
    for fund in funds:
        cat = fund.get('category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1

    # Risk level distribution
    risk_levels = {}
    for fund in funds:
        risk = fund.get('risk_level', 0)
        risk_levels[str(risk)] = risk_levels.get(str(risk), 0) + 1

    # Top performing categories
    category_returns = {}
    for fund in funds:
        cat = fund.get('category', 'Unknown')
        ret = fund.get('returns_1yr', 0)
        if cat not in category_returns:
            category_returns[cat] = []
        category_returns[cat].append(ret)

    avg_category_returns = {
        cat: round(statistics.mean(returns), 2)
        for cat, returns in category_returns.items() if returns
    }

    return jsonify({
        'success': True,
        'data': {
            'total_funds': total,
            'returns_summary': {
                'average_1yr': round(statistics.mean(returns_1yr), 2) if returns_1yr else 0,
                'median_1yr': round(statistics.median(returns_1yr), 2) if returns_1yr else 0,
                'max_1yr': round(max(returns_1yr), 2) if returns_1yr else 0,
                'min_1yr': round(min(returns_1yr), 2) if returns_1yr else 0
            },
            'sharpe_summary': {
                'average': round(statistics.mean(sharpe_ratios), 2) if sharpe_ratios else 0,
                'max': round(max(sharpe_ratios), 2) if sharpe_ratios else 0
            },
            'category_distribution': categories,
            'risk_level_distribution': risk_levels,
            'category_avg_returns': avg_category_returns
        }
    })


@app.route('/api/analytics/historical/<int:fund_id>')
def historical_performance(fund_id):
    """Get historical performance data for a fund"""
    fund = data_processor.get_fund_by_id(fund_id)

    if fund is None:
        return jsonify({
            'success': False,
            'error': 'Fund not found'
        }), 404

    # Get or generate historical data
    historical = data_processor.load_historical_data(fund.get('scheme_name', ''))

    return jsonify({
        'success': True,
        'fund': {
            'fund_id': fund_id,
            'scheme_name': fund.get('scheme_name', '')
        },
        'data': historical.to_dict('records') if not historical.empty else []
    })


# -------------- Advanced AI/ML Endpoints --------------

@app.route('/api/advanced/ml-predict/<int:fund_id>')
def ml_prediction(fund_id):
    """Get ML-based return prediction for a fund"""
    fund = data_processor.get_fund_by_id(fund_id)

    if fund is None:
        return jsonify({'success': False, 'error': 'Fund not found'}), 404

    prediction = ml_predictor.predict_returns(fund)

    return jsonify({
        'success': True,
        'fund': {'fund_id': fund_id, 'scheme_name': fund.get('scheme_name', '')},
        'data': prediction
    })


@app.route('/api/advanced/momentum/<int:fund_id>')
def momentum_analysis(fund_id):
    """Get momentum analysis for a fund"""
    fund = data_processor.get_fund_by_id(fund_id)

    if fund is None:
        return jsonify({'success': False, 'error': 'Fund not found'}), 404

    # Use available returns data
    momentum = momentum_strategy.calculate_momentum_score(
        returns_1m=fund.get('returns_1yr', 10) / 12,  # Approximate monthly
        returns_3m=fund.get('returns_1yr', 10) / 4,   # Approximate quarterly
        returns_6m=fund.get('returns_1yr', 10) / 2,   # Approximate 6-month
        returns_12m=fund.get('returns_1yr', 10)
    )

    return jsonify({
        'success': True,
        'fund': {'fund_id': fund_id, 'scheme_name': fund.get('scheme_name', '')},
        'data': momentum
    })


@app.route('/api/advanced/factor/<int:fund_id>')
def factor_analysis(fund_id):
    """Get multi-factor analysis for a fund"""
    fund = data_processor.get_fund_by_id(fund_id)

    if fund is None:
        return jsonify({'success': False, 'error': 'Fund not found'}), 404

    factors = factor_model.calculate_factor_exposure(
        alpha=fund.get('alpha', 0),
        beta=fund.get('beta', 1),
        sharpe=fund.get('sharpe', 0),
        volatility=fund.get('sd', 15),
        returns_1yr=fund.get('returns_1yr', 10),
        fund_size=fund.get('fund_size_cr', 1000),
        expense_ratio=fund.get('expense_ratio', 1.5)
    )

    return jsonify({
        'success': True,
        'fund': {'fund_id': fund_id, 'scheme_name': fund.get('scheme_name', '')},
        'data': factors
    })


@app.route('/api/advanced/sentiment/<int:fund_id>')
def sentiment_analysis(fund_id):
    """Get market sentiment analysis for a fund"""
    fund = data_processor.get_fund_by_id(fund_id)

    if fund is None:
        return jsonify({'success': False, 'error': 'Fund not found'}), 404

    sentiment = sentiment_analyzer.analyze_market_sentiment(
        returns_1yr=fund.get('returns_1yr', 10),
        volatility=fund.get('sd', 15)
    )

    return jsonify({
        'success': True,
        'fund': {'fund_id': fund_id, 'scheme_name': fund.get('scheme_name', '')},
        'data': sentiment
    })


@app.route('/api/advanced/complete/<int:fund_id>')
def complete_analysis(fund_id):
    """Get complete AI/ML analysis for a fund"""
    fund = data_processor.get_fund_by_id(fund_id)

    if fund is None:
        return jsonify({'success': False, 'error': 'Fund not found'}), 404

    # Monte Carlo
    mc_prediction = monte_carlo.predict_nav(
        current_nav=100000, annual_return=fund.get('returns_1yr', 10),
        volatility=fund.get('sd', 15), days=252
    )

    # Black-Scholes
    risk_premium = black_scholes.calculate_risk_premium(
        current_nav=100, expected_nav=100 * (1 + fund.get('returns_1yr', 10)/100),
        volatility=fund.get('sd', 15)/100
    )

    # ML Prediction
    ml_pred = ml_predictor.predict_returns(fund)

    # Momentum
    momentum = momentum_strategy.calculate_momentum_score(
        returns_1m=fund.get('returns_1yr', 10) / 12,
        returns_3m=fund.get('returns_1yr', 10) / 4,
        returns_6m=fund.get('returns_1yr', 10) / 2,
        returns_12m=fund.get('returns_1yr', 10)
    )

    # Factor Analysis
    factors = factor_model.calculate_factor_exposure(
        alpha=fund.get('alpha', 0), beta=fund.get('beta', 1),
        sharpe=fund.get('sharpe', 0), volatility=fund.get('sd', 15),
        returns_1yr=fund.get('returns_1yr', 10), fund_size=fund.get('fund_size_cr', 1000),
        expense_ratio=fund.get('expense_ratio', 1.5)
    )

    # Sentiment
    sentiment = sentiment_analyzer.analyze_market_sentiment(
        returns_1yr=fund.get('returns_1yr', 10), volatility=fund.get('sd', 15)
    )

    # Drawdown (simplified with synthetic data)
    returns_series = list(np.random.normal(fund.get('returns_1yr', 10)/252, fund.get('sd', 15)/np.sqrt(252), 252))
    drawdown = drawdown_analyzer.analyze_drawdown(returns_series)

    return jsonify({
        'success': True,
        'fund': {
            'fund_id': fund_id,
            'scheme_name': fund.get('scheme_name', ''),
            'category': fund.get('category', ''),
            'rating': fund.get('rating', 0)
        },
        'data': {
            'monte_carlo': {
                'expected_value': mc_prediction['statistics']['mean_nav'],
                'expected_return': mc_prediction['statistics']['expected_return_pct'],
                'var_95': mc_prediction['risk_metrics']['var_95'],
                'prob_loss': mc_prediction['risk_metrics']['probability_of_loss']
            },
            'black_scholes': risk_premium,
            'ml_prediction': ml_pred,
            'momentum': momentum,
            'factor_analysis': factors,
            'sentiment': sentiment,
            'drawdown': drawdown
        }
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8009))
    print(f"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   🇮🇳 FIMFP - Federal Indian Mutual Fund Portal 🇮🇳           ║
    ║                                                               ║
    ║   Server running at: http://localhost:{port}                   ║
    ║                                                               ║
    ║   API Endpoints:                                              ║
    ║   - GET  /api/funds           - List all funds                ║
    ║   - GET  /api/fund/<id>       - Get fund details              ║
    ║   - GET  /api/predict/<id>    - Monte Carlo prediction        ║
    ║   - POST /api/recommend       - AI recommendations            ║
    ║   - POST /api/optimize        - Portfolio optimization        ║
    ║   - GET  /api/analytics/summary - Analytics dashboard         ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=port, debug=True)
