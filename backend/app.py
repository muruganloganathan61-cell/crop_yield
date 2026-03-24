"""
Crop Yield Prediction - Flask Backend API
REST API for yield prediction and agricultural recommendations
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import joblib
import numpy as np
import os
from datetime import datetime
from urllib.parse import urlparse
import requests
from io import BytesIO
import base64
import re

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)  # Enable CORS for frontend communication

# ============================================================================
# MODEL LOADING
# ============================================================================

MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'ml_models')

def load_model(filename):
    """Utility to load a model file safely"""
    try:
        path = os.path.join(MODEL_DIR, filename)
        if os.path.exists(path):
            model = joblib.load(path)
            print(f"[SUCCESS] {filename} loaded successfully")
            return model
        else:
            print(f"[WARNING] {filename} not found at {path}")
            return None
    except Exception as e:
        print(f"[ERROR] Error loading {filename}: {e}")
        return None

yield_model = load_model('yield_model.pkl')
seed_model = load_model('seed_model.pkl')
fertilizer_model = load_model('fertilizer_model.pkl')
soil_type_encoder = load_model('soil_type_encoder.pkl')

if not all([yield_model, seed_model, fertilizer_model]):
    print("[WARNING] Some core models are missing. Some features may not work.")

# ============================================================================
# CONSTANTS & REFERENCE DATA
# ============================================================================

SOIL_TYPES = ['Loamy', 'Sandy', 'Clay', 'Silt']
CROP_TYPES = ['Rice', 'Wheat', 'Corn', 'Soybean', 'Barley']

SOIL_IMPROVEMENT_RULES = {
    'nitrogen': {
        'low': {'threshold': 40, 'suggestion': 'Use nitrogen-rich fertilizers (Urea, Ammonium Nitrate)'},
        'normal': {'threshold': 70, 'suggestion': 'Nitrogen levels are adequate'},
        'high': {'threshold': 100, 'suggestion': 'Nitrogen is sufficient; avoid over-application'}
    },
    'phosphorus': {
        'low': {'threshold': 25, 'suggestion': 'Add phosphate fertilizers (DAP, MAP)'},
        'normal': {'threshold': 45, 'suggestion': 'Phosphorus levels are good'},
        'high': {'threshold': 60, 'suggestion': 'Phosphorus is abundant; minimal addition needed'}
    },
    'potassium': {
        'low': {'threshold': 25, 'suggestion': 'Apply potassium-rich fertilizers (MOP, SOP)'},
        'normal': {'threshold': 45, 'suggestion': 'Potassium levels are adequate'},
        'high': {'threshold': 60, 'suggestion': 'Potassium is sufficient; reduce applications'}
    },
    'ph': {
        'very_low': {'threshold': 5.5, 'suggestion': 'Soil is too acidic; apply lime to raise pH'},
        'low': {'threshold': 6.0, 'suggestion': 'Apply lime to improve soil pH'},
        'normal': {'threshold': 7.5, 'suggestion': 'pH is optimal for most crops'},
        'high': {'threshold': 8.0, 'suggestion': 'Soil is alkaline; add sulfur if needed'},
        'very_high': {'threshold': 8.5, 'suggestion': 'Soil is very alkaline; consider acidifying amendments'}
    },
    'moisture': {
        'low': {'threshold': 30, 'suggestion': 'Soil moisture is low; increase irrigation'},
        'normal': {'threshold': 60, 'suggestion': 'Moisture levels are optimal'},
        'high': {'threshold': 100, 'suggestion': 'Soil is waterlogged; improve drainage'}
    }
}

WEATHER_WARNING_RULES = {
    'temperature': {
        'low': {'threshold': 15, 'warning': '[WARNING] Temperature is below 15C; consider frost protection'},
        'high': {'threshold': 35, 'warning': '[WARNING] Temperature exceeds 35C; ensure adequate irrigation'}
    },
    'rainfall': {
        'low': {'threshold': 75, 'warning': '[WARNING] Low rainfall; supplement with irrigation'},
        'high': {'threshold': 250, 'warning': '[WARNING] Heavy rainfall expected; ensure proper drainage'}
    },
    'humidity': {
        'low': {'threshold': 40, 'warning': '[WARNING] Low humidity; monitor for plant stress'},
        'high': {'threshold': 80, 'warning': '[WARNING] High humidity; watch for fungal diseases'}
    }
}

FERTILIZER_DETAILS = {
    'NPK 10-26-26': {
        'quantity': '150-200 kg/hectare',
        'application_time': 'Pre-planting',
        'description': 'High phosphorus and potassium; ideal for crops needing P and K boost'
    },
    'NPK 12-32-16': {
        'quantity': '120-150 kg/hectare',
        'application_time': 'Pre-planting',
        'description': 'Balanced with extra phosphorus; suitable for flowering crops'
    },
    'NPK 15-15-15': {
        'quantity': '100-150 kg/hectare',
        'application_time': 'Pre-planting & Side dressing',
        'description': 'Balanced NPK; versatile for most crops'
    },
    'NPK 20-20-0': {
        'quantity': '80-120 kg/hectare',
        'application_time': 'Top dressing',
        'description': 'Nitrogen-focused; for boosting vegetative growth'
    },
    'Organic Compost': {
        'quantity': '10-20 tonnes/hectare',
        'application_time': 'Pre-planting (2-3 weeks before)',
        'description': 'Sustainable option; improves soil health and structure'
    }
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_input(data):
    """Validate input data from API request"""
    required_fields = {
        'nitrogen': (0, 150),
        'phosphorus': (0, 100),
        'potassium': (0, 100),
        'ph': (4, 9),
        'moisture': (0, 100),
        'temperature': (-10, 50),
        'rainfall': (0, 400),
        'humidity': (0, 100),
        'soil_type': SOIL_TYPES,
        'crop_type': CROP_TYPES
    }
    
    errors = {}
    
    for field, rule in required_fields.items():
        if field not in data:
            errors[field] = f"Missing required field: {field}"
        elif isinstance(rule, list):  # For categorical fields
            if data[field] not in rule:
                errors[field] = f"Invalid value. Choose from: {', '.join(rule)}"
        else:
            min_val, max_val = rule
            try:
                val = float(data[field])
                if not (min_val <= val <= max_val):
                    errors[field] = f"Value must be between {min_val} and {max_val}"
            except (ValueError, TypeError):
                errors[field] = f"Must be a numeric value"
    
    return errors

def get_soil_suggestions(nitrogen, phosphorus, potassium, ph, moisture):
    """Generate soil improvement suggestions based on values"""
    suggestions = []
    
    # Nitrogen assessment
    if nitrogen < 40:
        suggestions.append({
            'nutrient': 'Nitrogen',
            'level': 'Low',
            'value': nitrogen,
            'recommendation': SOIL_IMPROVEMENT_RULES['nitrogen']['low']['suggestion']
        })
    elif nitrogen > 70:
        suggestions.append({
            'nutrient': 'Nitrogen',
            'level': 'High',
            'value': nitrogen,
            'recommendation': SOIL_IMPROVEMENT_RULES['nitrogen']['high']['suggestion']
        })
    else:
        suggestions.append({
            'nutrient': 'Nitrogen',
            'level': 'Optimal',
            'value': nitrogen,
            'recommendation': SOIL_IMPROVEMENT_RULES['nitrogen']['normal']['suggestion']
        })
    
    # Phosphorus assessment
    if phosphorus < 25:
        suggestions.append({
            'nutrient': 'Phosphorus',
            'level': 'Low',
            'value': phosphorus,
            'recommendation': SOIL_IMPROVEMENT_RULES['phosphorus']['low']['suggestion']
        })
    elif phosphorus > 45:
        suggestions.append({
            'nutrient': 'Phosphorus',
            'level': 'High',
            'value': phosphorus,
            'recommendation': SOIL_IMPROVEMENT_RULES['phosphorus']['high']['suggestion']
        })
    else:
        suggestions.append({
            'nutrient': 'Phosphorus',
            'level': 'Optimal',
            'value': phosphorus,
            'recommendation': SOIL_IMPROVEMENT_RULES['phosphorus']['normal']['suggestion']
        })
    
    # Potassium assessment
    if potassium < 25:
        suggestions.append({
            'nutrient': 'Potassium',
            'level': 'Low',
            'value': potassium,
            'recommendation': SOIL_IMPROVEMENT_RULES['potassium']['low']['suggestion']
        })
    elif potassium > 45:
        suggestions.append({
            'nutrient': 'Potassium',
            'level': 'High',
            'value': potassium,
            'recommendation': SOIL_IMPROVEMENT_RULES['potassium']['high']['suggestion']
        })
    else:
        suggestions.append({
            'nutrient': 'Potassium',
            'level': 'Optimal',
            'value': potassium,
            'recommendation': SOIL_IMPROVEMENT_RULES['potassium']['normal']['suggestion']
        })
    
    # pH assessment
    if ph < 5.5:
        suggestions.append({
            'nutrient': 'Soil pH',
            'level': 'Very Acidic',
            'value': ph,
            'recommendation': SOIL_IMPROVEMENT_RULES['ph']['very_low']['suggestion']
        })
    elif ph < 6.0:
        suggestions.append({
            'nutrient': 'Soil pH',
            'level': 'Acidic',
            'value': ph,
            'recommendation': SOIL_IMPROVEMENT_RULES['ph']['low']['suggestion']
        })
    elif ph < 7.5:
        suggestions.append({
            'nutrient': 'Soil pH',
            'level': 'Optimal',
            'value': ph,
            'recommendation': SOIL_IMPROVEMENT_RULES['ph']['normal']['suggestion']
        })
    elif ph < 8.0:
        suggestions.append({
            'nutrient': 'Soil pH',
            'level': 'Alkaline',
            'value': ph,
            'recommendation': SOIL_IMPROVEMENT_RULES['ph']['high']['suggestion']
        })
    else:
        suggestions.append({
            'nutrient': 'Soil pH',
            'level': 'Very Alkaline',
            'value': ph,
            'recommendation': SOIL_IMPROVEMENT_RULES['ph']['very_high']['suggestion']
        })
    
    # Moisture assessment
    if moisture < 30:
        suggestions.append({
            'nutrient': 'Soil Moisture',
            'level': 'Low',
            'value': moisture,
            'recommendation': SOIL_IMPROVEMENT_RULES['moisture']['low']['suggestion']
        })
    elif moisture > 80:
        suggestions.append({
            'nutrient': 'Soil Moisture',
            'level': 'High',
            'value': moisture,
            'recommendation': SOIL_IMPROVEMENT_RULES['moisture']['high']['suggestion']
        })
    else:
        suggestions.append({
            'nutrient': 'Soil Moisture',
            'level': 'Optimal',
            'value': moisture,
            'recommendation': SOIL_IMPROVEMENT_RULES['moisture']['normal']['suggestion']
        })
    
    return suggestions

def get_weather_warnings(temperature, rainfall, humidity):
    """Generate weather-related warnings"""
    warnings = []
    
    if temperature < 15:
        warnings.append(WEATHER_WARNING_RULES['temperature']['low']['warning'])
    elif temperature > 35:
        warnings.append(WEATHER_WARNING_RULES['temperature']['high']['warning'])
    
    if rainfall < 75:
        warnings.append(WEATHER_WARNING_RULES['rainfall']['low']['warning'])
    elif rainfall > 250:
        warnings.append(WEATHER_WARNING_RULES['rainfall']['high']['warning'])
    
    if humidity < 40:
        warnings.append(WEATHER_WARNING_RULES['humidity']['low']['warning'])
    elif humidity > 80:
        warnings.append(WEATHER_WARNING_RULES['humidity']['high']['warning'])
    
    return warnings

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'models_loaded': all([yield_model, seed_model, fertilizer_model])
    }), 200

@app.route('/api/predict-yield', methods=['POST'])
def predict_yield():
    """
    Predict crop yield based on soil, weather, and crop data
    
    Expected JSON:
    {
        "nitrogen": float,
        "phosphorus": float,
        "potassium": float,
        "ph": float,
        "moisture": float,
        "temperature": float,
        "rainfall": float,
        "humidity": float,
        "soil_type": string,
        "crop_type": string
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        errors = validate_input(data)
        if errors:
            return jsonify({'success': False, 'errors': errors}), 400
        
        if not yield_model:
            return jsonify({
                'success': False,
                'error': 'Yield model not loaded. Please train models first.'
            }), 500
        
        # Prepare features for prediction
        features = np.array([[
            float(data['nitrogen']),
            float(data['phosphorus']),
            float(data['potassium']),
            float(data['ph']),
            float(data['moisture']),
            float(data['temperature']),
            float(data['rainfall']),
            float(data['humidity'])
        ]])
        
        # Make prediction
        predicted_yield = yield_model.predict(features)[0]
        
        # Generate soil suggestions
        soil_suggestions = get_soil_suggestions(
            float(data['nitrogen']),
            float(data['phosphorus']),
            float(data['potassium']),
            float(data['ph']),
            float(data['moisture'])
        )
        
        # Generate weather warnings
        weather_warnings = get_weather_warnings(
            float(data['temperature']),
            float(data['rainfall']),
            float(data['humidity'])
        )
        
        response = {
            'success': True,
            'prediction': {
                'yield_estimate': round(max(predicted_yield, 0), 2),
                'yield_unit': 'kg/hectare',
                'confidence': 'Based on Random Forest regression model',
                'crop_type': data['crop_type']
            },
            'soil_analysis': soil_suggestions,
            'weather_analysis': {
                'warnings': weather_warnings if weather_warnings else ['All weather parameters are favorable'],
                'temperature': float(data['temperature']),
                'rainfall': float(data['rainfall']),
                'humidity': float(data['humidity'])
            }
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Prediction failed: {str(e)}'
        }), 500

@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    """
    Get seed and fertilizer recommendations based on soil and weather conditions
    
    Expected JSON: Same as predict-yield
    """
    try:
        data = request.get_json()
        
        # Validate input
        errors = validate_input(data)
        if errors:
            return jsonify({'success': False, 'errors': errors}), 400
        
        if not (seed_model and fertilizer_model):
            return jsonify({
                'success': False,
                'error': 'Recommendation models not loaded. Please train models first.'
            }), 500
        
        # Prepare features for seed recommendation
        seed_features = np.array([[
            float(data['nitrogen']),
            float(data['phosphorus']),
            float(data['potassium']),
            float(data['ph']),
            float(data['moisture']),
            float(data['temperature']),
            float(data['rainfall'])
        ]])
        
        # Get seed recommendation
        recommended_seed = seed_model.predict(seed_features)[0]
        seed_probabilities = seed_model.predict_proba(seed_features)[0]
        seed_confidence = max(seed_probabilities) * 100
        
        # Prepare features for fertilizer recommendation
        if soil_type_encoder:
            try:
                soil_type_encoded = soil_type_encoder.transform([data['soil_type']])[0]
            except Exception as e:
                print(f"Encoding error: {e}")
                soil_type_encoded = 0 # Fallback
        else:
            # Simple mapping fallback if encoder is missing
            soil_map = {s: i for i, s in enumerate(SOIL_TYPES)}
            soil_type_encoded = soil_map.get(data['soil_type'], 0)
        
        fertilizer_features = np.array([[
            float(data['nitrogen']),
            float(data['phosphorus']),
            float(data['potassium']),
            float(data['ph']),
            float(data['moisture']),
            soil_type_encoded
        ]])
        
        # Get fertilizer recommendation
        recommended_fertilizer = fertilizer_model.predict(fertilizer_features)[0]
        fertilizer_probabilities = fertilizer_model.predict_proba(fertilizer_features)[0]
        fertilizer_confidence = max(fertilizer_probabilities) * 100
        
        response = {
            'success': True,
            'recommendations': {
                'seed': {
                    'recommended_crop': recommended_seed,
                    'confidence': round(seed_confidence, 2),
                    'reason': f'Optimal for your soil (pH: {data["ph"]}) and weather conditions (Temp: {data["temperature"]}C, Rainfall: {data["rainfall"]}mm)'
                },
                'fertilizer': {
                    'recommended_type': recommended_fertilizer,
                    'confidence': round(fertilizer_confidence, 2),
                    'details': FERTILIZER_DETAILS.get(recommended_fertilizer, {
                        'quantity': 'As per product specifications',
                        'application_time': 'Follow manufacturer guidelines',
                        'description': 'Consult agronomist for optimal application'
                    }),
                    'soil_type': data['soil_type'],
                    'reason': f'Selected based on soil NPK levels and pH ({data["ph"]})'
                }
            },
            'input_summary': {
                'crop_type': data['crop_type'],
                'soil_type': data['soil_type'],
                'region': data.get('region', 'Not specified')
            }
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Recommendation failed: {str(e)}'
        }), 500

@app.route('/api/data-ranges', methods=['GET'])
def get_data_ranges():
    """Get valid data ranges and options for frontend validation"""
    return jsonify({
        'soil_types': SOIL_TYPES,
        'crop_types': CROP_TYPES,
        'ranges': {
            'nitrogen': {'min': 0, 'max': 150, 'unit': 'mg/kg'},
            'phosphorus': {'min': 0, 'max': 100, 'unit': 'mg/kg'},
            'potassium': {'min': 0, 'max': 100, 'unit': 'mg/kg'},
            'ph': {'min': 4, 'max': 9, 'unit': 'pH'},
            'moisture': {'min': 0, 'max': 100, 'unit': '%'},
            'temperature': {'min': -10, 'max': 50, 'unit': 'C'},
            'rainfall': {'min': 0, 'max': 400, 'unit': 'mm'},
            'humidity': {'min': 0, 'max': 100, 'unit': '%'}
        }
    }), 200

@app.route('/', methods=['GET'])
def index():
    """API documentation"""
    return jsonify({
        'name': 'Crop Yield Prediction API',
        'version': '1.0.0',
        'description': 'REST API for predicting crop yield and providing agricultural recommendations',
        'endpoints': {
            'GET /api/health': 'Health check',
            'GET /api/data-ranges': 'Get valid data ranges and options',
            'POST /api/predict-yield': 'Predict crop yield',
            'POST /api/recommend': 'Get seed and fertilizer recommendations',
            'POST /api/disease-classification': 'Classify plant disease',
            'GET /api/disease-info/{disease}': 'Get disease information',
            'GET /api/diseases-list': 'List all diseases'
        }
    }), 200

@app.route('/index.html', methods=['GET'])
def serve_index():
    """Serve main application page"""
    try:
        return send_file('../frontend/index.html')
    except Exception as e:
        return jsonify({'error': f'Failed to serve index.html: {str(e)}'}), 404

@app.route('/disease_classification.html', methods=['GET'])
def serve_disease_classification():
    """Serve disease classification page"""
    try:
        return send_file('../frontend/disease_classification.html')
    except Exception as e:
        return jsonify({'error': f'Failed to serve disease_classification.html: {str(e)}'}), 404

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(415)
def unsupported_media_type(error):
    return jsonify({'error': 'Unsupported media type. Please send JSON.'}), 415

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# PLANT DISEASE CLASSIFICATION
# ============================================================================

# Bytez API Configuration
BYTEZ_API_KEY = os.getenv('BYTEZ_API_KEY', '15ae9bca2b0cf5da31236514c29af493')
# Default plant disease model used by examples in the repo
# Use a more reliable PlantVillage model slug
DISEASE_MODEL_NAME = 'marwaALzaabi/plant-disease-detection-vit'
# Optional Hugging Face fallback (set HF_API_TOKEN to use)
HF_API_TOKEN = os.getenv('HF_API_TOKEN', '')
HF_MODEL_NAME = os.getenv('HF_MODEL_NAME', DISEASE_MODEL_NAME)


def call_bytez_inference(image_file=None, image_url=None):
    """
    Call Bytez v2 inference API with image file or URL.
    Returns parsed JSON on success.
    """
    url = f"https://api.bytez.com/models/v2/{DISEASE_MODEL_NAME}"

    headers = {
        "Authorization": f"Bearer {BYTEZ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {}
    if image_url:
        payload["url"] = image_url
    elif image_file:
        try:
            file_bytes = image_file.read()
            # Standard Bytez v2 expects base64; some models might prefer data URI format
            # We'll use a data URI just in case the model requires the mime type hint
            content_type = getattr(image_file, 'content_type', None) or 'image/jpeg'
            b64_data = base64.b64encode(file_bytes).decode('utf-8')
            payload["base64"] = f"data:{content_type};base64,{b64_data}"
        finally:
            try:
                image_file.seek(0)
            except Exception:
                pass
    else:
        raise Exception("Either image_file or image_url must be provided")

    response = requests.post(url, headers=headers, json=payload, timeout=30)

    if response.status_code != 200:
        raise Exception(f"Bytez API error: {response.status_code} {response.text}")

    result = response.json()
    if result.get('error'):
        raise Exception(f"Bytez API returned error: {result['error']}")
    
    # Bytez v2 usually returns the output in the 'output' field
    return result.get('output') or result

# Map for ajay-drew/plant-disease-vit (standard PlantVillage classes)
PLANT_VILLAGE_MAP = {
    "LABEL_0": "Apple___Apple_scab",
    "LABEL_1": "Apple___Black_rot",
    "LABEL_2": "Apple___Cedar_apple_rust",
    "LABEL_3": "Apple___healthy",
    "LABEL_4": "Blueberry___healthy",
    "LABEL_5": "Cherry_(including_sour)___Powdery_mildew",
    "LABEL_6": "Cherry_(including_sour)___healthy",
    "LABEL_7": "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "LABEL_8": "Corn_(maize)___Common_rust_",
    "LABEL_9": "Corn_(maize)___Northern_Leaf_Blight",
    "LABEL_10": "Corn_(maize)___healthy",
    "LABEL_11": "Grape___Black_rot",
    "LABEL_12": "Grape___Esca_(Black_Measles)",
    "LABEL_13": "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "LABEL_14": "Grape___healthy",
    "LABEL_15": "Orange___Haunglongbing_(Citrus_greening)",
    "LABEL_16": "Peach___Bacterial_spot",
    "LABEL_17": "Peach___healthy",
    "LABEL_18": "Pepper,_bell___Bacterial_spot",
    "LABEL_19": "Pepper,_bell___healthy",
    "LABEL_20": "Potato___Early_blight",
    "LABEL_21": "Potato___Late_blight",
    "LABEL_22": "Potato___healthy",
    "LABEL_23": "Raspberry___healthy",
    "LABEL_24": "Soybean___healthy",
    "LABEL_25": "Squash___Powdery_mildew",
    "LABEL_26": "Strawberry___Leaf_scorch",
    "LABEL_27": "Strawberry___healthy",
    "LABEL_28": "Tomato___Bacterial_spot",
    "LABEL_29": "Tomato___Early_blight",
    "LABEL_30": "Tomato___Late_blight",
    "LABEL_31": "Tomato___Leaf_Mold",
    "LABEL_32": "Tomato___Septoria_leaf_spot",
    "LABEL_33": "Tomato___Spider_mites Two-spotted_spider_mite",
    "LABEL_34": "Tomato___Target_Spot",
    "LABEL_35": "Tomato___Yellow_Leaf_Curl_Virus",
    "LABEL_36": "Tomato___mosaic_virus",
    "LABEL_37": "Tomato___healthy"
}

# Plant disease classification mapping and recommendations
DISEASE_INFO = {
    'healthy': {
        'confidence_threshold': 0.7,
        'treatment': 'No disease detected. Maintain regular crop care and monitoring.',
        'severity': 'None',
        'actions': [
            'Continue regular watering schedule',
            'Maintain appropriate fertilization',
            'Monitor for any changes in plant health',
            'Continue preventive measures'
        ]
    },
    'early_blight': {
        'treatment': 'Apply fungicide (Chlorothalonil or Mancozeb) every 7-10 days',
        'severity': 'Moderate',
        'actions': [
            'Remove infected leaves immediately',
            'Improve air circulation by pruning lower branches',
            'Apply fungicide spray',
            'Avoid watering foliage',
            'Clean garden tools to prevent spread'
        ]
    },
    'late_blight': {
        'treatment': 'Apply systemic fungicide (Metalaxyl or Cymoxanil) immediately',
        'severity': 'High',
        'actions': [
            'Remove heavily infected plants',
            'Apply fungicide every 7 days',
            'Ensure proper spacing for air circulation',
            'Avoid overhead irrigation',
            'Burn or bury affected plant material'
        ]
    },
    'powdery_mildew': {
        'treatment': 'Apply sulfur dust or potassium bicarbonate fungicide',
        'severity': 'Low-Moderate',
        'actions': [
            'Apply fungicide at first sign of white powder',
            'Improve air circulation',
            'Reduce nitrogen fertilizer if excessive',
            'Avoid overhead watering',
            'Remove heavily affected leaves'
        ]
    },
    'rust': {
        'treatment': 'Apply copper-based fungicide or sulfur dust',
        'severity': 'Moderate',
        'actions': [
            'Remove infected leaves promptly',
            'Apply fungicide to undersides of leaves',
            'Increase air circulation',
            'Avoid overhead irrigation',
            'Monitor for spread weekly'
        ]
    },
    'common_rust': {
        'treatment': 'Apply copper-based fungicide or sulfur dust. Resistant hybrids are best.',
        'severity': 'Moderate',
        'actions': [
            'Remove infected leaves promptly',
            'Apply fungicide to undersides of leaves',
            'Increase air circulation',
            'Avoid overhead irrigation',
            'Plant resistant corn varieties'
        ]
    },
    'leaf_spot': {
        'treatment': 'Apply copper fungicide or Bordeaux mixture',
        'severity': 'Low-Moderate',
        'actions': [
            'Remove infected leaves',
            'Apply fungicide every 10-14 days',
            'Avoid wetting foliage during watering',
            'Clean up fallen debris',
            'Space plants properly for airflow'
        ]
    },
    'mosaic_virus': {
        'treatment': 'No cure; manage by controlling vectors and removing infected plants',
        'severity': 'High',
        'actions': [
            'Remove and destroy infected plants',
            'Control aphids and other vector insects',
            'Disinfect tools and hands between plants',
            'Plant resistant varieties',
            'Avoid overhead watering'
        ]
    },
    'bacterial_spot': {
        'treatment': 'Apply copper-based bactericides',
        'severity': 'Moderate',
        'actions': [
            'Remove infected plant debris',
            'Avoid overhead irrigation',
            'Use certified disease-free seeds',
            'Rotate crops every 2-3 years'
        ]
    },
    'leaf_mold': {
        'treatment': 'Apply fungicides and improve ventilation',
        'severity': 'Low-Moderate',
        'actions': [
            'Increase spacing between plants',
            'Lower humidity in greenhouses',
            'Remove infected lower leaves'
        ]
    },
    'yellow_leaf_curl_virus': {
        'treatment': 'Control whiteflies and remove infected plants',
        'severity': 'High',
        'actions': [
            'Use silver-colored mulches to repel whiteflies',
            'Install fine-mesh screening in greenhouses',
            'Remove weeds that host the virus'
        ]
    }
}

def classify_plant_disease(image_url, test_disease=None):
    """
    Classify plant disease using available inference APIs
    Returns disease classification and recommendations
    Supports HuggingFace API with mock fallback
    
    Args:
        image_url: URL or identifier of the plant image
        test_disease: (Optional) For testing, force a specific disease classification
    """
    try:
        # Primary method: HuggingFace API if token is configured
        if HF_API_TOKEN:
            print("[INFO] Using Hugging Face API for disease classification")
            hf_result = call_hf_inference(image_url)
            if 'error' not in hf_result:
                return hf_result
            else:
                print(f"[WARNING] Hugging Face API failed: {hf_result.get('error')}")
        
        # Fallback: simple mock classifier for offline testing
        print("[INFO] Using mock classification due to no primary API available")
        mock = simple_mock_classifier(image_url, test_disease=test_disease)
        mock['note'] = 'Returned mock classification (no external API configured)'
        return mock
    
    except Exception as e:
        print(f"[ERROR] Disease classification failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        
        # Final fallback: simple mock classifier
        try:
            err_text = f"API error: {type(e).__name__}: {str(e)}"
        except Exception:
            err_text = 'API error'

        mock = simple_mock_classifier(image_url, test_disease=test_disease)
        mock['error'] = err_text
        mock['note'] = 'Returned mock classification after error'
        return mock


def call_hf_inference(image_url):
    """Call Hugging Face Inference API as a fallback if HF_API_TOKEN is set."""
    if not HF_API_TOKEN:
        return {'error': 'HF_API_TOKEN not configured', 'disease': None, 'confidence': 0}

    headers = {
        'Authorization': f'Bearer {HF_API_TOKEN}',
        'Accept': 'application/json'
    }
    model_url = f'https://api-inference.huggingface.co/models/{HF_MODEL_NAME}'
    try:
        resp = requests.post(model_url, headers=headers, json={"inputs": image_url}, timeout=30)
    except Exception as ex:
        return {'error': f'HF request failed: {ex}', 'disease': None, 'confidence': 0}

    if resp.status_code != 200:
        try:
            body = resp.json()
            err = body.get('error') or body
        except Exception:
            err = resp.text
        return {'error': f'HF API error: {resp.status_code} {err}', 'disease': None, 'confidence': 0}

    try:
        data = resp.json()
    except Exception as ex:
        return {'error': f'Invalid HF response: {ex}', 'disease': None, 'confidence': 0}

    # Expecting a list of label/confidence dicts or similar
    if isinstance(data, list) and data:
        first = data[0]
        if isinstance(first, dict):
            label = first.get('label') or first.get('class') or first.get('name') or 'unknown'
            score = first.get('score') or first.get('confidence') or 0
            return {
                'disease': label,
                'confidence': float(score),
                'raw_api_response': data,
                'timestamp': datetime.now().isoformat()
            }

    # Fallback: try to extract common keys
    if isinstance(data, dict):
        # Some models return {'error':...}
        if 'error' in data:
            return {'error': data.get('error'), 'disease': None, 'confidence': 0}
        # Or {'label':..., 'score':...}
        label = data.get('label') or data.get('class')
        score = data.get('score') or data.get('confidence')
        if label:
            return {'disease': label, 'confidence': float(score or 0), 'raw_api_response': data, 'timestamp': datetime.now().isoformat()}

    return {'error': 'Unexpected HF response format', 'disease': None, 'confidence': 0}


def simple_mock_classifier(image_url, test_disease=None):
    """
    Very small heuristic mock used when cloud providers fail.
    Looks for keywords in image URL and returns plausible disease labels for testing.
    If test_disease is provided, uses that for testing purposes.
    """
    # If test_disease is specified, use it directly (for testing)
    if test_disease and test_disease.lower() in DISEASE_INFO:
        disease = test_disease.lower()
        confidence_map = {
            'healthy': 0.95,
            'early_blight': 0.88,
            'late_blight': 0.90,
            'powdery_mildew': 0.85,
            'rust': 0.83,
            'leaf_spot': 0.82,
            'mosaic_virus': 0.87
        }
        return {
            'disease': disease,
            'confidence': confidence_map.get(disease, 0.80),
            'timestamp': datetime.now().isoformat(),
            'note': 'Test classification (using test_disease parameter)'
        }
    
    # Otherwise, heuristically detect from URL
    url = (image_url or '').lower()
    if 'mosaic' in url or 'mosaic-virus' in url or 'mosaic_virus' in url:
        return {'disease': 'mosaic_virus', 'confidence': 0.92, 'timestamp': datetime.now().isoformat()}
    if 'late_blight' in url or 'lateblight' in url:
        return {'disease': 'late_blight', 'confidence': 0.90, 'timestamp': datetime.now().isoformat()}
    if 'blight' in url or 'early_blight' in url:
        return {'disease': 'early_blight', 'confidence': 0.85, 'timestamp': datetime.now().isoformat()}
    if 'rust' in url:
        return {'disease': 'rust', 'confidence': 0.84, 'timestamp': datetime.now().isoformat()}
    if 'powdery' in url or 'mildew' in url:
        return {'disease': 'powdery_mildew', 'confidence': 0.80, 'timestamp': datetime.now().isoformat()}
    if 'leaf_spot' in url or 'leafspot' in url:
        return {'disease': 'leaf_spot', 'confidence': 0.82, 'timestamp': datetime.now().isoformat()}
    # default healthy
    return {'disease': 'healthy', 'confidence': 0.75, 'timestamp': datetime.now().isoformat()}


@app.route('/api/disease-classification', methods=['POST'])
def disease_classification_endpoint():
    """
    API endpoint for plant disease classification
    Accepts: 
      - image_url (string): URL of the plant image
      - image_file (file): Uploaded image file
      - test_disease (string): For testing, specify the disease name directly (optional)
    
    Available test diseases: healthy, early_blight, late_blight, powdery_mildew, rust, leaf_spot, mosaic_virus
    """
    try:
        # For Bytez we require a file upload (multipart/form-data)
        data = request.form.to_dict() if not request.is_json else request.get_json()
        image_file = request.files.get('image_file')
        test_disease = data.get('test_disease')

        # Validate request: Bytez requires either an uploaded file or an image URL
        if not image_file and not data.get('image_url'):
            return jsonify({
                'success': False,
                'error': 'image_file or image_url is required'
            }), 400

        print(f"[INFO] Processing disease classification for uploaded file: {getattr(image_file, 'filename', 'uploaded')}")

        image_url = data.get('image_url')

        # Call Bytez API
        try:
            bytez_result = call_bytez_inference(image_file=image_file, image_url=image_url)
        except Exception as ex:
            msg = str(ex)
            print(f"[ERROR] Bytez inference failed: {msg}")
            # Detect common model-not-found / wrong-route errors and provide guidance
            if '404' in msg or 'Model not found' in msg:
                hint = (
                    "Bytez returned 404 for the model endpoint. "
                    "Verify that DISEASE_MODEL_NAME is a valid Bytez model slug and using the v2 API."
                )
                return jsonify({'success': False, 'error': 'Bytez model endpoint not found', 'hint': hint, 'raw': msg}), 404
            return jsonify({'success': False, 'error': f'Bytez inference failed: {msg}', 'raw': msg}), 500

        # Normalize Bytez response
        # Bytez v2 may return a list or a dict; try to extract meaningful label and confidence
        if isinstance(bytez_result, list) and len(bytez_result) > 0:
            # pick top-scoring item if list returned
            try:
                bytez_result = sorted(bytez_result, key=lambda x: (x.get('score') or x.get('confidence') or 0), reverse=True)[0]
            except Exception:
                bytez_result = bytez_result[0]

        # timestamp
        timestamp = None

        # Try common single-field labels
        label = None
        confidence = 0
        if isinstance(bytez_result, dict):
            for k in ('label', 'disease', 'prediction', 'class', 'name'):
                if k in bytez_result:
                    label = bytez_result.get(k)
                    break

            # some responses include nested prediction lists
            if label is None:
                preds = bytez_result.get('predictions') or bytez_result.get('outputs') or bytez_result.get('data')
                if isinstance(preds, list) and preds:
                    first = preds[0]
                    if isinstance(first, dict):
                        label = first.get('label') or first.get('class') or first.get('name')
                        confidence = first.get('score') or first.get('confidence') or 0

            # timestamp and confidence top-level
            timestamp = bytez_result.get('timestamp')
            confidence = confidence or bytez_result.get('score') or bytez_result.get('confidence') or 0

        # Map Bytez labels to human readable names if needed
        # Handle formats like "LABEL_37", "label 37", or just "37"
        final_disease_name = None
        if label:
            label_str = str(label)
            label_key = label_str.upper().replace(' ', '_')
            if not label_key.startswith('LABEL_') and label_key.isdigit():
                label_key = f"LABEL_{label_key}"
            
            # Use mapping if it's a generic label
            if label_key.startswith('LABEL_'):
                final_disease_name = PLANT_VILLAGE_MAP.get(label_key)
            else:
                # If the model returns a descriptive name already
                final_disease_name = label_str

        if not final_disease_name:
            final_disease_name = str(label) if label is not None else "Unknown"

        # Normalize the disease name for lookup in DISEASE_INFO
        # Example: "Tomato___healthy" -> "healthy", "Corn (maize) - Common rust " -> "common_rust"
        disease_lookup_key = final_disease_name.lower().strip()
        
        # Handle Plant Village style separators
        if '___' in disease_lookup_key:
            disease_lookup_key = disease_lookup_key.split('___')[1]
        elif ' - ' in disease_lookup_key:
            # For "Corn (maize) - Common rust ", pick the part after '-'
            parts = disease_lookup_key.split(' - ')
            disease_lookup_key = parts[-1]
            
        # Standardize for dictionary lookup: replace spaces/hyphens with underscore, remove parentheses
        disease_lookup_key = disease_lookup_key.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
        # Remove multiple underscores and trailing/leading underscores
        disease_lookup_key = re.sub(r'_+', '_', disease_lookup_key).strip('_')
        
        disease_info = DISEASE_INFO.get(disease_lookup_key, {
            'treatment': 'Consult with an agricultural expert for specific treatment.',
            'severity': 'Unknown',
            'actions': ['Monitor the plant closely', 'Consult with a local expert']
        })

        return jsonify({
            'success': True,
            'classification': {
                'disease': final_disease_name.replace('___', ' - ').replace('_', ' '),
                'disease_id': disease_lookup_key,
                'confidence': float(confidence),
                'severity': disease_info.get('severity', 'Unknown'),
                'treatment': disease_info.get('treatment'),
                'recommended_actions': disease_info.get('actions', []),
                'timestamp': timestamp or datetime.now().isoformat(),
                'provider': 'bytez'
            }
        }), 200
    
    except Exception as e:
        print(f"[ERROR] Endpoint exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/api/disease-info/<disease_name>', methods=['GET'])
def get_disease_info(disease_name):
    """Get detailed information about a specific disease"""
    disease_name = disease_name.lower().replace('-', '_')
    
    if disease_name not in DISEASE_INFO:
        return jsonify({
            'error': f'Disease "{disease_name}" not found',
            'available_diseases': list(DISEASE_INFO.keys())
        }), 404
    
    info = DISEASE_INFO[disease_name]
    return jsonify({
        'disease': disease_name,
        'details': info
    }), 200

@app.route('/api/diseases-list', methods=['GET'])
def get_diseases_list():
    """Get list of all classified diseases"""
    return jsonify({
        'diseases': list(DISEASE_INFO.keys()),
        'count': len(DISEASE_INFO)
    }), 200


@app.route('/api/bytez-diagnose', methods=['GET'])
def bytez_diagnose():
    """
    Diagnose Bytez connectivity and model availability.
    Returns the endpoint URL, HTTP status for an OPTIONS request, and headers.
    """
    test_url = f"https://api.bytez.com/models/v2/{DISEASE_MODEL_NAME}"

    headers = {
        "Authorization": f"Bearer {BYTEZ_API_KEY}"
    }

    try:
        # Use OPTIONS to probe the endpoint without sending a file
        r = requests.options(test_url, headers=headers, timeout=10)

        return jsonify({
            'bytez_endpoint': test_url,
            'http_status': r.status_code,
            'headers': dict(r.headers),
            'hint': (
                "404 = model slug not exposed via REST or not deployed. "
                "Check Bytez dashboard -> model -> REST availability."
            )
        }), 200

    except Exception as e:
        return jsonify({
            'error': str(e),
            'hint': 'Failed to reach Bytez API'
        }), 500

if __name__ == '__main__':
    print("Starting Crop Yield Prediction API Server...")
    print("Server running on http://localhost:5000")
    print("API Documentation: http://localhost:5000/api/")
    app.run(debug=True, host='0.0.0.0', port=5000)
