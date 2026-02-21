#!/bin/bash
# Project Phoenix - Production Deployment Script
# One-command deployment for entire stack

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENVIRONMENT="${1:-production}"

echo "════════════════════════════════════════════════════════════════"
echo "  PROJECT PHOENIX - PRODUCTION DEPLOYMENT"
echo "  Database: PostgreSQL 15 (Free, Open-Source)"
echo "  LLM: Ollama + Mistral 7B ($0 forever)"
echo "  Framework: 7-Phase Autonomous System"
echo "════════════════════════════════════════════════════════════════"

# Check prerequisites
echo ""
echo "📋 Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not installed. Install from https://docker.com"
    exit 1
fi
echo "✅ Docker: $(docker --version)"

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not installed"
    exit 1
fi
echo "✅ Docker Compose: $(docker-compose --version)"

# Create .env file if not exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo ""
    echo "🔐 Creating .env file with secure defaults..."
    cat > "$PROJECT_DIR/.env" << EOF
# PostgreSQL
DB_PASSWORD=$(openssl rand -base64 32)
POSTGRES_USER=phoenix_user
POSTGRES_DB=phoenix_db

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
FLASK_ENV=production

# Ollama
OLLAMA_HOST=http://ollama:11434
EOF
    echo "✅ .env created (secure password generated)"
fi

# Build images
echo ""
echo "🔨 Building Docker images..."
docker-compose -f "$PROJECT_DIR/docker-compose.prod.yml" build --no-cache

# Start services
echo ""
echo "🚀 Starting services..."
docker-compose -f "$PROJECT_DIR/docker-compose.prod.yml" up -d

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 5

# Check database
echo "  Checking PostgreSQL..."
for i in {1..30}; do
    if docker-compose -f "$PROJECT_DIR/docker-compose.prod.yml" exec -T postgres pg_isready -U phoenix_user > /dev/null 2>&1; then
        echo "  ✅ PostgreSQL is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "  ❌ PostgreSQL failed to start"
        exit 1
    fi
    sleep 1
done

# Check Ollama
echo "  Checking Ollama..."
for i in {1..60}; do
    if docker-compose -f "$PROJECT_DIR/docker-compose.prod.yml" exec -T ollama curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "  ✅ Ollama is ready"
        break
    fi
    if [ $i -eq 60 ]; then
        echo "  ❌ Ollama failed to start (model download may take time)"
    fi
    echo -n "."
    sleep 1
done
echo ""

# Check Phoenix app
echo "  Checking Project Phoenix..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "  ✅ Project Phoenix is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "  ⚠️  Phoenix may still be initializing"
    fi
    sleep 1
done

# Show status
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  ✅ DEPLOYMENT COMPLETE"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "🌐 Services running:"
echo "  📱 Project Phoenix: http://localhost:8000"
echo "  🤖 Ollama API: http://localhost:11434"
echo "  🗄️  PostgreSQL: localhost:5432"
echo ""
echo "📊 Endpoints:"
echo "  GET  http://localhost:8000/health          - System health"
echo "  GET  http://localhost:8000/llm/health      - LLM status"
echo "  POST http://localhost:8000/llm/analyze_error"
echo "  POST http://localhost:8000/llm/detect_patterns"
echo "  POST http://localhost:8000/llm/optimize"
echo ""
echo "💾 Database:"
echo "  Host: localhost:5432"
echo "  Database: phoenix_db"
echo "  User: phoenix_user"
echo "  (Password in .env file)"
echo ""
echo "📋 Logs:"
docker-compose -f "$PROJECT_DIR/docker-compose.prod.yml" logs -f --tail=50
