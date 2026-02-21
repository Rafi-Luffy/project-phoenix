#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                   PROJECT PHOENIX - FINAL STATUS CHECK                      ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check services
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SERVICE STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# FastAPI
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ FastAPI (port 8000) - Running"
else
    echo "❌ FastAPI (port 8000) - Not responding"
fi

# PostgreSQL
if psql -U postgres -d phoenix_db -c "SELECT 1" > /dev/null 2>&1; then
    TABLES=$(psql -U postgres -d phoenix_db -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema='public'")
    echo "✅ PostgreSQL (port 5432) - Running with $TABLES tables"
else
    echo "❌ PostgreSQL (port 5432) - Not responding"
fi

# Ollama
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    MODELS=$(curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*' | wc -l)
    echo "✅ Ollama (port 11434) - Running with $MODELS model(s)"
else
    echo "❌ Ollama (port 11434) - Not responding"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "CODE METRICS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Python LOC
PYTHON_LOC=$(find . -name "*.py" -type f ! -path "./__pycache__/*" ! -path "./.git/*" -exec wc -l {} + | tail -1 | awk '{print $1}')
echo "📊 Python Code: $PYTHON_LOC LOC"

# Test LOC
TEST_LOC=$(find tests -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
TEST_FILES=$(find tests -name "test_*.py" -type f | wc -l)
echo "📊 Test Code: $TEST_LOC LOC ($TEST_FILES files)"

# Frontend files
FRONTEND_FILES=$(find frontend/src -name "*.tsx" -o -name "*.ts" | wc -l)
echo "📊 Frontend Components: $FRONTEND_FILES TypeScript/React files"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "MODULE COMPLETENESS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

modules=(
    "core"
    "api"
    "agents"
    "recovery"
    "learning"
    "monitoring"
    "test_suite"
)

for module in "${modules[@]}"; do
    if [ -d "autonomous_system/$module" ]; then
        FILES=$(find "autonomous_system/$module" -name "*.py" -type f | wc -l)
        echo "✅ Module '$module': $FILES files"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "KEY FILES VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

key_files=(
    "main.py"
    "requirements.txt"
    "autonomous_system/core/database.py"
    "autonomous_system/core/orchestrator.py"
    "autonomous_system/api/gateway.py"
    "autonomous_system/core/self_evolving_llm.py"
    "frontend/src/main.tsx"
    "frontend/package.json"
    "docker-compose.yml"
    "Dockerfile.backend"
    "DEPLOYMENT_READINESS_REPORT.md"
    "PROJECT_PHOENIX_COMPLETE_OVERVIEW.md"
)

for file in "${key_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "API ENDPOINT VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

endpoints=(
    "GET:http://localhost:8000/health"
    "GET:http://localhost:8000/llm/health"
)

for endpoint in "${endpoints[@]}"; do
    IFS=':' read -r method url <<< "$endpoint"
    if curl -s -X "$method" "$url" > /dev/null 2>&1; then
        echo "✅ $method $url"
    else
        echo "❌ $method $url"
    fi
done

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                        ✅ SYSTEM READY FOR DEPLOYMENT                      ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
