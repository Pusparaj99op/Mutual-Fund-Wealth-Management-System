# FIMFP - Federal Indian Mutual Fund Portal
## भारतीय संघीय म्यूचुअल फंड पोर्टल

![Government of India](https://img.shields.io/badge/Government%20of%20India-Initiative-orange?style=for-the-badge)
![AI Powered](https://img.shields.io/badge/AI-Powered-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-2.3+-red?style=for-the-badge)

An AI-powered mutual fund analysis and recommendation portal developed under the Digital India Programme.

## 🇮🇳 Features

### Advanced AI/ML Models
- **Monte Carlo Simulation** - 10,000 simulation paths for NAV prediction and VaR calculation
- **Black-Scholes Model** - Greeks analysis (Delta, Gamma, Theta, Vega) and risk premium assessment
- **Black-Litterman** - Portfolio optimization with market equilibrium
- **GARCH Volatility** - Time-series volatility forecasting
- **ML Predictors** - Ensemble learning with Random Forest and Gradient Boosting
- **Momentum Analysis** - Multi-timeframe momentum scoring
- **Factor Models** - 6-factor exposure analysis
- **Sentiment Analysis** - Market sentiment indicators

### Core Functionality
- 🔍 Browse 790+ SEBI-registered mutual funds
- 📊 AI-powered fund recommendations based on risk profile
- 📈 Monte Carlo predictions with confidence intervals
- ⚖️ Portfolio optimization using Black-Litterman model
- 📉 Comprehensive risk analytics and stress testing
- 🎯 Real-time fund comparison and analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Modern web browser (Chrome, Firefox, Edge)
- Linux/macOS/Windows

### Installation

1. **Clone or navigate to the Anti directory**
```bash
cd /path/to/Mutual-Fund-Wealth-Management-System/Anti
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Ensure data files are available**
The system expects mutual fund data in CSV/JSON format in the parent `data/` directory.

### Running the Application

#### Option 1: Using the startup script (Linux/macOS)
```bash
chmod +x run.sh
./run.sh
```

#### Option 2: Manual startup
```bash
cd api
python app.py
```

The application will start on **http://localhost:8009**

Open your browser and navigate to:
```
http://localhost:8009
```

## 📁 Project Structure

```
Anti/
├── frontend/              # Frontend files
│   ├── index.html        # Main HTML file
│   ├── css/
│   │   └── gov-style.css # Government design system
│   └── js/
│       ├── app.js        # Main application logic
│       └── charts.js     # Chart.js utilities
│
├── api/                  # Backend API
│   ├── app.py           # Flask server & REST endpoints
│   ├── data_processor.py # Data handling
│   ├── ml_models.py     # AI/ML model implementations
│   ├── recommendation_engine.py # Recommendation system
│   ├── models/          # Financial models
│   └── services/        # Data services
│
├── requirements.txt     # Python dependencies
├── run.sh              # Startup script
└── README.md           # This file
```

## 🔌 API Endpoints

### Fund Data
- `GET /api/funds` - List all mutual funds (with pagination/filtering)
- `GET /api/fund/<id>` - Get detailed fund information
- `GET /api/categories` - Get all fund categories
- `GET /api/top-funds` - Get top performing funds

### AI/ML Analysis
- `GET /api/predict/<id>` - Monte Carlo prediction
- `GET /api/risk-analysis/<id>` - Black-Scholes risk analysis
- `GET /api/stress-test/<id>` - Stress testing scenarios
- `POST /api/recommend` - Get AI recommendations
- `POST /api/optimize` - Portfolio optimization

### Advanced Analytics
- `GET /api/advanced/ml-predict/<id>` - ML-based return prediction
- `GET /api/advanced/momentum/<id>` - Momentum analysis
- `GET /api/advanced/factor/<id>` - Factor model analysis
- `GET /api/advanced/sentiment/<id>` - Sentiment analysis
- `GET /api/advanced/complete/<id>` - Complete AI analysis

### Market Analytics
- `GET /api/analytics/summary` - Market overview
- `GET /api/analytics/historical/<id>` - Historical performance

## 🎨 Design

The portal follows authentic Indian Government web design guidelines:
- **Tricolor Banner** - Saffron, White, and Green national colors
- **NIC Standards** - Based on National Informatics Centre guidelines
- **Accessibility** - WCAG 2.1 compliant
- **Responsive** - Mobile-first design approach

## 🔧 Configuration

### API Configuration
The frontend automatically detects whether it's being served from Flask or standalone:
- When served from Flask: Uses relative URLs
- When standalone: Connects to `http://localhost:8009`

### Environment Variables
```bash
export PORT=8009  # Set custom port (default: 8009)
```

## 📊 Data Requirements

The system expects mutual fund data in the following structure:
- CSV files with fund information (NAV, returns, risk metrics)
- JSON files for detailed fund data
- Historical NAV data for time-series analysis

Place data files in: `../data/raw/csv/` and `../data/raw/json/`

## 🧪 Testing

Test API endpoints:
```bash
# Health check
curl http://localhost:8009/api/health

# Get funds list
curl http://localhost:8009/api/funds?limit=10

# Get specific fund
curl http://localhost:8009/api/fund/1
```

## 🛡️ Disclaimer

**Important Notice:** Mutual Fund investments are subject to market risks. Read all scheme-related documents carefully before investing. Past performance is not indicative of future returns. This portal is developed for educational and informational purposes only and should not be considered as financial advice.

## 📝 License

This project is developed under the Digital India Programme by the National Informatics Centre for educational purposes.

## 🤝 Contributing

This is a government initiative portal. For queries or contributions, please contact the National Informatics Centre.

## 📧 Support

For technical support or queries:
- Visit: [india.gov.in](https://india.gov.in)
- SEBI: [sebi.gov.in](https://sebi.gov.in)
- AMFI: [amfiindia.com](https://amfiindia.com)

---

**Developed under Digital India Programme by National Informatics Centre**

🇮🇳 **Satyameva Jayate** - Truth Alone Triumphs
