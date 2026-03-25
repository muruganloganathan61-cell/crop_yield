/**
 * Crop Yield Prediction System - Frontend JavaScript
 * Handles form submission, API calls, and result rendering
 */

// ============================================================================
// CONFIGURATION
// ============================================================================

// Use explicit backend URL so POSTs go to the Flask API when frontend
// is served by a static server on a different port (e.g., :8080).
const API_BASE_URL = 'http://localhost:5000/api';
const TIMEOUT = 10000; // 10 seconds

// ============================================================================
// DOM ELEMENTS
// ============================================================================

const form = document.getElementById('predictionForm');
const loadingIndicator = document.getElementById('loadingIndicator');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const errorMessage = document.getElementById('errorMessage');

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    form.addEventListener('submit', handleFormSubmit);

    // Load data ranges for validation
    loadDataRanges();
});

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Fetch data ranges from API for client-side validation
 */
async function loadDataRanges() {
    try {
        const response = await fetch(`${API_BASE_URL}/data-ranges`);
        if (!response.ok) {
            console.warn('Could not load data ranges from API');
        }
    } catch (error) {
        console.warn('API connection unavailable. Running offline mode.');
    }
}

/**
 * Show error message
 */
function showError(message) {
    errorMessage.textContent = message;
    errorSection.style.display = 'block';
    resultsSection.style.display = 'none';
    form.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Hide error message
 */
function hideError() {
    errorSection.style.display = 'none';
}

/**
 * Show loading indicator
 */
function showLoading() {
    loadingIndicator.style.display = 'block';
    resultsSection.style.display = 'none';
    hideError();
}

/**
 * Hide loading indicator
 */
function hideLoading() {
    loadingIndicator.style.display = 'none';
}

/**
 * Validate form inputs on client side
 */
function validateForm(formData) {
    const errors = [];

    const numericFields = [
        'nitrogen', 'phosphorus', 'potassium', 'ph',
        'moisture', 'temperature', 'rainfall', 'humidity'
    ];

    numericFields.forEach(field => {
        const value = parseFloat(formData[field]);
        if (isNaN(value)) {
            errors.push(`${field} must be a number`);
        }
    });

    if (!formData.soil_type) {
        errors.push('Soil type is required');
    }

    if (!formData.crop_type) {
        errors.push('Crop type is required');
    }

    return errors;
}

/**
 * Format number to 2 decimal places
 */
function formatNumber(num) {
    return parseFloat(num).toFixed(2);
}

// ============================================================================
// FORM HANDLING
// ============================================================================

/**
 * Handle form submission
 */
async function handleFormSubmit(event) {
    event.preventDefault();
    hideError();

    // Get form data
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    // Validate form
    const validationErrors = validateForm(data);
    if (validationErrors.length > 0) {
        showError(`Validation Error: ${validationErrors.join(', ')}`);
        return;
    }

    showLoading();

    try {
        // Make prediction
        await makePrediction(data);
    } catch (error) {
        showError(`Error: ${error.message}`);
    } finally {
        hideLoading();
    }
}

/**
 * Safely parse JSON from response
 */
async function safeParseJSON(response) {
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
        return await response.json();
    } else {
        const text = await response.text();
        console.error('Expected JSON but got:', text.substring(0, 100));
        throw new Error(`Server returned ${response.status} ${response.statusText}. Please ensure the backend is running.`);
    }
}

/**
 * Make API call to predict yield and get recommendations
 */
async function makePrediction(formData) {
    try {
        // Call predict endpoint
        const predictionResponse = await fetch(`${API_BASE_URL}/predict-yield`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (!predictionResponse.ok) {
            let errorMessage = 'Yield prediction failed';
            try {
                const errorData = await safeParseJSON(predictionResponse);
                errorMessage = errorData.error || errorData.errors ? JSON.stringify(errorData.errors) : errorMessage;
            } catch (e) {
                errorMessage = e.message;
            }
            throw new Error(errorMessage);
        }

        const predictionData = await safeParseJSON(predictionResponse);

        // Call recommendation endpoint
        const recommendationResponse = await fetch(`${API_BASE_URL}/recommend`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (!recommendationResponse.ok) {
            let errorMessage = 'Recommendation failed';
            try {
                const errorData = await safeParseJSON(recommendationResponse);
                errorMessage = errorData.error || errorMessage;
            } catch (e) {
                errorMessage = e.message;
            }
            throw new Error(errorMessage);
        }

        const recommendationData = await safeParseJSON(recommendationResponse);

        // Display results
        displayResults(predictionData, recommendationData, formData);

    } catch (error) {
        throw new Error(error.message || 'Failed to communicate with server');
    }
}

// ============================================================================
// RESULT DISPLAY
// ============================================================================

/**
 * Display prediction and recommendation results
 */
function displayResults(predictionData, recommendationData, formData) {
    if (!predictionData.success || !recommendationData.success) {
        showError('Failed to process prediction. Please check your input.');
        return;
    }

    // Display yield prediction
    displayYieldPrediction(predictionData, formData);

    // Display weather analysis
    displayWeatherAnalysis(predictionData);

    // Display soil analysis
    displaySoilAnalysis(predictionData);

    // Display seed recommendation
    displaySeedRecommendation(recommendationData);

    // Display fertilizer recommendation
    displayFertilizerRecommendation(recommendationData);

    // Show results section
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Display yield prediction card
 */
function displayYieldPrediction(data, formData) {
    const yieldValue = document.getElementById('yieldValue');
    const yieldCrop = document.getElementById('yieldCrop');

    const prediction = data.prediction;
    yieldValue.textContent = formatNumber(prediction.yield_estimate);
    yieldCrop.textContent = `Expected yield for ${formData.crop_type}`;
}

/**
 * Display weather analysis
 */
function displayWeatherAnalysis(data) {
    const weatherTemp = document.getElementById('weatherTemp');
    const weatherRain = document.getElementById('weatherRain');
    const weatherHumidity = document.getElementById('weatherHumidity');
    const weatherWarnings = document.getElementById('weatherWarnings');

    const weather = data.weather_analysis;
    weatherTemp.textContent = `${formatNumber(weather.temperature)}°C`;
    weatherRain.textContent = `${formatNumber(weather.rainfall)}mm`;
    weatherHumidity.textContent = `${formatNumber(weather.humidity)}%`;

    // Display warnings
    weatherWarnings.innerHTML = '';
    if (weather.warnings && weather.warnings.length > 0) {
        weather.warnings.forEach(warning => {
            const warningEl = document.createElement('div');
            warningEl.className = 'warning';
            warningEl.textContent = warning;
            weatherWarnings.appendChild(warningEl);
        });
    }
}

/**
 * Display soil analysis
 */
function displaySoilAnalysis(data) {
    const soilAnalysisDiv = document.getElementById('soilAnalysis');
    soilAnalysisDiv.innerHTML = '';

    const suggestions = data.soil_analysis || [];
    suggestions.forEach(nutrient => {
        const itemEl = document.createElement('div');
        itemEl.className = 'nutrient-item';

        let levelClass = 'level-optimal';
        if (nutrient.level === 'Low' || nutrient.level === 'Acidic' ||
            nutrient.level === 'Very Acidic' || nutrient.level === 'Very Alkaline') {
            levelClass = 'level-low';
        } else if (nutrient.level === 'High' || nutrient.level === 'Alkaline') {
            levelClass = 'level-high';
        }

        itemEl.innerHTML = `
            <h4>${nutrient.nutrient}</h4>
            <div class="nutrient-level ${levelClass}">${nutrient.level} (${formatNumber(nutrient.value)})</div>
            <div class="nutrient-recommendation">${nutrient.recommendation}</div>
        `;

        soilAnalysisDiv.appendChild(itemEl);
    });
}

/**
 * Display seed recommendation
 */
function displaySeedRecommendation(data) {
    const seedName = document.getElementById('seedName');
    const seedConfidence = document.getElementById('seedConfidence');
    const seedReason = document.getElementById('seedReason');

    const rec = data.recommendations.seed;
    seedName.textContent = rec.recommended_crop;
    seedConfidence.textContent = `${rec.confidence}% Confidence`;
    seedReason.textContent = rec.reason;
}

/**
 * Display fertilizer recommendation
 */
function displayFertilizerRecommendation(data) {
    const fertilizerName = document.getElementById('fertilizerName');
    const fertilizerConfidence = document.getElementById('fertilizerConfidence');
    const fertilizerReason = document.getElementById('fertilizerReason');
    const fertilizerDetails = document.getElementById('fertilizerDetails');

    const rec = data.recommendations.fertilizer;
    fertilizerName.textContent = rec.recommended_type;
    fertilizerConfidence.textContent = `${rec.confidence}% Confidence`;
    fertilizerReason.textContent = rec.reason;

    // Display fertilizer details
    const details = rec.details;
    let detailsHTML = `
        <h5>${rec.recommended_type}</h5>
        <p><strong>Quantity:</strong> ${details.quantity}</p>
        <p><strong>Application Time:</strong> ${details.application_time}</p>
        <p><strong>Description:</strong> ${details.description}</p>
        <p><strong>Soil Type:</strong> ${rec.soil_type}</p>
    `;

    fertilizerDetails.innerHTML = detailsHTML;
}

// ============================================================================
// FORM VALIDATION FEEDBACK
// ============================================================================

/**
 * Add real-time validation feedback
 */
document.addEventListener('DOMContentLoaded', () => {
    const inputs = form.querySelectorAll('input[type="number"]');

    inputs.forEach(input => {
        input.addEventListener('change', () => {
            validateInputField(input);
        });

        input.addEventListener('blur', () => {
            validateInputField(input);
        });
    });
});

/**
 * Validate individual input field
 */
function validateInputField(input) {
    const value = parseFloat(input.value);
    const min = parseFloat(input.min);
    const max = parseFloat(input.max);

    if (isNaN(value) || value < min || value > max) {
        input.style.borderColor = '#e74c3c';
    } else {
        input.style.borderColor = '#ddd';
    }
}

// ============================================================================
// API FALLBACK (Offline Mode)
// ============================================================================

/**
 * Generate mock prediction for offline mode
 */
function generateMockPrediction(formData) {
    const baseYield = 5000 +
        formData.nitrogen * 20 +
        formData.phosphorus * 15 +
        formData.potassium * 10 +
        (8 - Math.abs(formData.ph - 7)) * 200 +
        formData.rainfall * 2;

    return {
        success: true,
        prediction: {
            yield_estimate: Math.max(baseYield + (Math.random() - 0.5) * 1000, 1000),
            yield_unit: 'kg/hectare',
            crop_type: formData.crop_type
        },
        soil_analysis: [
            { nutrient: 'Nitrogen', level: 'Optimal', value: formData.nitrogen, recommendation: 'Current N levels are good' },
            { nutrient: 'Phosphorus', level: 'Optimal', value: formData.phosphorus, recommendation: 'P levels are adequate' },
            { nutrient: 'Potassium', level: 'Optimal', value: formData.potassium, recommendation: 'K levels are sufficient' },
            { nutrient: 'Soil pH', level: 'Optimal', value: formData.ph, recommendation: 'pH is in optimal range' }
        ],
        weather_analysis: {
            temperature: formData.temperature,
            rainfall: formData.rainfall,
            humidity: formData.humidity,
            warnings: []
        }
    };
}

/**
 * Generate mock recommendations for offline mode
 */
function generateMockRecommendations(formData) {
    const crops = ['Rice', 'Wheat', 'Corn', 'Soybean', 'Barley'];
    const fertilizers = ['NPK 15-15-15', 'NPK 10-26-26', 'NPK 12-32-16', 'NPK 20-20-0', 'Organic Compost'];

    return {
        success: true,
        recommendations: {
            seed: {
                recommended_crop: formData.crop_type,
                confidence: 85 + Math.random() * 10,
                reason: 'Well-suited to your soil and weather conditions'
            },
            fertilizer: {
                recommended_type: fertilizers[Math.floor(Math.random() * fertilizers.length)],
                confidence: 80 + Math.random() * 15,
                details: {
                    quantity: '100-150 kg/hectare',
                    application_time: 'Pre-planting',
                    description: 'Balanced NPK formulation'
                },
                soil_type: formData.soil_type,
                reason: 'Selected based on your soil conditions'
            }
        }
    };
}

console.log('Crop Yield Prediction System loaded successfully!');
console.log(`API Base URL: ${API_BASE_URL}`);
