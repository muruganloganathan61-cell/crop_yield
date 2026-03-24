#!/bin/bash
# Setup script for Linux/Mac

echo "🌾 Crop Yield Prediction System - Setup"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Found: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.8+${NC}"
    exit 1
fi

# Check pip
echo "Checking pip installation..."
if command -v pip3 &> /dev/null; then
    echo -e "${GREEN}✓ pip3 found${NC}"
else
    echo -e "${RED}✗ pip3 not found${NC}"
    exit 1
fi

# Create virtual environment (optional but recommended)
echo ""
echo "Setting up Python environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Train ML Models
echo ""
echo "Training ML models..."
cd ml_models
pip install -r requirements.txt > /dev/null 2>&1
echo "Running train_models.py..."
python3 train_models.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Models trained successfully${NC}"
else
    echo -e "${RED}✗ Model training failed${NC}"
    exit 1
fi

# Setup Backend
echo ""
echo "Setting up Backend..."
cd ../backend
pip install -r requirements.txt > /dev/null 2>&1
echo -e "${GREEN}✓ Backend dependencies installed${NC}"

# Setup Frontend
echo ""
echo "Frontend setup complete (static files)"

echo ""
echo "========================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Start Backend: cd backend && python3 app.py"
echo "2. Start Frontend: cd frontend && python3 -m http.server 8000"
echo "3. Open browser: http://localhost:8000"
echo ""
echo "For more information, see README.md"
