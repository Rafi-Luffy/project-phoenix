#!/bin/bash
# PROJECT PHOENIX - PRE-DEMO CHECKLIST
# Run this before your demo review to ensure everything is ready

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     PROJECT PHOENIX - PRE-DEMO VERIFICATION CHECKLIST         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

PROJECT_ROOT="/Users/rafi/Documents/Projects_OnGoing/Project phoenix"
ISSUES=0
WARNINGS=0

echo "Checking prerequisites..."
echo ""

# Check 1: Python version
echo -n "✓ Checking Python version... "
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1-2)
if command -v python3 &> /dev/null; then
    echo "OK (v$PYTHON_VERSION)"
else
    echo "FAIL - Python 3 not found"
    ISSUES=$((ISSUES + 1))
fi

# Check 2: Requests module
echo -n "✓ Checking requests module... "
if python3 -c "import requests" 2>/dev/null; then
    echo "OK"
else
    echo "MISSING - Run: pip3 install requests"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 3: Project directory
echo -n "✓ Checking project directory... "
if [ -d "$PROJECT_ROOT" ]; then
    echo "OK"
else
    echo "FAIL - Project not found at $PROJECT_ROOT"
    ISSUES=$((ISSUES + 1))
fi

# Check 4: Backend files
echo -n "✓ Checking backend... "
if [ -f "$PROJECT_ROOT/backend/src/main.py" ]; then
    echo "OK"
else
    echo "FAIL - Backend not found"
    ISSUES=$((ISSUES + 1))
fi

# Check 5: Demo script
echo -n "✓ Checking demo script... "
if [ -f "$PROJECT_ROOT/demo_self_healing.py" ]; then
    echo "OK"
else
    echo "FAIL - Demo script not found"
    ISSUES=$((ISSUES + 1))
fi

# Check 6: Dashboard script
echo -n "✓ Checking dashboard... "
if [ -f "$PROJECT_ROOT/dashboard_monitor.py" ]; then
    echo "OK"
else
    echo "WARN - Dashboard not found (optional)"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 7: Documentation
echo -n "✓ Checking documentation... "
if [ -f "$PROJECT_ROOT/DEMO_GUIDE.md" ] && [ -f "$PROJECT_ROOT/DEMO_QUICK_REFERENCE.txt" ]; then
    echo "OK"
else
    echo "WARN - Some documentation missing"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 8: Python syntax
echo -n "✓ Checking demo syntax... "
if python3 -m py_compile "$PROJECT_ROOT/demo_self_healing.py" 2>/dev/null; then
    echo "OK"
else
    echo "FAIL - Demo script has syntax errors"
    ISSUES=$((ISSUES + 1))
fi

# Check 9: Port availability
echo -n "✓ Checking port 8000 (backend)... "
if nc -z localhost 8000 2>/dev/null; then
    echo "IN USE (Backend already running?)"
else
    echo "AVAILABLE"
fi

# Check 10: Port 8080
echo -n "✓ Checking port 8080 (frontend)... "
if nc -z localhost 8080 2>/dev/null; then
    echo "IN USE (Frontend already running?)"
else
    echo "AVAILABLE"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    SUMMARY                                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

if [ $ISSUES -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✓ ALL CHECKS PASSED - You're ready to demo!"
    echo ""
    echo "Next steps:"
    echo "  1. Read: DEMO_QUICK_REFERENCE.txt"
    echo "  2. Terminal 1: python3 backend/src/main.py"
    echo "  3. Terminal 2: python3 demo_self_healing.py"
    echo "  4. Watch the magic! ✨"
    echo ""
elif [ $ISSUES -eq 0 ]; then
    echo "⚠ Some warnings detected (but you can still demo):"
    echo "  Run the recommended fixes above"
    echo ""
else
    echo "✗ CRITICAL ISSUES DETECTED:"
    echo "  Fix the FAIL items before running the demo"
    echo ""
fi

echo "Demo location: $PROJECT_ROOT"
echo ""
