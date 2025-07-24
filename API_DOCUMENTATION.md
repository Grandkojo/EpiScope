# Health Dashboard Analytics API Documentation

This document provides comprehensive documentation for the Health Dashboard Analytics APIs, including analytics data, time series forecasting, and AI insights.

## Base URL
```
http://localhost:8000/api/
```

## Authentication
Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## 1. Analytics Dashboard APIs

### 1.1 Dashboard Overview
**GET** `/analytics/overview/`

Returns comprehensive overview statistics for the health dashboard.

**Response:**
```json
{
  "total_cases": {
    "diabetes": 1026,
    "malaria": 1748
  },
  "localities": {
    "diabetes": 45,
    "malaria": 52
  },
  "age_distribution": {
    "diabetes": {
      "0-18": 15,
      "19-35": 89,
      "36-60": 456,
      "60+": 466
    },
    "malaria": {
      "0-18": 234,
      "19-35": 567,
      "36-60": 678,
      "60+": 269
    }
  },
  "sex_distribution": {
    "diabetes": {
      "Male": 234,
      "Female": 792
    },
    "malaria": {
      "Male": 456,
      "Female": 1292
    }
  }
}
```

### 1.2 Principal Diagnoses
**GET** `/analytics/principal-diagnoses/`

Returns top principal diagnoses with counts.

**Query Parameters:**
- `disease` (optional): Filter by disease ('diabetes' or 'malaria')

**Response:**
```json
{
  "diabetes": [
    {
      "code": "E11.9",
      "count": 234,
      "description": "Non-insulin-dependent diabetes mellitus: Without complications"
    },
    {
      "code": "E08.40",
      "count": 156,
      "description": "Diabetes mellitus due to underlying condition with diabetic neuropathy, unspecified"
    }
  ],
  "malaria": [
    {
      "code": "B50.9",
      "count": 1456,
      "description": "Plasmodium falciparum malaria, unspecified"
    }
  ]
}
```

### 1.3 Additional Diagnoses
**GET** `/analytics/additional-diagnoses/`

Returns top additional diagnoses with counts.

**Query Parameters:**
- `disease` (optional): Filter by disease ('diabetes' or 'malaria')

**Response:**
```json
{
  "diabetes": [
    {
      "code": "I10",
      "count": 89,
      "description": "Essential (primary) hypertension"
    }
  ],
  "malaria": [
    {
      "code": "N39.0",
      "count": 67,
      "description": "Urinary tract infection, site not specified"
    }
  ]
}
```

### 1.4 NHIA Status
**GET** `/analytics/nhia-status/`

Returns NHIA (National Health Insurance Authority) status distribution.

**Response:**
```json
{
  "diabetes": {
    "Yes": 892,
    "No": 134
  },
  "malaria": {
    "Yes": 1234,
    "No": 514
  }
}
```

### 1.5 Pregnancy Status
**GET** `/analytics/pregnancy-status/`

Returns pregnancy status distribution.

**Response:**
```json
{
  "diabetes": {
    "Yes": 23,
    "No": 1003
  },
  "malaria": {
    "Yes": 45,
    "No": 1703
  }
}
```

### 1.6 Disease Hotspots
**GET** `/analytics/hotspots/`

Returns disease hotspots by locality.

**Query Parameters:**
- `disease` (optional): Filter by disease ('diabetes' or 'malaria')

**Response:**
```json
{
  "diabetes": [
    {
      "locality": "MADINA-NEW RD",
      "cases": 45
    },
    {
      "locality": "GBAWE, TELECOM",
      "cases": 38
    }
  ],
  "malaria": [
    {
      "locality": "KWASHIEMAN",
      "cases": 67
    },
    {
      "locality": "KASOA",
      "cases": 54
    }
  ]
}
```

### 1.7 Disease Comparison
**GET** `/analytics/disease-comparison/`

Compares two diseases.

**Query Parameters:**
- `disease1` (default: 'diabetes'): First disease to compare
- `disease2` (default: 'malaria'): Second disease to compare

**Response:**
```json
{
  "disease1": {
    "name": "diabetes",
    "total_cases": 1026,
    "localities": 45,
    "avg_age": 58.3,
    "sex_distribution": {
      "Male": 234,
      "Female": 792
    }
  },
  "disease2": {
    "name": "malaria",
    "total_cases": 1748,
    "localities": 52,
    "avg_age": 32.1,
    "sex_distribution": {
      "Male": 456,
      "Female": 1292
    }
  }
}
```

### 1.8 Trends by Locality
**GET** `/analytics/trends/`

Returns trends by locality over time.

**Query Parameters:**
- `disease` (default: 'diabetes'): Disease to analyze
- `time_range` (default: '3M'): Time range for analysis

**Response:**
```json
{
  "labels": ["2022-03", "2022-04", "2022-05"],
  "datasets": [
    {
      "label": "MADINA-NEW RD",
      "data": [12, 15, 18]
    },
    {
      "label": "GBAWE, TELECOM",
      "data": [8, 10, 12]
    }
  ]
}
```

## 2. Time Series Forecasting APIs

### 2.1 Basic Forecast
**GET** `/forecast/`

Returns time series forecast for disease data.

**Query Parameters:**
- `disease` (default: 'diabetes'): Disease to forecast
- `months` (default: 3): Number of months to forecast (3, 6, 9, or 12)
- `locality` (optional): Specific locality to forecast

**Response:**
```json
{
  "historical": [
    {
      "date": "2022-03",
      "cases": 45
    },
    {
      "date": "2022-04",
      "cases": 52
    }
  ],
  "forecast": [
    {
      "date": "2022-05",
      "cases": 58,
      "lower_bound": 52,
      "upper_bound": 64
    },
    {
      "date": "2022-06",
      "cases": 62,
      "lower_bound": 56,
      "upper_bound": 68
    }
  ],
  "confidence_intervals": {
    "lower": [52, 56],
    "upper": [64, 68]
  },
  "metadata": {
    "disease": "diabetes",
    "forecast_months": 3,
    "locality": "MADINA-NEW RD",
    "last_historical_date": "2022-04",
    "forecast_start_date": "2022-05"
  }
}
```

### 2.2 Multi-Locality Forecast
**GET** `/forecast/multi-locality/`

Returns forecasts for multiple localities.

**Query Parameters:**
- `disease` (default: 'diabetes'): Disease to forecast
- `months` (default: 3): Number of months to forecast (3, 6, 9, or 12)
- `top_n` (default: 5): Number of top localities to include

**Response:**
```json
{
  "localities": {
    "MADINA-NEW RD": {
      "historical": [...],
      "forecast": [...],
      "confidence_intervals": {...}
    },
    "GBAWE, TELECOM": {
      "historical": [...],
      "forecast": [...],
      "confidence_intervals": {...}
    }
  },
  "metadata": {
    "disease": "diabetes",
    "forecast_months": 3,
    "top_n": 5
  }
}
```

### 2.3 Seasonal Forecast
**GET** `/forecast/seasonal/`

Returns seasonal forecast with trend and seasonality components.

**Query Parameters:**
- `disease` (default: 'diabetes'): Disease to forecast
- `months` (default: 12): Number of months to forecast

**Response:**
```json
{
  "historical": [...],
  "forecast": [
    {
      "date": "2022-05",
      "cases": 58,
      "trend_component": 55,
      "seasonal_component": 61
    }
  ],
  "seasonal_patterns": {
    "1": 45,
    "2": 42,
    "3": 48
  },
  "trend_slope": 2.3,
  "metadata": {
    "forecast_months": 12,
    "last_historical_date": "2022-04",
    "forecast_start_date": "2022-05"
  }
}
```

### 2.4 Forecast Accuracy Metrics
**GET** `/forecast/accuracy/`

Returns forecast accuracy metrics.

**Query Parameters:**
- `disease` (default: 'diabetes'): Disease to analyze
- `test_months` (default: 3): Number of months to use for testing

**Response:**
```json
{
  "mae": 3.2,
  "mape": 8.5,
  "rmse": 4.1,
  "test_period": 3,
  "actual_values": [45, 52, 48],
  "predicted_values": [42, 55, 51]
}
```

## 3. AI Insights APIs

### 3.1 AI Insights
**GET** `/ai/insights/`

Returns AI-powered insights for health data.

**Query Parameters:**
- `disease` (optional): Filter by disease ('diabetes' or 'malaria')
- `type` (default: 'general'): Type of insights ('general', 'trends', 'anomalies', 'predictions', 'correlations')

**Response:**
```json
{
  "insights": [
    {
      "type": "disease_overview",
      "disease": "diabetes",
      "title": "Diabetes Cases Overview",
      "description": "Total of 1026 diabetes cases across 45 localities",
      "key_findings": [
        "Average age: 58.3 years",
        "NHIA coverage: 892 patients",
        "Pregnancy cases: 23 patients"
      ],
      "severity": "medium"
    }
  ],
  "metadata": {
    "disease": "diabetes",
    "insight_type": "general",
    "generated_at": "2024-01-15T10:30:00Z"
  }
}
```

### 3.2 AI Q&A
**POST** `/ai/qa/`

Returns AI-powered Q&A response about health data.

**Request Body:**
```json
{
  "question": "What is the trend in diabetes cases over the last year?",
  "context": "Optional context data"
}
```

**Response:**
```json
{
  "question": "What is the trend in diabetes cases over the last year?",
  "answer": "Based on the health data analysis, diabetes cases have shown a steady increase of approximately 15% over the last year...",
  "generated_at": "2024-01-15T10:30:00Z"
}
```

### 3.3 Anomaly Detection
**GET** `/ai/anomalies/`

Detects anomalies in health data using AI.

**Query Parameters:**
- `disease` (optional): Filter by disease ('diabetes' or 'malaria')

**Response:**
```json
{
  "anomalies": [
    {
      "type": "volume_anomaly",
      "disease": "diabetes",
      "description": "High case volume: 1026 cases",
      "severity": "high"
    }
  ],
  "ai_explanation": "The detected anomalies indicate unusual patterns in the health data that may require attention...",
  "metadata": {
    "disease": "diabetes",
    "detection_method": "statistical + AI",
    "generated_at": "2024-01-15T10:30:00Z"
  }
}
```

## 4. Error Responses

All APIs return consistent error responses:

```json
{
  "error": "Error message description"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `401`: Unauthorized (missing or invalid token)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found
- `500`: Internal Server Error

## 5. Rate Limiting

APIs are subject to rate limiting:
- 100 requests per minute per user
- 1000 requests per hour per user

## 6. Data Sources

The APIs use the following data sources:
- `src/artifacts/csv/health_data_eams_diabetes.csv`
- `src/artifacts/csv/health_data_eams_malaria.csv`
- `src/artifacts/time_series/health_data_eams_diabetes_time_stamped.csv`
- `src/artifacts/time_series/health_data_eams_malaria_time_stamped.csv`

## 7. Configuration

### Gemini AI Integration
To enable AI insights, set the following environment variable:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### Time Series Forecasting
The forecasting models use:
- Linear regression for trend analysis
- Seasonal decomposition for seasonal patterns
- Confidence intervals for uncertainty quantification

## 8. Examples

### Frontend Integration Example

```javascript
// Get dashboard overview
const response = await fetch('/api/analytics/overview/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
const data = await response.json();

// Get 6-month forecast for diabetes
const forecastResponse = await fetch('/api/forecast/?disease=diabetes&months=6', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
const forecastData = await forecastResponse.json();

// Get AI insights
const insightsResponse = await fetch('/api/ai/insights/?type=trends', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
const insightsData = await insightsResponse.json();
```

This comprehensive API documentation covers all the new endpoints created for the Health Dashboard Analytics system, providing detailed information about request/response formats, parameters, and usage examples. 