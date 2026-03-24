#!/usr/bin/env python3
"""
Plant Disease Classification Setup Script
Sets up Bytez API integration for disease detection
"""

import os
import sys
import json
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

BYTEZ_API_KEY_DEFAULT = "64e297d5c105bf11beff0d17c16bf41f"
DISEASE_MODEL_OPTIONS = [
    "Falconsai/plant-disease-detection",
    "Falconsai/crop-disease-detector",
    "Falconsai/nsfw_image_detection"  # Default (temporary)
]

CONFIG_FILE = Path(__file__).parent / ".disease_config.json"
BACKEND_FILE = Path(__file__).parent / "backend" / "app.py"

# ============================================================================
# SETUP FUNCTIONS
# ============================================================================

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")

def print_section(title):
    """Print a formatted section"""
    print(f"\n▶ {title}")
    print("-" * 70)

def check_dependencies():
    """Check if required packages are installed"""
    print_section("Checking Dependencies")
    
    required_packages = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'requests': 'requests'
    }
    
    missing = []
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✓ {package_name} is installed")
        except ImportError:
            print(f"✗ {package_name} is NOT installed")
            missing.append(package_name)
    
    if missing:
        print(f"\n⚠ Missing packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    
    print("\n✓ All dependencies are installed!")
    return True

def configure_api_key():
    """Configure Bytez API key"""
    print_section("Configuring Bytez API Key")
    
    # Check environment variable
    env_key = os.getenv('BYTEZ_API_KEY')
    if env_key:
        print(f"✓ Found API key in environment variable: {env_key[:10]}...")
        return env_key
    
    print("No API key found in environment variable BYTEZ_API_KEY")
    print(f"\nDefault API key available:")
    print(f"  {BYTEZ_API_KEY_DEFAULT[:10]}...")
    
    choice = input("\nUse default API key? (y/n): ").strip().lower()
    
    if choice == 'y':
        print("Using default API key")
        return BYTEZ_API_KEY_DEFAULT
    else:
        api_key = input("\nEnter your Bytez API key: ").strip()
        if api_key:
            return api_key
        else:
            print("No API key provided. Using default.")
            return BYTEZ_API_KEY_DEFAULT

def select_model():
    """Select disease detection model"""
    print_section("Selecting Disease Detection Model")
    
    print("Available models:")
    for i, model in enumerate(DISEASE_MODEL_OPTIONS, 1):
        marker = " (default)" if i == 3 else ""
        print(f"  {i}. {model}{marker}")
    
    choice = input("\nSelect model (1-3, or 3 for default): ").strip()
    
    model_map = {
        '1': DISEASE_MODEL_OPTIONS[0],
        '2': DISEASE_MODEL_OPTIONS[1],
        '3': DISEASE_MODEL_OPTIONS[2]
    }
    
    selected = model_map.get(choice, DISEASE_MODEL_OPTIONS[2])
    print(f"✓ Selected model: {selected}")
    return selected

def save_configuration(api_key, model):
    """Save configuration to file"""
    config = {
        'api_key': api_key,
        'model': model,
        'setup_date': str(Path(BACKEND_FILE).stat().st_mtime)
    }
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Configuration saved to {CONFIG_FILE}")

def verify_backend_setup():
    """Verify backend setup"""
    print_section("Verifying Backend Setup")
    
    if not BACKEND_FILE.exists():
        print(f"✗ Backend file not found: {BACKEND_FILE}")
        return False
    
    with open(BACKEND_FILE, 'r') as f:
        content = f.read()
    
    checks = [
        ('disease_classification_endpoint', 'Disease classification endpoint'),
        ('classify_plant_disease', 'Disease classification function'),
        ('DISEASE_INFO', 'Disease information database'),
        ('get_disease_info', 'Disease info endpoint'),
        ('get_diseases_list', 'Diseases list endpoint')
    ]
    
    all_ok = True
    for check_str, description in checks:
        if check_str in content:
            print(f"✓ {description} - Found")
        else:
            print(f"✗ {description} - NOT found")
            all_ok = False
    
    return all_ok

def verify_frontend_setup():
    """Verify frontend setup"""
    print_section("Verifying Frontend Setup")
    
    disease_html = Path(__file__).parent / "frontend" / "disease_classification.html"
    main_html = Path(__file__).parent / "frontend" / "index.html"
    
    if not disease_html.exists():
        print(f"✗ Disease classification page not found: {disease_html}")
        return False
    else:
        print(f"✓ Disease classification page found")
    
    with open(main_html, 'r') as f:
        content = f.read()
    
    if 'disease_classification.html' in content:
        print(f"✓ Main page has navigation link to disease classification")
    else:
        print(f"⚠ Main page may need navigation link update")
    
    return True

def test_api_endpoints():
    """Provide test commands for API endpoints"""
    print_section("API Endpoints for Testing")
    
    endpoints = [
        {
            'name': 'Classify Disease',
            'method': 'POST',
            'endpoint': '/api/disease-classification',
            'example': 'curl -X POST http://localhost:5000/api/disease-classification -H "Content-Type: application/json" -d \'{"image_url":"https://example.com/plant.jpg"}\''
        },
        {
            'name': 'Get Disease Info',
            'method': 'GET',
            'endpoint': '/api/disease-info/{disease_name}',
            'example': 'curl http://localhost:5000/api/disease-info/early_blight'
        },
        {
            'name': 'List Diseases',
            'method': 'GET',
            'endpoint': '/api/diseases-list',
            'example': 'curl http://localhost:5000/api/diseases-list'
        }
    ]
    
    for ep in endpoints:
        print(f"\n{ep['name']} - {ep['method']}")
        print(f"  Endpoint: {ep['endpoint']}")
        print(f"  Test: {ep['example']}")

def print_next_steps():
    """Print next steps"""
    print_section("Next Steps")
    
    steps = [
        "1. Install dependencies:",
        "   pip install -r backend/requirements.txt",
        "",
        "2. Start the backend server:",
        "   python backend/app.py",
        "",
        "3. Open in browser:",
        "   - Main app: http://localhost:5000",
        "   - Disease classification: http://localhost:5000/disease_classification.html",
        "",
        "4. Test the API:",
        "   - Upload a plant image",
        "   - Or use curl commands above to test endpoints",
        "",
        "5. For production use:",
        "   - Replace mock classification with real Bytez API calls",
        "   - Set BYTEZ_API_KEY environment variable",
        "   - Configure appropriate disease detection model",
        "",
        "📚 Documentation: See DISEASE_CLASSIFICATION_GUIDE.md"
    ]
    
    for step in steps:
        print(step)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print_header("Plant Disease Classification - Setup")
    
    # Check dependencies
    if not check_dependencies():
        print("\n⚠ Please install missing packages and try again.")
        sys.exit(1)
    
    # Configure API
    api_key = configure_api_key()
    
    # Select model
    model = select_model()
    
    # Save configuration
    save_configuration(api_key, model)
    
    # Verify setup
    print("\n" + "=" * 70)
    print("  Verifying Installation")
    print("=" * 70)
    
    backend_ok = verify_backend_setup()
    frontend_ok = verify_frontend_setup()
    
    if backend_ok and frontend_ok:
        print("\n✓ Setup verification PASSED!")
    else:
        print("\n⚠ Setup verification found some issues. Please review above.")
    
    # Show test endpoints
    test_api_endpoints()
    
    # Print next steps
    print_next_steps()
    
    print_header("Setup Complete!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Setup interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error during setup: {e}")
        sys.exit(1)
