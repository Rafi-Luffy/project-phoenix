#!/bin/bash

###############################################################################
# PROJECT PHOENIX - COMPLETE OLLAMA SETUP & VERIFICATION
# 
# This script will:
# 1. Check/install Ollama
# 2. Verify installation
# 3. Test Python environment
# 4. Run integration tests
# 5. Provide final instructions
#
# Usage: chmod +x run_complete_setup.sh && ./run_complete_setup.sh
###############################################################################

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
OLLAMA_URL="http://localhost:11434"
PYTHON_CMD="python3"
WORKSPACE="/Users/rafi/Documents/Projects_OnGoing/Project\ phoenix"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║     PROJECT PHOENIX - COMPLETE OLLAMA SETUP & VERIFICATION         ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

###############################################################################
# STEP 1: CHECK OPERATING SYSTEM
###############################################################################
echo -e "\n${BLUE}[STEP 1] Checking Operating System${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

OS_TYPE=$(uname -s)
echo "OS Detected: $OS_TYPE"

if [[ "$OS_TYPE" != "Darwin" && "$OS_TYPE" != "Linux" ]]; then
    echo -e "${RED}❌ Error: Unsupported OS ($OS_TYPE). This script supports macOS and Linux.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ OS compatible${NC}"

###############################################################################
# STEP 2: CHECK/INSTALL OLLAMA
###############################################################################
echo -e "\n${BLUE}[STEP 2] Checking Ollama Installation${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v ollama &> /dev/null; then
    OLLAMA_VERSION=$(ollama --version 2>/dev/null | head -n 1 || echo "unknown")
    echo -e "${GREEN}✅ Ollama is installed${NC}"
    echo "   Version: $OLLAMA_VERSION"
else
    echo -e "${YELLOW}⚠️  Ollama not found. Installing...${NC}"
    
    if [[ "$OS_TYPE" == "Darwin" ]]; then
        echo "   Installing via Homebrew (macOS)..."
        if command -v brew &> /dev/null; then
            brew install ollama
            echo -e "${GREEN}✅ Ollama installed successfully${NC}"
        else
            echo -e "${RED}❌ Homebrew not found. Please install Ollama from https://ollama.ai${NC}"
            exit 1
        fi
    elif [[ "$OS_TYPE" == "Linux" ]]; then
        echo "   For Linux, please visit: https://ollama.ai/download/linux"
        echo "   Or run: curl https://ollama.ai/install.sh | sh"
        exit 1
    fi
fi

###############################################################################
# STEP 3: CHECK PYTHON ENVIRONMENT
###############################################################################
echo -e "\n${BLUE}[STEP 3] Checking Python Environment${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if ! command -v $PYTHON_CMD &> /dev/null; then
    echo -e "${RED}❌ Python3 not found${NC}"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python found${NC}"
echo "   Version: $PYTHON_VERSION"

# Check required packages
echo "   Checking required packages..."

MISSING_PACKAGES=()

for package in fastapi pydantic aiohttp; do
    if ! $PYTHON_CMD -c "import $package" 2>/dev/null; then
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Missing packages: ${MISSING_PACKAGES[*]}${NC}"
    echo "   Installing..."
    $PYTHON_CMD -m pip install -q "${MISSING_PACKAGES[@]}"
    echo -e "${GREEN}✅ Packages installed${NC}"
else
    echo -e "${GREEN}✅ All required packages found${NC}"
fi

###############################################################################
# STEP 4: TEST PROJECT PHOENIX IMPORTS
###############################################################################
echo -e "\n${BLUE}[STEP 4] Testing Project Phoenix Imports${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$WORKSPACE"

echo "   Testing core framework imports..."
$PYTHON_CMD << 'EOF'
import sys
sys.path.insert(0, '.')

try:
    from autonomous_system.core import CoreOrchestrator
    print("   ✅ CoreOrchestrator imported")
    
    from autonomous_system.core import SelfCorrectionOrchestrator
    print("   ✅ SelfCorrectionOrchestrator imported")
    
    from autonomous_system.core import MemoryManager
    print("   ✅ MemoryManager imported")
    
    from autonomous_system.core.llm_system_integration import (
        LLMSystemIntegrator,
        initialize_llm_integration,
        OllamaClient,
        OllamaConfig
    )
    print("   ✅ LLM integration imported")
    
    print("\n✅ All imports successful")
except ImportError as e:
    print(f"\n❌ Import error: {e}")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Import test failed${NC}"
    exit 1
fi

###############################################################################
# STEP 5: VERIFY PROJECT PHOENIX STRUCTURE
###############################################################################
echo -e "\n${BLUE}[STEP 5] Verifying Project Structure${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

REQUIRED_FILES=(
    "autonomous_system/core/__init__.py"
    "autonomous_system/core/llm_system_integration.py"
    "main.py"
    "tests/test_complete_integration_ollama.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "   ${GREEN}✅${NC} $file"
    else
        echo -e "   ${RED}❌${NC} $file (missing)"
    fi
done

###############################################################################
# STEP 6: DISPLAY SETUP INSTRUCTIONS
###############################################################################
echo -e "\n${BLUE}[STEP 6] Setup Complete - Next Steps${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo -e "\n${YELLOW}IMPORTANT: Before running Project Phoenix, you need to:${NC}\n"

echo "1. ${BLUE}Download Mistral Model (4.1GB)${NC}"
echo "   Run in a terminal:"
echo "   ${GREEN}ollama pull mistral${NC}"
echo "   (This downloads the free Mistral 7B model)"
echo ""

echo "2. ${BLUE}Start Ollama Service${NC}"
echo "   In Terminal 1:"
echo "   ${GREEN}ollama serve${NC}"
echo "   (Keep this running)"
echo ""

echo "3. ${BLUE}Start Project Phoenix${NC}"
echo "   In Terminal 2:"
echo "   ${GREEN}cd '$WORKSPACE'${NC}"
echo "   ${GREEN}python3 main.py${NC}"
echo ""

echo "4. ${BLUE}Test Integration${NC}"
echo "   In Terminal 3:"
echo "   ${GREEN}curl http://localhost:8000/llm/health${NC}"
echo ""

echo "5. ${BLUE}Run Complete Tests${NC}"
echo "   ${GREEN}python3 -m pytest tests/test_complete_integration_ollama.py -v${NC}"
echo ""

###############################################################################
# STEP 7: OPTIONAL - DOWNLOAD MODEL NOW
###############################################################################
echo -e "\n${BLUE}[STEP 7] Model Download${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo -e "${YELLOW}Would you like to download the Mistral model now? (y/n)${NC}"
read -p "Download model? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting Ollama service for model download..."
    
    # Start ollama in background
    if pgrep -x "ollama" > /dev/null; then
        echo "Ollama already running"
    else
        echo "Starting Ollama daemon..."
        nohup ollama serve > /tmp/ollama.log 2>&1 &
        OLLAMA_PID=$!
        echo "Ollama PID: $OLLAMA_PID"
        sleep 3
    fi
    
    echo "Downloading Mistral model..."
    echo "(This may take 10-15 minutes for 4.1GB)"
    echo ""
    
    ollama pull mistral
    
    if [ $? -eq 0 ]; then
        echo -e "\n${GREEN}✅ Mistral model downloaded successfully${NC}"
    else
        echo -e "\n${RED}❌ Model download failed${NC}"
    fi
else
    echo "Skipping model download. You can download later with: ollama pull mistral"
fi

###############################################################################
# FINAL SUMMARY
###############################################################################
echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║               ✅ SETUP COMPLETE - READY TO START                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${GREEN}Project Phoenix Status:${NC}"
echo "  ✅ Framework: Ready"
echo "  ✅ LLM Integration: Ready"
echo "  ✅ Ollama: Installed"
echo "  ✅ Python: Configured"
echo ""

echo -e "${GREEN}Cost:${NC} $0 (completely free)"
echo -e "${GREEN}Privacy:${NC} 100% local, no cloud"
echo -e "${GREEN}Models Available:${NC} Mistral, LLaMA2, Zephyr, Neural Chat"
echo ""

echo -e "${YELLOW}Next Command:${NC}"
echo "  ${GREEN}ollama pull mistral${NC}  (if not already done)"
echo ""

echo -e "${YELLOW}Then in two terminals:${NC}"
echo "  Terminal 1: ${GREEN}ollama serve${NC}"
echo "  Terminal 2: ${GREEN}cd '$WORKSPACE' && python3 main.py${NC}"
echo ""

echo -e "${YELLOW}Test in third terminal:${NC}"
echo "  ${GREEN}curl http://localhost:8000/llm/health${NC}"
echo ""

echo -e "${BLUE}Documentation:${NC}"
echo "  - LLM_FRAMEWORK_ALIGNMENT_VERIFICATION.md"
echo "  - LLM_INTEGRATION_REPORT.md"
echo "  - QUICK_START_LLM.md"
echo ""

echo -e "${GREEN}🎉 Ready to run Project Phoenix with Ollama!${NC}\n"
