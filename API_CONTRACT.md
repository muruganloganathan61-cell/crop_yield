# API Contract Documentation

## Overview
This document defines the complete API contract for the Crop Yield Prediction System.

## Base URL
```
http://localhost:5000/api
```

## Authentication
Currently, no authentication is required. (Consider adding API keys for production)

## Content Type
All requests and responses use `application/json`.

## Response Format

### Success Response
```json
{
  "success": true,
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "errors": { "field": "specific error" }
}
```

## HTTP Status Codes
- **200 OK**: Request succeeded
- **400 Bad Request**: Invalid input or validation error
- **404 Not Found**: Endpoint does not exist
- **405 Method Not Allowed**: Wrong HTTP method
- **500 Internal Server Error**: Server error

---

## Endpoints

### 1. GET /api/health
Health check endpoint to verify API is running.

**Request:**
```
GET /api/health HTTP/1.1
Host: localhost:5000
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-12T10:30:00.000000",
  "models_loaded": true
}
```

**Use Case:** Monitor API availability

---

### 2. GET /api/data-ranges
Retrieve valid data ranges and options for frontend form validation.

**Request:**
```
GET /api/data-ranges HTTP/1.1
Host: localhost:5000
```

**Response (200 OK):**
```json
{
  "soil_types": [
    "Loamy",
    "Sandy", 
    "Clay",
    "Silt"
  ],
  "crop_types": [
    "Rice",
    "Wheat",
    "Corn",
    "Soybean",
    "Barley"
  ],
  "ranges": {
    "nitrogen": {
      "min": 0,
      "max": 150,
      "unit": "mg/kg"
    },
    "phosphorus": {
      "min": 0,
      "max": 100,
      "unit": "mg/kg"
    },
    "potassium": {
      "min": 0,
      "max": 100,
      "unit": "mg/kg"
    },
    "ph": {
      "min": 4,
      "max": 9,
      "unit": "pH"
    },
    "moisture": {
      "min": 0,
      "max": 100,
      "unit": "%"
    },
    "temperature": {
      "min": -10,
      "max": 50,
      "unit": "°C"
    },
    "rainfall": {
      "min": 0,
      "max": 400,
      "unit": "mm"
    },
    "humidity": {
      "min": 0,
      "max": 100,
      "unit": "%"
    }
  }
}
```

**Use Case:** Populate frontend form dropdowns and validate input ranges

---

### 3. POST /api/predict-yield
Predict crop yield based on soil, weather, and crop data.

**Request:**
```
POST /api/predict-yield HTTP/1.1
Host: localhost:5000
Content-Type: application/json

{
  "nitrogen": 60,
  "phosphorus": 35,
  "potassium": 35,
  "ph": 7.0,
  "moisture": 65,
  "temperature": 28,
  "rainfall": 200,
  "humidity": 75,
  "soil_type": "Loamy",
  "crop_type": "Rice"
}
```

**Request Body Parameters:**

| Field | Type | Range | Required | Description |
|-------|------|-------|----------|-------------|
| nitrogen | float | 0-150 | Yes | Nitrogen level in mg/kg |
| phosphorus | float | 0-100 | Yes | Phosphorus level in mg/kg |
| potassium | float | 0-100 | Yes | Potassium level in mg/kg |
| ph | float | 4-9 | Yes | Soil pH value |
| moisture | float | 0-100 | Yes | Soil moisture percentage |
| temperature | float | -10 to 50 | Yes | Average temperature in °C |
| rainfall | float | 0-400 | Yes | Expected rainfall in mm |
| humidity | float | 0-100 | Yes | Relative humidity percentage |
| soil_type | string | Loamy, Sandy, Clay, Silt | Yes | Type of soil |
| crop_type | string | Rice, Wheat, Corn, Soybean, Barley | Yes | Crop to predict |

**Response (200 OK):**
```json
{
  "success": true,
  "prediction": {
    "yield_estimate": 5642.34,
    "yield_unit": "kg/hectare",
    "confidence": "Based on Random Forest regression model",
    "crop_type": "Rice"
  },
  "soil_analysis": [
    {
      "nutrient": "Nitrogen",
      "level": "Optimal",
      "value": 60,
      "recommendation": "Nitrogen levels are adequate"
    },
    {
      "nutrient": "Phosphorus",
      "level": "Optimal",
      "value": 35,
      "recommendation": "Phosphorus levels are good"
    },
    {
      "nutrient": "Potassium",
      "level": "Optimal",
      "value": 35,
      "recommendation": "Potassium levels are adequate"
    },
    {
      "nutrient": "Soil pH",
      "level": "Optimal",
      "value": 7.0,
      "recommendation": "pH is optimal for most crops"
    },
    {
      "nutrient": "Soil Moisture",
      "level": "Optimal",
      "value": 65,
      "recommendation": "Moisture levels are optimal"
    }
  ],
  "weather_analysis": {
    "warnings": [],
    "temperature": 28,
    "rainfall": 200,
    "humidity": 75
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "errors": {
    "nitrogen": "Value must be between 0 and 150",
    "ph": "Missing required field: ph"
  }
}
```

**Use Case:** Get yield predictions and soil health assessment

---

### 4. POST /api/recommend
Get seed and fertilizer recommendations based on conditions.

**Request:**
```
POST /api/recommend HTTP/1.1
Host: localhost:5000
Content-Type: application/json

{
  "nitrogen": 60,
  "phosphorus": 35,
  "potassium": 35,
  "ph": 7.0,
  "moisture": 65,
  "temperature": 28,
  "rainfall": 200,
  "humidity": 75,
  "soil_type": "Loamy",
  "crop_type": "Rice"
}
```

**Request Body Parameters:** Same as `/predict-yield`

**Response (200 OK):**
```json
{
  "success": true,
  "recommendations": {
    "seed": {
      "recommended_crop": "Rice",
      "confidence": 87.5,
      "reason": "Optimal for your soil (pH: 7.0) and weather conditions (Temp: 28°C, Rainfall: 200mm)"
    },
    "fertilizer": {
      "recommended_type": "NPK 15-15-15",
      "confidence": 92.3,
      "details": {
        "quantity": "100-150 kg/hectare",
        "application_time": "Pre-planting & Side dressing",
        "description": "Balanced NPK; versatile for most crops"
      },
      "soil_type": "Loamy",
      "reason": "Selected based on soil NPK levels and pH (7.0)"
    }
  },
  "input_summary": {
    "crop_type": "Rice",
    "soil_type": "Loamy",
    "region": "Not specified"
  }
}
```

**Possible Fertilizer Types:**
- NPK 10-26-26: High phosphorus and potassium
- NPK 12-32-16: Balanced with extra phosphorus
- NPK 15-15-15: Balanced NPK
- NPK 20-20-0: Nitrogen-focused
- Organic Compost: Sustainable option

**Use Case:** Get seed variety and fertilizer recommendations

---

## Example Workflows

### Workflow 1: Complete Prediction + Recommendations

```javascript
// Step 1: Get data ranges (optional, for validation)
const ranges = await fetch('http://localhost:5000/api/data-ranges')
  .then(r => r.json());

// Step 2: Validate user input against ranges

// Step 3: Make prediction request
const prediction = await fetch('http://localhost:5000/api/predict-yield', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(userData)
}).then(r => r.json());

// Step 4: Get recommendations
const recommendations = await fetch('http://localhost:5000/api/recommend', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(userData)
}).then(r => r.json());

// Step 5: Display results to user
displayResults(prediction, recommendations);
```

### Workflow 2: Health Check

```bash
curl http://localhost:5000/api/health
```

### Workflow 3: Testing with cURL

```bash
# Health check
curl -X GET http://localhost:5000/api/health

# Get data ranges
curl -X GET http://localhost:5000/api/data-ranges

# Predict yield
curl -X POST http://localhost:5000/api/predict-yield \
  -H "Content-Type: application/json" \
  -d '{
    "nitrogen": 60,
    "phosphorus": 35,
    "potassium": 35,
    "ph": 7.0,
    "moisture": 65,
    "temperature": 28,
    "rainfall": 200,
    "humidity": 75,
    "soil_type": "Loamy",
    "crop_type": "Rice"
  }'

# Get recommendations
curl -X POST http://localhost:5000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "nitrogen": 60,
    "phosphorus": 35,
    "potassium": 35,
    "ph": 7.0,
    "moisture": 65,
    "temperature": 28,
    "rainfall": 200,
    "humidity": 75,
    "soil_type": "Loamy",
    "crop_type": "Rice"
  }'
```

---

## Rate Limiting

Currently, no rate limiting is implemented. For production, consider adding:
- 100 requests per minute per IP
- 1000 requests per hour per user

---

## Versioning

**Current Version:** 1.0.0

Future versions might include:
- `/api/v2/predict-yield` with additional parameters
- Breaking changes will increment major version

---

## CORS Policy

**Allowed Origins:** *
**Allowed Methods:** GET, POST, OPTIONS
**Allowed Headers:** Content-Type

---

## Error Codes Reference

| Code | Message | Cause |
|------|---------|-------|
| 400 | Missing required field | Incomplete request body |
| 400 | Invalid value | Value out of range |
| 404 | Endpoint not found | Wrong URL path |
| 405 | Method not allowed | Wrong HTTP method |
| 500 | Models not loaded | ML models not trained/found |
| 500 | Prediction failed | Unexpected server error |

---

## Performance Considerations

- **Response Time:** < 500ms typically
- **Payload Size:** Request ~500B, Response ~2KB
- **Concurrent Users:** Limited by server resources
- **Model Loading:** ~2-3 seconds on startup

---

## Security Notes

⚠️ **Development Mode Only:**
- No HTTPS
- No authentication
- CORS allows all origins
- Debug mode enabled

**For Production:**
- Enable HTTPS
- Add API key authentication
- Restrict CORS origins
- Disable debug mode
- Implement rate limiting
- Add input sanitization
- Use HTTPS only

---

## Testing

**Recommended Testing Tools:**
- Postman (GUI)
- curl (Command line)
- Thunder Client (VS Code)
- Insomnia (Advanced testing)

**Test Cases:**
```
1. Valid input → Complete prediction
2. Missing field → 400 error
3. Out of range value → 400 error
4. Health endpoint → 200 response
5. Data ranges endpoint → Valid options
```

---

**Last Updated:** January 2024  
**API Version:** 1.0.0
