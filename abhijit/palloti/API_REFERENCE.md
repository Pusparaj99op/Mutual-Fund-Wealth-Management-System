# API Reference - Federal Wealth Management System

## Base URL
```
http://localhost:8000
```

## Documentation
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Endpoints

### 1. Health Check

#### Endpoint
```
GET /health
```

#### Description
Check API server status and version

#### Response (200 OK)
```json
{
  "status": "healthy",
  "timestamp": "2024-12-15T10:30:45.123456",
  "version": "1.0.0"
}
```

---

### 2. Get Fund Recommendations

#### Endpoint
```
POST /recommend_funds
```

#### Description
Get personalized mutual fund recommendations based on investor profile

#### Request Body
```json
{
  "investment_amount": 100000,
  "investment_type": "sip",
  "tenure_months": 60,
  "category": null,
  "risk_tolerance": 4
}
```

#### Parameters

| Parameter | Type | Required | Default | Range | Description |
|-----------|------|----------|---------|-------|-------------|
| investment_amount | float | Yes | - | > 0 | Investment amount in INR |
| investment_type | string | No | "sip" | sip, lumpsum | Type of investment |
| tenure_months | integer | No | 60 | 6-360 | Investment tenure in months |
| category | string | No | null | See below | Fund category |
| risk_tolerance | integer | No | 3 | 1-6 | Risk tolerance level |

#### Category Options
- `null` - All categories
- `"Equity"` - Equity funds
- `"Debt"` - Debt/Bond funds
- `"Hybrid"` - Balanced funds
- `"Solution Oriented"` - Goal-based funds
- `"Other"` - Precious metals, international

#### Response (200 OK)
```json
{
  "timestamp": "2024-12-15T10:30:45.123456",
  "investor_profile": {
    "investment_amount": 100000,
    "investment_type": "SIP",
    "tenure_months": 60,
    "category": "All Categories"
  },
  "recommendations": [
    {
      "scheme_id": "FUND_0045",
      "scheme_name": "HDFC AMC Large Cap Fund 45",
      "amc_name": "HDFC AMC",
      "category": "Equity",
      "sub_category": "Large Cap",
      "rating": 4.7,
      "risk_level": 4,
      "recommendation_score": 87.5,
      "predicted_return_5yr": 14.25,
      "historical_return_5yr": 13.80,
      "sharpe_ratio": 2.15,
      "expense_ratio": 0.65,
      "min_sip": 500,
      "min_lumpsum": 5000,
      "explanation": {
        "recommendation_score": 87.5,
        "predicted_return_5yr": 14.25,
        "strengths": [
          "Excellent rating (4.7/5)",
          "Strong 5-year returns (13.8%)",
          "Superior risk-adjusted returns (Sharpe: 2.15)",
          "Low expense ratio (0.65%)"
        ],
        "weaknesses": [],
        "investment_rationale": "This fund ranks in top selections based on predicted returns..."
      }
    }
  ],
  "filtering_stats": {
    "total_funds_in_database": 150,
    "funds_after_filtering": 87,
    "recommendations_provided": 5,
    "filters_applied": {
      "investment_amount": "₹100,000",
      "investment_type": "SIP",
      "tenure_months": 60,
      "category": "All",
      "min_rating": 3.0
    }
  }
}
```

#### Error Responses

**400 Bad Request**
```json
{
  "error": "Invalid investment_amount: must be greater than 0"
}
```

**503 Service Unavailable**
```json
{
  "error": "Recommendation engine not initialized"
}
```

---

### 3. Predict Fund Returns

#### Endpoint
```
POST /predict_returns
```

#### Description
Predict future returns for a specific mutual fund

#### Request Body
```json
{
  "scheme_id": "FUND_0045",
  "investment_period_years": 5
}
```

#### Parameters

| Parameter | Type | Required | Default | Range | Description |
|-----------|------|----------|---------|-------|-------------|
| scheme_id | string | Yes | - | - | Fund scheme ID |
| investment_period_years | float | No | 5 | 0.1-30 | Prediction period |

#### Response (200 OK)
```json
{
  "scheme_id": "FUND_0045",
  "scheme_name": "HDFC AMC Large Cap Fund 45",
  "predicted_return": 14.25,
  "confidence_interval": {
    "lower": 8.45,
    "expected": 14.25,
    "upper": 20.05
  },
  "risk_metrics": {
    "volatility": 12.50,
    "beta": 0.98,
    "alpha": 2.35,
    "sharpe_ratio": 2.15,
    "sortino_ratio": 3.25,
    "risk_level": 4
  },
  "explanation": {
    "top_contributing_factors": {
      "Return (5yr)": 28.5,
      "Rating": 25.3,
      "Sharpe Ratio": 22.1,
      "Risk Adjusted": 18.2,
      "Expense Ratio": 15.8
    },
    "total_impact_score": 109.9
  }
}
```

#### Error Responses

**404 Not Found**
```json
{
  "error": "Fund FUND_0999 not found"
}
```

---

### 4. Forecast NAV (Net Asset Value)

#### Endpoint
```
POST /forecast_nav
```

#### Description
Generate NAV forecast for a fund

#### Request Body
```json
{
  "scheme_id": "FUND_0045",
  "forecast_months": 12,
  "confidence_level": 0.95
}
```

#### Parameters

| Parameter | Type | Required | Default | Range | Description |
|-----------|------|----------|---------|-------|-------------|
| scheme_id | string | Yes | - | - | Fund scheme ID |
| forecast_months | integer | No | 12 | 1-60 | Forecast horizon |
| confidence_level | float | No | 0.95 | 0.90-0.99 | Confidence level |

#### Response (200 OK)
```json
{
  "scheme_id": "FUND_0045",
  "scheme_name": "HDFC AMC Large Cap Fund 45",
  "forecast_data": [
    {
      "date": "Month 1",
      "forecasted_nav": 152.35,
      "lower_bound": 144.73,
      "upper_bound": 159.97
    },
    {
      "date": "Month 2",
      "forecasted_nav": 154.65,
      "lower_bound": 146.92,
      "upper_bound": 162.38
    },
    {
      "date": "Month 3",
      "forecasted_nav": 157.02,
      "lower_bound": 149.17,
      "upper_bound": 164.87
    }
  ],
  "confidence_level": 0.95,
  "methodology": "Exponential growth model based on historical returns"
}
```

---

### 5. Get Fund Details

#### Endpoint
```
GET /funds/{scheme_id}
```

#### Description
Get comprehensive information about a specific fund

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| scheme_id | string | Fund scheme ID (e.g., FUND_0045) |

#### Response (200 OK)
```json
{
  "scheme_id": "FUND_0045",
  "scheme_name": "HDFC AMC Large Cap Fund 45",
  "amc_name": "HDFC AMC",
  "category": "Equity",
  "sub_category": "Large Cap",
  "rating": 4.7,
  "risk_level": 4,
  "returns": {
    "return_1yr": 18.50,
    "return_3yr": 14.25,
    "return_5yr": 13.80
  },
  "metrics": {
    "sharpe_ratio": 2.15,
    "sortino_ratio": 3.25,
    "alpha": 2.35,
    "beta": 0.98,
    "std_deviation": 12.50
  },
  "investment_info": {
    "min_sip": 500,
    "min_lumpsum": 5000,
    "expense_ratio": 0.65
  },
  "other": {
    "fund_size_cr": 12500.50,
    "fund_age_years": 15,
    "nav": 150.75,
    "inception_date": "2009-06-15"
  }
}
```

#### Error Responses

**404 Not Found**
```json
{
  "error": "Fund FUND_0999 not found"
}
```

---

### 6. Compare Multiple Funds

#### Endpoint
```
POST /compare_funds
```

#### Description
Get comparative analysis of multiple funds

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| scheme_ids | string[] | Yes | List of scheme IDs |

#### Example Request
```
POST /compare_funds?scheme_ids=FUND_0045&scheme_ids=FUND_0067&scheme_ids=FUND_0089
```

#### Response (200 OK)
```json
{
  "comparison": [
    {
      "scheme_id": "FUND_0045",
      "scheme_name": "HDFC AMC Large Cap Fund 45",
      "rating": 4.7,
      "risk_level": 4,
      "return_5yr": 13.80,
      "sharpe_ratio": 2.15,
      "expense_ratio": 0.65
    },
    {
      "scheme_id": "FUND_0067",
      "scheme_name": "ICICI Prudential Large Cap 67",
      "rating": 4.5,
      "risk_level": 4,
      "return_5yr": 12.95,
      "sharpe_ratio": 2.08,
      "expense_ratio": 0.70
    }
  ],
  "timestamp": "2024-12-15T10:30:45.123456"
}
```

---

## Error Handling

All endpoints follow standard HTTP status codes:

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Request processed successfully |
| 400 | Bad Request | Invalid parameters |
| 404 | Not Found | Fund not found |
| 500 | Server Error | Internal server error |
| 503 | Unavailable | Service not initialized |

### Error Response Format
```json
{
  "error": "Error message",
  "timestamp": "2024-12-15T10:30:45.123456"
}
```

---

## Example Usage

### Using cURL

**Get Recommendations**
```bash
curl -X POST http://localhost:8000/recommend_funds \
  -H "Content-Type: application/json" \
  -d '{
    "investment_amount": 100000,
    "investment_type": "sip",
    "tenure_months": 60,
    "category": null,
    "risk_tolerance": 4
  }'
```

**Predict Returns**
```bash
curl -X POST http://localhost:8000/predict_returns \
  -H "Content-Type: application/json" \
  -d '{
    "scheme_id": "FUND_0045",
    "investment_period_years": 5
  }'
```

**Get Fund Details**
```bash
curl http://localhost:8000/funds/FUND_0045
```

### Using Python

```python
import requests

API_BASE = "http://localhost:8000"

# Get recommendations
response = requests.post(
    f"{API_BASE}/recommend_funds",
    json={
        "investment_amount": 100000,
        "investment_type": "sip",
        "tenure_months": 60
    }
)
print(response.json())

# Get fund details
response = requests.get(f"{API_BASE}/funds/FUND_0045")
print(response.json())

# Compare funds
response = requests.post(
    f"{API_BASE}/compare_funds",
    params={"scheme_ids": ["FUND_0045", "FUND_0067"]}
)
print(response.json())
```

### Using JavaScript

```javascript
const API_BASE = "http://localhost:8000";

// Get recommendations
fetch(`${API_BASE}/recommend_funds`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    investment_amount: 100000,
    investment_type: "sip",
    tenure_months: 60
  })
})
.then(res => res.json())
.then(data => console.log(data));

// Get fund details
fetch(`${API_BASE}/funds/FUND_0045`)
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## Rate Limiting

Currently, no rate limiting is implemented. For production, implement:
- Maximum requests per minute per IP
- API key validation
- Request timeout limits

---

## Authentication

Currently, the API is open (no authentication). For production, implement:
- API key validation
- JWT token authentication
- OAuth 2.0 integration

---

## Best Practices

1. **Cache Results** - Cache recommendations for 1 hour
2. **Error Handling** - Always check HTTP status codes
3. **Input Validation** - Validate all parameters client-side
4. **Rate Limiting** - Implement client-side request throttling
5. **Monitoring** - Log all API calls for analytics

---

## Support

- **Documentation**: Check /docs endpoint
- **Issues**: Review logs in console
- **FAQ**: See README.md

---

**Last Updated**: December 2024  
**API Version**: 1.0.0
