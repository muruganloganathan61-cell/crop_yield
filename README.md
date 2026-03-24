display# 🌾 Crop Yield Prediction & Recommendation System

A comprehensive full-stack web application that predicts crop yield and provides intelligent agricultural recommendations using machine learning.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Model Details](#model-details)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)

---

## 🎯 Overview

This system empowers farmers and agronomists to:
- **Predict crop yield** based on soil and weather conditions
- **Get seed recommendations** optimized for their land
- **Receive fertilizer suggestions** with application rates
- **Understand soil health** with detailed analysis
- **Monitor weather risks** with intelligent warnings

The architecture separates frontend (HTML/CSS/JS), backend (Flask API), and ML services for scalability and maintainability.

---

## ✨ Features

### User Interface
- ✅ Clean, responsive web interface (mobile, tablet, desktop)
- ✅ Real-time form validation with helpful hints
- ✅ Intuitive data input for soil, weather, and crop information
- ✅ Beautiful visualization of predictions and recommendations
- ✅ Professional gradient design with smooth animations

### Predictions & Recommendations
- ✅ **Yield Prediction**: Random Forest Regressor model
- ✅ **Seed Recommendation**: Classification based on soil/weather
- ✅ **Fertilizer Recommendation**: NPK type and quantity
- ✅ **Soil Analysis**: Nutrient level assessment with suggestions
- ✅ **Weather Warnings**: Risk alerts based on conditions

### Backend API
- ✅ RESTful endpoints for predictions and recommendations
- ✅ Input validation and error handling
- ✅ CORS-enabled for frontend integration
- ✅ Health check endpoint
- ✅ Data ranges endpoint for frontend validation

### Models
- ✅ Pre-trained ML models (joblib format)
- ✅ Random Forest for yield prediction (Regression)
- ✅ Random Forest for seed selection (Classification)
- ✅ Random Forest for fertilizer type (Classification)
- ✅ Soil type label encoder

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (HTML/CSS/JS)                   │
│                  Responsive Web Interface                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Input Form | Dashboard | Results Visualization      │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/JSON
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              BACKEND (Flask REST API)                         │
│         /api/predict-yield  /api/recommend                   │
│         /api/data-ranges    /api/health                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Request Handling | Validation | Response JSON       │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│          ML LAYER (Trained Models)                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ yield_model.pkl      (Random Forest Regressor)      │  │
│  │ seed_model.pkl       (Random Forest Classifier)     │  │
│  │ fertilizer_model.pkl (Random Forest Classifier)     │  │
│  │ soil_type_encoder.pkl (LabelEncoder)                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
crop yield prediction/
├── frontend/
│   ├── index.html           # Main HTML structure
│   ├── styles.css           # Responsive CSS styling
│   ├── script.js            # Frontend logic and API calls
│   └── README.md            # Frontend documentation
│
├── backend/
│   ├── app.py               # Flask API application
│   ├── requirements.txt      # Python dependencies
│   └── README.md            # Backend documentation
│
├── ml_models/
│   ├── train_models.py      # ML model training script
│   ├── requirements.txt      # ML dependencies
│   ├── yield_model.pkl       # Trained yield prediction model
│   ├── seed_model.pkl        # Trained seed recommendation model
│   ├── fertilizer_model.pkl  # Trained fertilizer recommendation model
│   └── soil_type_encoder.pkl # Soil type label encoder
│
├── data/
│   └── [Training data files (optional)]
│
└── README.md                # This file
```

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+ (https://www.python.org/)
- pip or conda package manager
- A modern web browser (Chrome, Firefox, Safari, Edge)

### Step 1: Clone/Download the Project
```bash
cd path/to/crop\ yield\ prediction
```

### Step 2: Train ML Models

Navigate to the ML models directory and train the models:

```bash
cd ml_models
pip install -r requirements.txt
python train_models.py
```

**Expected Output:**
```
============================================================
CROP YIELD PREDICTION - MODEL TRAINING
============================================================

Training Yield Prediction Model...
Yield Model Performance:
  RMSE: XX.XX
  MAE: XX.XX
  R²: X.XXXX
✓ Yield model saved as yield_model.pkl

Training Seed Recommendation Model...
Seed Model Performance:
  Accuracy: X.XXXX
  Classes: ['Rice' 'Wheat' 'Corn' 'Soybean' 'Barley']
✓ Seed model saved as seed_model.pkl

Training Fertilizer Recommendation Model...
Fertilizer Model Performance:
  Accuracy: X.XXXX
  Classes: ['NPK 10-26-26' 'NPK 12-32-16' 'NPK 15-15-15' 'NPK 20-20-0' 'Organic Compost']
✓ Fertilizer model saved as fertilizer_model.pkl
✓ Soil type encoder saved as soil_type_encoder.pkl
```

### Step 3: Setup Backend API

Navigate to the backend directory and install dependencies:

```bash
cd ../backend
pip install -r requirements.txt
python app.py
```

**Expected Output:**
```
Starting Crop Yield Prediction API Server...
Server running on http://localhost:5000
API Documentation: http://localhost:5000/api/
 * Running on http://0.0.0.0:5000
```

### Step 4: Open Frontend

In a web browser, open:
```
file:///path/to/crop%20yield%20prediction/frontend/index.html
```

Or start a simple HTTP server in the frontend directory:

```bash
# Using Python 3
cd ../frontend
python -m http.server 8000
```

Then navigate to: `http://localhost:8000`

---

## 💻 Usage

### Using the Application

1. **Fill in Soil Data**
   - Enter nitrogen, phosphorus, potassium levels (in mg/kg)
   - Specify pH value (4-9)
   - Provide soil moisture percentage (0-100%)
   - Select soil type (Loamy, Sandy, Clay, Silt)

2. **Enter Weather Information**
   - Average temperature (°C)
   - Expected rainfall (mm)
   - Relative humidity (%)

3. **Select Crop Type**
   - Choose from: Rice, Wheat, Corn, Soybean, Barley
   - Optionally specify region

4. **Get Results**
   - Click "🔮 Predict Yield & Get Recommendations"
   - View comprehensive results:
     - Predicted yield in kg/hectare
     - Soil health analysis
     - Seed recommendations
     - Fertilizer suggestions
     - Weather warnings

### Example Input Values

**For Rice (Good Conditions):**
- Nitrogen: 60 mg/kg
- Phosphorus: 35 mg/kg
- Potassium: 35 mg/kg
- pH: 7.0
- Moisture: 65%
- Temperature: 28°C
- Rainfall: 200mm
- Humidity: 75%

---

## 🔌 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Endpoints

#### 1. Health Check
```
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-12T10:30:00.000000",
  "models_loaded": true
}
```

#### 2. Data Ranges
```
GET /api/data-ranges
```

**Response:**
```json
{
  "soil_types": ["Loamy", "Sandy", "Clay", "Silt"],
  "crop_types": ["Rice", "Wheat", "Corn", "Soybean", "Barley"],
  "ranges": {
    "nitrogen": {"min": 0, "max": 150, "unit": "mg/kg"},
    ...
  }
}
```

#### 3. Predict Yield
```
POST /api/predict-yield
Content-Type: application/json
```

**Request Body:**
```json
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

**Response:**
```json
{
  "success": true,
  "prediction": {
    "yield_estimate": 5642.34,
    "yield_unit": "kg/hectare",
    "crop_type": "Rice"
  },
  "soil_analysis": [
    {
      "nutrient": "Nitrogen",
      "level": "Optimal",
      "value": 60,
      "recommendation": "Nitrogen levels are adequate"
    },
    ...
  ],
  "weather_analysis": {
    "warnings": [],
    "temperature": 28,
    "rainfall": 200,
    "humidity": 75
  }
}
```

#### 4. Get Recommendations
```
POST /api/recommend
Content-Type: application/json
```

**Request Body:** Same as `/predict-yield`

**Response:**
```json
{
  "success": true,
  "recommendations": {
    "seed": {
      "recommended_crop": "Rice",
      "confidence": 87.5,
      "reason": "Optimal for your soil (pH: 7.0) and weather conditions..."
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
      "reason": "Selected based on soil NPK levels and pH..."
    }
  },
  "input_summary": {
    "crop_type": "Rice",
    "soil_type": "Loamy",
    "region": "Not specified"
  }
}
```

### Error Handling

**400 Bad Request (Validation Error):**
```json
{
  "success": false,
  "errors": {
    "nitrogen": "Value must be between 0 and 150"
  }
}
```

**500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Models not loaded. Please train models first."
}
```

---

## 🤖 Model Details

### Yield Prediction Model
- **Type:** Random Forest Regressor
- **Features:** 8 (nitrogen, phosphorus, potassium, pH, moisture, temperature, rainfall, humidity)
- **Target:** Crop yield (kg/hectare)
- **Training Samples:** 500 synthetic samples
- **Performance Metrics:**
  - RMSE: Mean Squared Error
  - MAE: Mean Absolute Error
  - R²: Coefficient of Determination
- **Algorithm:** Ensemble of decision trees with averaging

### Seed Recommendation Model
- **Type:** Random Forest Classifier
- **Features:** 7 (N, P, K, pH, moisture, temperature, rainfall)
- **Classes:** Rice, Wheat, Corn, Soybean, Barley
- **Training Samples:** 500 synthetic samples
- **Performance:** Classification accuracy metric

### Fertilizer Recommendation Model
- **Type:** Random Forest Classifier
- **Features:** 6 (N, P, K, pH, moisture, soil_type_encoded)
- **Classes:** NPK 10-26-26, NPK 12-32-16, NPK 15-15-15, NPK 20-20-0, Organic Compost
- **Training Samples:** 500 synthetic samples

### Label Encoder
- **Purpose:** Encodes soil types to numeric values
- **Classes:** Loamy (0), Sandy (1), Clay (2), Silt (3)

---

## ⚙️ Configuration

### Backend Configuration

Edit `backend/app.py` to customize:

```python
# Model directory
MODEL_DIR = '../ml_models'

# CORS settings
CORS(app)

# Server configuration
app.run(debug=True, host='0.0.0.0', port=5000)
```

### Frontend Configuration

Edit `frontend/script.js` to customize:

```javascript
const API_BASE_URL = 'http://localhost:5000/api';
const TIMEOUT = 10000; // 10 seconds
```

### Model Training Configuration

Edit `ml_models/train_models.py` to adjust:

```python
# Training parameters
n_samples = 500           # Number of synthetic samples
n_estimators = 100        # Number of decision trees
max_depth = 15           # Maximum tree depth
test_size = 0.2          # Train/test split ratio
```

---

## 🐛 Troubleshooting

### Issue: "Models not found" or "All models loaded" error

**Solution:**
```bash
cd ml_models
python train_models.py
```
Ensure all `.pkl` files are created in the `ml_models` directory.

### Issue: CORS errors in browser console

**Solution:** 
Backend CORS is already enabled. If issues persist:
1. Ensure backend is running on `localhost:5000`
2. Check browser console for exact error message
3. Try accessing via `http://localhost:8000` (frontend server)

### Issue: Cannot connect to localhost:5000

**Solution:**
1. Verify backend server is running: `python app.py`
2. Check port 5000 is not in use: `netstat -ano | findstr :5000` (Windows)
3. Firewall may block the connection
4. Use `0.0.0.0` instead of `localhost` in URLs

### Issue: Models load but predictions fail

**Solution:**
1. Check model file sizes (should be > 1 MB each)
2. Reinstall scikit-learn: `pip install --upgrade scikit-learn`
3. Verify Python version: `python --version` (should be 3.8+)
4. Check backend logs for specific errors

### Issue: Frontend shows "Offline mode" warnings

**Solution:**
1. Backend must be running before opening frontend
2. Ensure API_BASE_URL in `script.js` matches backend URL
3. Check browser's developer console (F12) for network errors

---

## 📊 Model Performance Metrics

### Training Results Example

```
Yield Model Performance:
  RMSE: 125.45 kg/hectare
  MAE: 98.23 kg/hectare
  R²: 0.8234

Seed Model Performance:
  Accuracy: 0.9150 (91.50%)

Fertilizer Model Performance:
  Accuracy: 0.8850 (88.50%)
```

---

## 🚀 Deployment

### For Production

1. **Set Flask to production mode:**
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

2. **Use WSGI server (Gunicorn):**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

3. **Frontend optimization:**
   - Minify CSS and JavaScript
   - Compress images
   - Use CDN for static files

4. **Security:**
   - Enable HTTPS
   - Add authentication
   - Rate limit API endpoints
   - Sanitize user inputs

5. **Database (optional):**
   - Store predictions for analytics
   - Track user recommendations
   - Build historical data

---

## 🔄 Future Enhancements

- [ ] Multi-language support (Hindi, Spanish, etc.)
- [ ] User authentication and profiles
- [ ] Historical predictions tracking
- [ ] Real-time weather API integration
- [ ] Mobile app (React Native / Flutter)
- [ ] Advanced visualizations (charts, maps)
- [ ] Crop rotation recommendations
- [ ] Pest/disease prediction
- [ ] Cost-benefit analysis
- [ ] Integration with agricultural IoT devices
- [ ] SMS/Email notifications
- [ ] Offline mode with local storage
- [ ] CSV import/export functionality
- [ ] Export PDF reports

---

## 📄 Technical Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Frontend | HTML5, CSS3, JavaScript | ES6+ |
| Backend | Flask | 3.0.0 |
| ML Framework | scikit-learn | 1.3.2 |
| Server | Werkzeug | 3.0.0 |
| Data Processing | NumPy, Pandas | Latest |
| Model Serialization | joblib | 1.3.2 |

---

## 📚 References

- [Scikit-learn Documentation](https://scikit-learn.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [MDN Web Docs](https://developer.mozilla.org/)
- [Agricultural Science Resources](https://www.fao.org/)

---

## 📝 License

This project is provided as-is for educational and research purposes.

---

## 👥 Contributors

- AI Developer
- Agricultural Domain Expert Support

---

## ⚠️ Disclaimer

**Important:** These predictions are based on machine learning models and should NOT be the sole basis for agricultural decisions. Always:
- Consult with local agricultural experts
- Validate predictions against regional data
- Consider local climate variations
- Review soil test reports from certified labs
- Follow regional farming guidelines

---

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review API response messages
3. Check browser console for errors (F12)
4. Verify all dependencies are installed

---

**Last Updated:** January 2024  
**Version:** 1.0.0
