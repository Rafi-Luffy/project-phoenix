#!/bin/bash
# Quick Start - Local Development

set -e

echo "════════════════════════════════════════════════════════════════"
echo "  PROJECT PHOENIX - QUICK START (Development)"
echo "════════════════════════════════════════════════════════════════"
echo ""

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if Ollama is running
echo "📍 Checking Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "❌ Ollama not running. Start with: ollama serve"
    echo ""
    echo "Optional: To enable LLM features:"
    echo "  1. Install Ollama: https://ollama.ai"
    echo "  2. Run: ollama serve"
    echo "  3. In another terminal: ollama pull mistral"
    echo ""
    echo "⚠️  Continuing without LLM (rule-based mode only)..."
else
    echo "✅ Ollama running"
fi

# Install/upgrade Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip install -q -r "$PROJECT_DIR/requirements.txt" || pip3 install -q -r "$PROJECT_DIR/requirements.txt"

# Start Project Phoenix
echo ""
echo "🚀 Starting Project Phoenix..."
python3.11 "$PROJECT_DIR/main.py" &

# Wait for service to start
sleep 3

# Test health check
echo ""
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Project Phoenix is running!"
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "  🌐 Available at: http://localhost:8000"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo "📊 API Endpoints:"
    echo "  GET  http://localhost:8000/health           - System health"
    echo "  GET  http://localhost:8000/llm/health       - LLM status"
    echo "  POST http://localhost:8000/llm/analyze_error"
    echo ""
    echo "🛑 To stop: Press Ctrl+C"
    echo ""
    # Keep running
    wait
else
    echo "❌ Failed to start Project Phoenix"
    exit 1
fi
