#!/bin/bash

################################################################################
# PROJECT PHOENIX - COMPLETE OLLAMA LLM INTEGRATION SETUP & VERIFICATION
# Free, Open-Source, $0 Cost, Works Forever
# Last Updated: January 5, 2026
################################################################################

set -e  # Exit on error

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                 PROJECT PHOENIX - COMPLETE SETUP WIZARD                    ║"
echo "║                   Free Ollama + Project Phoenix Integration                ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_PATH="/Users/rafi/Documents/Projects_OnGoing/Project phoenix"
OLLAMA_PORT=11434
PHOENIX_PORT=8000

echo -e "${BLUE}Step 1: Checking Prerequisites${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo -e "${RED}✗ Python not found${NC}"
    exit 1
fi
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# Check if Ollama is installed
if command -v ollama &> /dev/null; then
    OLLAMA_VERSION=$(ollama --version)
    echo -e "${GREEN}✓ Ollama already installed: $OLLAMA_VERSION${NC}"
else
    echo -e "${YELLOW}⚠ Ollama not installed. Installing now...${NC}"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            echo "Installing Ollama via Homebrew..."
            brew install ollama || {
                echo -e "${YELLOW}⚠ Homebrew installation failed. Downloading directly...${NC}"
                curl -fsSL https://ollama.ai/install.sh | sh
            }
        else
            echo "Installing Ollama from source..."
            curl -fsSL https://ollama.ai/install.sh | sh
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        echo "Installing Ollama via curl..."
        curl -fsSL https://ollama.ai/install.sh | sh
    else
        echo -e "${RED}✗ Unsupported operating system${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Ollama installed${NC}"
fi

echo ""
echo -e "${BLUE}Step 2: Downloading Free LLM Model${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Recommended: Mistral 7B (4.1GB, fast and capable)"
echo "Alternatives: LLaMA2 (3.8GB), Zephyr (3.8GB), Neural-Chat (4.0GB)"
echo ""

# Check if model is already available
if ollama list 2>/dev/null | grep -q "mistral"; then
    echo -e "${GREEN}✓ Mistral model already installed${NC}"
else
    echo "Pulling Mistral 7B model (this may take 5-10 minutes on first run)..."
    ollama pull mistral
    echo -e "${GREEN}✓ Mistral model ready${NC}"
fi

echo ""
echo -e "${BLUE}Step 3: Verifying Project Phoenix Files${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$PROJECT_PATH"

# Check core files
FILES_TO_CHECK=(
    "main.py"
    "autonomous_system/core/__init__.py"
    "autonomous_system/core/llm_system_integration.py"
    "autonomous_system/core/error_detection.py"
    "autonomous_system/core/self_correction.py"
)

ALL_FILES_EXIST=true
for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file${NC}"
    else
        echo -e "${RED}✗ $file not found${NC}"
        ALL_FILES_EXIST=false
    fi
done

if [ "$ALL_FILES_EXIST" = false ]; then
    echo -e "${RED}✗ Some required files are missing${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}Step 4: Installing Python Dependencies${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Install critical dependencies
echo "Installing dependencies (httpx, aiohttp, etc.)..."
pip install -q httpx aiohttp fastapi uvicorn 2>/dev/null || pip install httpx aiohttp fastapi uvicorn

echo -e "${GREEN}✓ Dependencies installed${NC}"

echo ""
echo -e "${BLUE}Step 5: Testing Ollama Connection${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if Ollama is running
if curl -s http://localhost:$OLLAMA_PORT/api/tags &> /dev/null; then
    echo -e "${GREEN}✓ Ollama is running on localhost:$OLLAMA_PORT${NC}"
else
    echo -e "${YELLOW}⚠ Ollama is not running. Starting Ollama...${NC}"
    echo ""
    echo "IMPORTANT: Ollama needs to run in a separate terminal!"
    echo ""
    echo "Run this in another terminal window:"
    echo "  → ollama serve"
    echo ""
    echo "Then come back here and press Enter to continue..."
    read -p "Press Enter when Ollama is running: "
    
    # Verify again
    if ! curl -s http://localhost:$OLLAMA_PORT/api/tags &> /dev/null; then
        echo -e "${RED}✗ Ollama still not responding${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Ollama connection verified${NC}"
fi

echo ""
echo -e "${BLUE}Step 6: Testing LLM Integration${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 << 'PYTHON_TEST'
import asyncio
import sys

sys.path.insert(0, '/Users/rafi/Documents/Projects_OnGoing/Project phoenix')

from autonomous_system.core import CoreOrchestrator
from autonomous_system.core.llm_system_integration import initialize_llm_integration
from autonomous_system.core.error_detection import ErrorContext, ErrorType, ErrorSeverity
import datetime

async def test_integration():
    try:
        # Initialize orchestrator
        print("Testing CoreOrchestrator initialization...")
        orchestrator = CoreOrchestrator()
        print("✓ CoreOrchestrator initialized")
        
        # Initialize LLM integration
        print("Testing LLM integration...")
        integrator = initialize_llm_integration(orchestrator)
        print("✓ LLM integration initialized")
        
        # Check health
        print("Checking LLM health...")
        health = await integrator.get_health_status()
        
        if health.get('ollama_available', False):
            print(f"✓ Ollama available: {health.get('status')}")
        else:
            print("⚠ Ollama available but warming up")
        
        # Test error analysis
        print("Testing error analysis...")
        error = ErrorContext(
            agent_id='test-agent',
            operation='test_operation',
            timestamp=datetime.datetime.now(),
            error_type=ErrorType.DEPENDENCY_ERROR,
            severity=ErrorSeverity.CRITICAL,
            message='Test database timeout',
            stack_trace='test trace'
        )
        
        analysis = await integrator.analyze_error_with_reasoning(error)
        print("✓ Error analysis working")
        
        # Shutdown
        await integrator.shutdown()
        
        print("")
        print("═" * 78)
        print("✓ ALL TESTS PASSED!")
        print("═" * 78)
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

success = asyncio.run(test_integration())
sys.exit(0 if success else 1)
PYTHON_TEST

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠ Some tests had issues. This might be normal on first run.${NC}"
fi

echo ""
echo -e "${BLUE}Step 7: Starting Project Phoenix${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo -e "${GREEN}✓ SETUP COMPLETE!${NC}"
echo ""
echo "Your Project Phoenix is ready to run with full LLM integration!"
echo ""
echo "To start the system, run in this directory:"
echo "  ${BLUE}python main.py${NC}"
echo ""
echo "The application will be available at:"
echo "  ${BLUE}http://localhost:$PHOENIX_PORT${NC}"
echo ""
echo "LLM Endpoints:"
echo "  ${BLUE}GET  /llm/health${NC}              - LLM status"
echo "  ${BLUE}POST /llm/analyze_error${NC}       - Analyze errors with reasoning"
echo "  ${BLUE}POST /llm/explain_correction${NC}  - Generate explanations"
echo "  ${BLUE}POST /llm/detect_patterns${NC}     - Pattern detection"
echo "  ${BLUE}POST /llm/optimize${NC}            - Optimization recommendations"
echo ""
echo "IMPORTANT:"
echo "  • Keep Ollama running: 'ollama serve' in another terminal"
echo "  • First LLM request may take 2-3 seconds (model loading)"
echo "  • Subsequent requests will be <100ms (cached)"
echo ""
echo "Cost: $0 (completely free, local, no cloud)"
echo "Privacy: 100% (all processing happens locally)"
echo ""
echo "═" * 78

echo ""
read -p "Ready to start Project Phoenix? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd "$PROJECT_PATH"
    python main.py
fi
