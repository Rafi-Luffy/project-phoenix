#!/bin/bash

# Phoenix Setup Script

set -e

echo " Phoenix - Self-Healing Agentic AI Framework Setup"
echo "===================================================="
echo ""

# Check Python version
echo " Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo " Python 3.11+ is required"
    exit 1
fi

# Check Docker
echo " Checking Docker..."
docker --version
if [ $? -ne 0 ]; then
    echo "  Docker not found. Docker is optional but recommended for sandbox isolation."
fi

# Create virtual environment
echo " Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo " Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo " Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo " Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "  IMPORTANT: Please edit .env and add your API keys:"
    echo "   - OPENAI_API_KEY (for GPT-4)"
    echo "   - GEMINI_API_KEY (for Gemini)"
    echo "   - ANTHROPIC_API_KEY (for Claude)"
    echo ""
    echo "   At least one API key is required!"
    echo ""
fi

# Create required directories
echo " Creating required directories..."
mkdir -p data workspaces logs sandboxes

# Initialize database (if using Docker)
echo "  Database setup options:"
echo "   1. Use Docker Compose (recommended): docker-compose up -d"
echo "   2. Use local PostgreSQL: Update DATABASE_URL in .env"
echo ""

echo " Setup complete!"
echo ""
echo " Quick Start:"
echo "   1. Edit .env and add your LLM API key"
echo "   2. Start services: docker-compose up -d"
echo "   3. Run Phoenix: python -m phoenix.main"
echo "   4. Open http://localhost:8000/docs for API documentation"
echo ""
echo " Next steps:"
echo "   - Read README.md for detailed documentation"
echo "   - Try the example project in examples/calculator-buggy/"
echo "   - Check out the API at http://localhost:8000"
echo ""
echo " Phoenix is ready to heal your code!"
