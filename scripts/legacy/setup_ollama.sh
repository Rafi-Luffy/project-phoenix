#!/bin/bash

# OLLAMA QUICK START SCRIPT
# Installs Ollama and pulls free LLM models
# Works on macOS, Linux, Windows (WSL)

set -e

echo "🚀 Project Phoenix - Free LLM Setup"
echo "===================================="
echo ""

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
else
    echo "⚠️  Unsupported OS. Please install Ollama manually:"
    echo "   https://ollama.ai/download"
    exit 1
fi

echo "📦 Detected OS: $OS"
echo ""

# Check if Ollama is already installed
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is already installed!"
    OLLAMA_INSTALLED=true
else
    echo "⚠️  Ollama not found. Installing..."
    OLLAMA_INSTALLED=false
fi

echo ""
echo "Installing/Verifying Ollama..."
echo "================================"

if [ "$OS" == "macos" ]; then
    # macOS installation
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew not found. Install from https://brew.sh"
        exit 1
    fi
    
    if [ "$OLLAMA_INSTALLED" = false ]; then
        echo "Installing Ollama via Homebrew..."
        brew install ollama
        echo "✅ Ollama installed successfully!"
    fi
    
    # Start Ollama service (macOS)
    echo ""
    echo "Starting Ollama service..."
    brew services start ollama 2>/dev/null || true
    sleep 2
    
elif [ "$OS" == "linux" ]; then
    # Linux installation
    if [ "$OLLAMA_INSTALLED" = false ]; then
        echo "Installing Ollama..."
        curl -fsSL https://ollama.ai/install.sh | sh
        echo "✅ Ollama installed successfully!"
    fi
    
    # Start Ollama service (Linux)
    echo ""
    echo "Starting Ollama service..."
    sudo systemctl start ollama 2>/dev/null || ollama serve &
    sleep 2
fi

echo ""
echo "Verifying Ollama is running..."
echo "================================"

# Wait for Ollama to be ready
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama is running at http://localhost:11434"
        break
    fi
    echo "⏳ Waiting for Ollama to start... ($((attempt + 1))/$max_attempts)"
    sleep 1
    attempt=$((attempt + 1))
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Ollama failed to start. Please check installation."
    echo ""
    echo "Troubleshooting:"
    if [ "$OS" == "macos" ]; then
        echo "  1. Check if running: brew services list"
        echo "  2. Start manually: ollama serve"
        echo "  3. Check logs: /var/log/ollama.log"
    else
        echo "  1. Check if running: systemctl status ollama"
        echo "  2. Start manually: ollama serve"
        echo "  3. Check logs: journalctl -u ollama"
    fi
    exit 1
fi

echo ""
echo "📥 Downloading Free LLM Models"
echo "================================"
echo ""
echo "Available models:"
echo "  1. Mistral 7B      (4.1GB) ⭐ RECOMMENDED - Best balance"
echo "  2. LLaMA 2 7B      (3.8GB) - Fastest, smaller"
echo "  3. Zephyr 7B       (4.1GB) - Conversational"
echo "  4. Neural Chat 7B  (4.7GB) - Specialized tasks"
echo "  5. All of the above"
echo ""

# Default to Mistral
MODEL_CHOICE=${1:-1}

models_to_pull=()

case $MODEL_CHOICE in
    1)
        models_to_pull=("mistral")
        echo "Selected: Mistral 7B (recommended)"
        ;;
    2)
        models_to_pull=("llama2")
        echo "Selected: LLaMA 2 7B"
        ;;
    3)
        models_to_pull=("zephyr")
        echo "Selected: Zephyr 7B"
        ;;
    4)
        models_to_pull=("neural-chat")
        echo "Selected: Neural Chat 7B"
        ;;
    5)
        models_to_pull=("mistral" "llama2" "zephyr" "neural-chat")
        echo "Selected: All models"
        ;;
    *)
        models_to_pull=("mistral")
        echo "Invalid choice, using Mistral 7B"
        ;;
esac

echo ""
echo "Downloading models..."

for model in "${models_to_pull[@]}"; do
    echo ""
    echo "📥 Pulling $model..."
    ollama pull "$model"
    if [ $? -eq 0 ]; then
        echo "✅ $model installed successfully!"
    else
        echo "⚠️  Failed to download $model"
    fi
done

echo ""
echo "Verifying installed models..."
echo "==============================="
ollama list

echo ""
echo "✅ Ollama Setup Complete!"
echo ""
echo "Usage:"
echo "======"
echo ""
echo "1. Ollama is running on http://localhost:11434"
echo ""
echo "2. Start Project Phoenix:"
echo "   docker-compose -f docker-compose.complete.yml up -d"
echo ""
echo "3. Access the system:"
echo "   - Frontend: http://localhost:8080"
echo "   - Backend API: http://localhost:8000"
echo "   - Grafana Dashboard: http://localhost:3000"
echo "   - Prometheus: http://localhost:9090"
echo ""
echo "4. Test LLM integration:"
echo "   pytest tests/test_llm_integration.py -v"
echo ""
echo "5. View Ollama models:"
echo "   ollama list"
echo ""
echo "6. Change model (optional):"
echo "   export OLLAMA_MODEL=llama2  # or zephyr, neural-chat"
echo ""
echo "Cost: $0/month forever ✨"
echo ""
echo "Happy autonomous healing! 🤖"
