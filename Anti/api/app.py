"""
Flask API Server for FIMFP - Federal Indian Mutual Fund Portal
Main application entry point with all REST API endpoints
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import sys
import hashlib
import secrets
from datetime import datetime, timedelta

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_processor import get_processor
from ml_models import (monte_carlo, black_scholes, black_litterman, create_portfolio_optimizer,
                       garch_model, momentum_strategy, factor_model, risk_parity,
                       ml_predictor, sentiment_analyzer, drawdown_analyzer)
from recommendation_engine import get_engine, RiskProfiler
import numpy as np

# MongoDB imports
try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, DuplicateKeyError
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    print("Warning: pymongo not installed. User authentication will be disabled.")

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app, supports_credentials=True)

# MongoDB Connection
MONGODB_URI = "mongodb+srv://vineetmandhalkar_db_user:CHfu7ImZVF2yyTnf@fimfp.ls5aqqk.mongodb.net/?appName=FIMFP"
db = None
users_collection = None
sessions_collection = None

if MONGODB_AVAILABLE:
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client['fimfp_db']
        users_collection = db['users']
        sessions_collection = db['sessions']
        # Create unique index on email
        users_collection.create_index('email', unique=True)
        # Create index on token for fast lookup
        sessions_collection.create_index('token', unique=True)
        # Create TTL index - sessions expire after 24 hours
        sessions_collection.create_index('createdAt', expireAfterSeconds=86400)
        print("✅ MongoDB connected successfully!")
    except Exception as e:
        print(f"⚠️ MongoDB connection failed: {e}")
        MONGODB_AVAILABLE = False


# Password hashing utilities
def hash_password(password):
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(password, stored_hash):
    """Verify password against stored hash"""
    try:
        salt, hashed = stored_hash.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == hashed
    except:
        return False


def generate_token():
    """Generate a simple session token"""
    return secrets.token_urlsafe(32)


def get_current_user():
    """Get current user from session token"""
    if not MONGODB_AVAILABLE:
        return None

    # Check Authorization header first
    auth_header = request.headers.get('Authorization', '')
    token = None

    if auth_header.startswith('Bearer '):
        token = auth_header[7:]
    else:
        # Check cookie
        token = request.cookies.get('auth_token')

    if not token:
        return None

    try:
        session = sessions_collection.find_one({'token': token})
        if session:
            user = users_collection.find_one({'_id': session['userId']})
            return user
    except:
        pass

    return None


# Public routes that don't require authentication
PUBLIC_ROUTES = [
    '/login', '/login.html', '/register', '/register.html',
    '/terms', '/terms.html', '/privacy', '/privacy.html',
    '/onboarding', '/onboarding.html',
    '/api/auth/login', '/api/auth/register', '/api/auth/logout', '/api/health',
    '/css/', '/js/', '/images/'
]


def is_public_route(path):
    """Check if the route is public (no auth required)"""
    for route in PUBLIC_ROUTES:
        if path.startswith(route) or path == route:
            return True
    return False

# Initialize components
data_processor = get_processor()
recommendation_engine = get_engine()

# Load data on startup
data_processor.load_mutual_fund_data()


# ============== Static File Routes ==============

@app.after_request
def add_header(response):
    """Add headers to prevent caching during development"""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.before_request
def check_authentication():
    """Middleware to check if user is authenticated for protected routes"""
    path = request.path

    # Allow public routes without authentication
    if is_public_route(path):
        return None

    # Check if user is authenticated
    user = get_current_user()

    if user is None:
        # For API routes, return 401 JSON response
        if path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'Authentication required. Please login.',
                'redirect': '/login'
            }), 401

        # For page requests, redirect to login
        from flask import redirect
        return redirect('/login')

    # Store user in request context for later use
    request.current_user = user
    return None

@app.route('/')
def serve_frontend():
    """Serve the main frontend page"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/login')
@app.route('/login.html')
def serve_login():
    """Serve the login page"""
    return send_from_directory(app.static_folder, 'login.html')


@app.route('/register')
@app.route('/register.html')
def serve_register():
    """Serve the registration page"""
    return send_from_directory(app.static_folder, 'register.html')


@app.route('/terms')
@app.route('/terms.html')
def serve_terms():
    """Serve the Terms of Service page"""
    return send_from_directory(app.static_folder, 'terms.html')


@app.route('/privacy')
@app.route('/privacy.html')
def serve_privacy():
    """Serve the Privacy Policy page"""
    return send_from_directory(app.static_folder, 'privacy.html')


@app.route('/css/<path:filename>')
def serve_css(filename):
    """Serve CSS files"""
    return send_from_directory(os.path.join(app.static_folder, 'css'), filename)


@app.route('/js/<path:filename>')
def serve_js(filename):
    """Serve JavaScript files"""
    return send_from_directory(os.path.join(app.static_folder, 'js'), filename)


@app.route('/images/<path:filename>')
def serve_images(filename):
    """Serve image files"""
    return send_from_directory(os.path.join(app.static_folder, 'images'), filename)


@app.route('/pages/<path:filename>')
def serve_pages(filename):
    """Serve pages from the pages subdirectory"""
    return send_from_directory(os.path.join(app.static_folder, 'pages'), filename)


# ============== API Routes ==============

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'FIMFP - Federal Indian Mutual Fund Portal',
        'version': '1.0.0',
        'mongodb': 'connected' if MONGODB_AVAILABLE else 'unavailable'
    })


# -------------- Authentication Endpoints --------------

@app.route('/api/auth/register', methods=['POST'])
def register_user():
    """Register a new user"""
    if not MONGODB_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Database service unavailable. Please try again later.'
        }), 503

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Request body required'}), 400

    # Required fields
    required = ['email', 'password', 'firstName', 'lastName', 'mobile']
    for field in required:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'{field} is required'}), 400

    # Validate email format
    email = data['email'].lower().strip()
    if '@' not in email or '.' not in email:
        return jsonify({'success': False, 'error': 'Invalid email format'}), 400

    # Validate password strength
    password = data['password']
    if len(password) < 8:
        return jsonify({'success': False, 'error': 'Password must be at least 8 characters'}), 400

    try:
        # Create user document
        user_doc = {
            'email': email,
            'password': hash_password(password),
            'firstName': data['firstName'].strip(),
            'lastName': data['lastName'].strip(),
            'mobile': data['mobile'].strip(),
            'panCard': data.get('panCard', '').upper().strip(),
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow(),
            'isActive': True,
            'isVerified': False
        }

        # Insert into MongoDB
        result = users_collection.insert_one(user_doc)

        return jsonify({
            'success': True,
            'message': 'Registration successful! Please login to continue.',
            'userId': str(result.inserted_id)
        })

    except DuplicateKeyError:
        return jsonify({
            'success': False,
            'error': 'An account with this email already exists. Please login or use a different email.'
        }), 409
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({
            'success': False,
            'error': 'Registration failed. Please try again later.'
        }), 500


@app.route('/api/auth/login', methods=['POST'])
def login_user():
    """Authenticate user and return token"""
    if not MONGODB_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Database service unavailable. Please try again later.'
        }), 503

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Request body required'}), 400

    email = data.get('email', '').lower().strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password are required'}), 400

    try:
        # Find user by email
        user = users_collection.find_one({'email': email})

        if not user:
            return jsonify({'success': False, 'error': 'Invalid email or password'}), 401

        # Verify password
        if not verify_password(password, user['password']):
            return jsonify({'success': False, 'error': 'Invalid email or password'}), 401

        # Check if user is active
        if not user.get('isActive', True):
            return jsonify({'success': False, 'error': 'Account is deactivated. Contact support.'}), 403

        # Generate session token
        token = generate_token()

        # Store session in MongoDB
        sessions_collection.insert_one({
            'token': token,
            'userId': user['_id'],
            'email': user['email'],
            'createdAt': datetime.utcnow()
        })

        # Update last login
        users_collection.update_one(
            {'_id': user['_id']},
            {'$set': {'lastLogin': datetime.utcnow()}}
        )

        # Create response with cookie
        from flask import make_response
        response = make_response(jsonify({
            'success': True,
            'message': 'Login successful!',
            'token': token,
            'user': {
                'email': user['email'],
                'firstName': user['firstName'],
                'lastName': user['lastName'],
                'fullName': f"{user['firstName']} {user['lastName']}"
            }
        }))

        # Set auth cookie (expires in 24 hours)
        response.set_cookie('auth_token', token, max_age=86400, httponly=True, samesite='Lax')

        return response

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({
            'success': False,
            'error': 'Login failed. Please try again later.'
        }), 500


@app.route('/api/auth/logout', methods=['POST'])
def logout_user():
    """Logout user and invalidate session"""
    token = None

    # Get token from header or cookie
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]
    else:
        token = request.cookies.get('auth_token')

    if token and MONGODB_AVAILABLE:
        try:
            # Delete session from MongoDB
            sessions_collection.delete_one({'token': token})
        except:
            pass

    # Create response and clear cookie
    from flask import make_response
    response = make_response(jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }))
    response.set_cookie('auth_token', '', expires=0)

    return response


@app.route('/api/auth/me')
def get_current_user_info():
    """Get current authenticated user info"""
    user = get_current_user()

    if not user:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401

    return jsonify({
        'success': True,
        'user': {
            'email': user['email'],
            'firstName': user['firstName'],
            'lastName': user['lastName'],
            'fullName': f"{user['firstName']} {user['lastName']}"
        }
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


@app.route('/api/fund/<int:fund_id>/history')
def get_fund_history(fund_id):
    """Get historical NAV data for charts with period filtering"""
    period = request.args.get('period', '1Y').upper()

    # Validate period
    valid_periods = ['1M', '3M', '6M', '1Y', '3Y', '5Y', 'MAX']
    if period not in valid_periods:
        period = '1Y'

    history = data_processor.get_historical_nav(fund_id, period)

    if 'error' in history:
        return jsonify({
            'success': False,
            'error': history['error']
        }), 404

    return jsonify({
        'success': True,
        'data': history
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

def parse_profile_value(value, value_type='general'):
    """Convert string profile values to numeric equivalents"""
    if value is None:
        return None

    # If already a number, return it
    if isinstance(value, (int, float)):
        return value

    # Try to parse as number first
    try:
        return float(value)
    except (ValueError, TypeError):
        pass

    # Convert string labels to numbers
    value_str = str(value).lower().strip()

    if value_type == 'income':
        # Income in lakhs
        mapping = {'low': 5, 'medium': 15, 'high': 30, 'very_high': 50}
        return mapping.get(value_str, 10)
    elif value_type == 'horizon':
        # Years
        mapping = {'short': 2, 'medium': 5, 'long': 8, 'very_long': 15}
        return mapping.get(value_str, 5)
    elif value_type == 'loss_tolerance':
        # Scale 1-5
        mapping = {'very_low': 1, 'low': 2, 'medium': 3, 'high': 4, 'very_high': 5}
        return mapping.get(value_str, 3)
    elif value_type == 'experience':
        # Scale 1-5
        mapping = {'none': 1, 'beginner': 2, 'intermediate': 3, 'advanced': 4, 'expert': 5}
        return mapping.get(value_str, 3)
    else:
        # Default mapping
        mapping = {'low': 2, 'medium': 5, 'high': 8}
        return mapping.get(value_str, 5)


@app.route('/api/recommend', methods=['GET', 'POST'])
def get_recommendations():
    """Get AI-powered fund recommendations"""
    if request.method == 'POST':
        data = request.get_json() or {}
    else:
        data = request.args.to_dict()

    # Parse risk profile parameters with string-to-number conversion
    risk_profile = None
    if any(k in data for k in ['age', 'income', 'horizon', 'loss_tolerance', 'experience']):
        risk_profile = RiskProfiler.calculate_risk_score(
            age=int(parse_profile_value(data.get('age', 35)) or 35),
            income=float(parse_profile_value(data.get('income', 10), 'income') or 10),
            investment_horizon=int(parse_profile_value(data.get('horizon', 5), 'horizon') or 5),
            loss_tolerance=int(parse_profile_value(data.get('loss_tolerance', 3), 'loss_tolerance') or 3),
            investment_experience=int(parse_profile_value(data.get('experience', 3), 'experience') or 3)
        )

    # Get recommendations
    investment_amount = float(data.get('investment', 100000))
    horizon = int(parse_profile_value(data.get('horizon', 5), 'horizon') or 5)
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


# -------------- User Profile & Onboarding Endpoints --------------

@app.route('/onboarding')
@app.route('/onboarding.html')
def serve_onboarding():
    """Serve the onboarding wizard page"""
    return send_from_directory(app.static_folder, 'onboarding.html')


@app.route('/profile')
@app.route('/profile.html')
def serve_profile():
    """Serve the user profile page"""
    return send_from_directory(app.static_folder, 'profile.html')


@app.route('/api/user/onboarding', methods=['POST'])
def save_onboarding():
    """Save user onboarding data (investment profile, broker, MF preferences)"""
    if not MONGODB_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Database service unavailable'
        }), 503

    user = get_current_user()
    if not user:
        return jsonify({
            'success': False,
            'error': 'Authentication required'
        }), 401

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Request body required'}), 400

    try:
        update_data = {
            'updatedAt': datetime.utcnow()
        }

        # Investment profile
        if 'investmentProfile' in data:
            update_data['investmentProfile'] = {
                'age': data['investmentProfile'].get('age'),
                'annualIncome': data['investmentProfile'].get('annualIncome'),
                'investmentExperience': data['investmentProfile'].get('investmentExperience', 'beginner'),
                'riskTolerance': data['investmentProfile'].get('riskTolerance', 3)
            }

        # Broker information
        if 'broker' in data:
            update_data['broker'] = {
                'name': data['broker'].get('name'),
                'demat': data['broker'].get('demat')
            }

        # MF Preferences
        if 'mfPreferences' in data:
            update_data['mfPreferences'] = {
                'investmentGoal': data['mfPreferences'].get('investmentGoal', 'wealth_creation'),
                'preferredCategories': data['mfPreferences'].get('preferredCategories', []),
                'investmentHorizon': data['mfPreferences'].get('investmentHorizon', 5),
                'monthlySIPAmount': data['mfPreferences'].get('monthlySIPAmount', 5000)
            }

        # Mark onboarding as complete
        if data.get('onboardingCompleted'):
            update_data['onboardingCompleted'] = True

        # Update user document
        users_collection.update_one(
            {'_id': user['_id']},
            {'$set': update_data}
        )

        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        })

    except Exception as e:
        print(f"Onboarding save error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to save profile'
        }), 500


@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    """Get user profile with all preferences"""
    if not MONGODB_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Database service unavailable'
        }), 503

    user = get_current_user()
    if not user:
        return jsonify({
            'success': False,
            'error': 'Authentication required'
        }), 401

    # Build profile response (exclude sensitive data)
    profile = {
        'firstName': user.get('firstName', ''),
        'lastName': user.get('lastName', ''),
        'email': user.get('email', ''),
        'mobile': user.get('mobile', ''),
        'panCard': user.get('panCard', ''),
        'createdAt': user.get('createdAt').isoformat() if user.get('createdAt') else None,
        'investmentProfile': user.get('investmentProfile', {}),
        'broker': user.get('broker', {}),
        'mfPreferences': user.get('mfPreferences', {}),
        'onboardingCompleted': user.get('onboardingCompleted', False)
    }

    return jsonify({
        'success': True,
        'data': profile
    })


@app.route('/api/user/profile', methods=['PUT'])
def update_user_profile():
    """Update user profile"""
    if not MONGODB_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Database service unavailable'
        }), 503

    user = get_current_user()
    if not user:
        return jsonify({
            'success': False,
            'error': 'Authentication required'
        }), 401

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Request body required'}), 400

    try:
        update_data = {
            'updatedAt': datetime.utcnow()
        }

        # Personal fields (direct update)
        allowed_fields = ['firstName', 'lastName', 'mobile', 'panCard']
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field].strip() if isinstance(data[field], str) else data[field]

        # Nested objects (merge with existing)
        if 'investmentProfile' in data:
            existing = user.get('investmentProfile', {})
            existing.update(data['investmentProfile'])
            update_data['investmentProfile'] = existing

        if 'broker' in data:
            existing = user.get('broker', {})
            existing.update(data['broker'])
            update_data['broker'] = existing

        if 'mfPreferences' in data:
            existing = user.get('mfPreferences', {})
            existing.update(data['mfPreferences'])
            update_data['mfPreferences'] = existing

        # Update user document
        users_collection.update_one(
            {'_id': user['_id']},
            {'$set': update_data}
        )

        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        })

    except Exception as e:
        print(f"Profile update error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update profile'
        }), 500


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
