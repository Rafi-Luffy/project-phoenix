#!/bin/bash

# Project Phoenix - Demo Setup & Launcher
# This script helps you run the self-healing demo

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT="/Users/rafi/Documents/Projects_OnGoing/Project phoenix"
BACKEND_PORT=8000
FRONTEND_PORT=8080

# Helper functions
print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}  PROJECT PHOENIX - DEMO LAUNCHER                                 ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_section() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed"
        return 1
    fi
    print_success "$1 found"
    return 0
}

check_port() {
    if nc -z localhost $1 2>/dev/null; then
        return 0  # Port is open
    fi
    return 1  # Port is closed
}

wait_for_port() {
    local port=$1
    local service=$2
    local max_attempts=30
    local attempt=0

    print_info "Waiting for $service on port $port..."
    
    while [ $attempt -lt $max_attempts ]; do
        if check_port $port; then
            print_success "$service is ready on port $port"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo -n "."
        sleep 1
    done
    
    echo ""
    print_error "$service did not start within 30 seconds"
    return 1
}

main() {
    print_header

    # Check prerequisites
    print_section "Checking Prerequisites"
    
    check_command python3
    check_command pip3
    
    # Check Python version
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_success "Python version: $PYTHON_VERSION"

    # Check required modules
    print_section "Checking Python Modules"
    
    if python3 -c "import requests" 2>/dev/null; then
        print_success "requests module found"
    else
        print_warning "requests module not found, installing..."
        pip3 install requests > /dev/null 2>&1
        print_success "requests module installed"
    fi

    # Check project structure
    print_section "Verifying Project Structure"
    
    if [ -d "$PROJECT_ROOT" ]; then
        print_success "Project directory found"
    else
        print_error "Project directory not found: $PROJECT_ROOT"
        exit 1
    fi

    if [ -f "$PROJECT_ROOT/backend/src/main.py" ]; then
        print_success "Backend found"
    else
        print_error "Backend not found at expected location"
        exit 1
    fi

    if [ -f "$PROJECT_ROOT/demo_self_healing.py" ]; then
        print_success "Demo script found"
    else
        print_error "Demo script not found"
        exit 1
    fi

    # Check if services are already running
    print_section "Checking Running Services"
    
    BACKEND_RUNNING=0
    FRONTEND_RUNNING=0
    
    if check_port $BACKEND_PORT; then
        print_success "Backend already running on port $BACKEND_PORT"
        BACKEND_RUNNING=1
    else
        print_info "Backend not running (will need to start)"
    fi

    if check_port $FRONTEND_PORT; then
        print_success "Frontend already running on port $FRONTEND_PORT"
        FRONTEND_RUNNING=1
    else
        print_info "Frontend not running (optional for demo)"
    fi

    # Show menu
    print_section "Demo Setup Options"
    
    echo ""
    echo "1) Full Demo (backend + dashboard + demo script)"
    echo "2) Quick Demo (dashboard + demo script - backend must be running)"
    echo "3) Start Backend Only"
    echo "4) Just Run Demo (all services must be running)"
    echo "5) Show Demo Guide"
    echo "6) Exit"
    echo ""

    read -p "Select option (1-6): " CHOICE

    case $CHOICE in
        1)
            run_full_demo
            ;;
        2)
            run_quick_demo
            ;;
        3)
            start_backend_only
            ;;
        4)
            run_demo_only
            ;;
        5)
            show_demo_guide
            ;;
        6)
            print_info "Exiting"
            exit 0
            ;;
        *)
            print_error "Invalid option"
            exit 1
            ;;
    esac
}

start_backend_only() {
    print_section "Starting Backend"
    
    cd "$PROJECT_ROOT"
    print_info "Starting backend server..."
    print_info "Backend will run on http://localhost:$BACKEND_PORT"
    print_info "API docs available at http://localhost:$BACKEND_PORT/docs"
    print_info "Press Ctrl+C to stop"
    echo ""
    
    python3 backend/src/main.py
}

run_full_demo() {
    print_section "Full Demo Setup"
    
    # Start backend in background
    print_info "Starting backend..."
    cd "$PROJECT_ROOT"
    python3 backend/src/main.py > /tmp/phoenix_backend.log 2>&1 &
    BACKEND_PID=$!
    print_success "Backend started (PID: $BACKEND_PID)"
    
    # Wait for backend
    if ! wait_for_port $BACKEND_PORT "Backend API"; then
        print_error "Failed to start backend"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    
    print_section "Setup Complete - Ready for Demo"
    echo ""
    print_info "Backend running: http://localhost:$BACKEND_PORT"
    print_info "API docs: http://localhost:$BACKEND_PORT/docs"
    echo ""
    print_warning "IMPORTANT: You need to run these in separate terminal windows:"
    echo ""
    echo "  Terminal 1 (Dashboard Monitor):"
    echo "  cd '$PROJECT_ROOT'"
    echo "  python3 dashboard_monitor.py"
    echo ""
    echo "  Terminal 2 (Run Demo):"
    echo "  cd '$PROJECT_ROOT'"
    echo "  python3 demo_self_healing.py"
    echo ""
    
    read -p "Press Enter when you're ready to continue..."
    
    print_info "Starting dashboard in a new window (requires Terminal app on Mac)..."
    open -a Terminal "$PROJECT_ROOT/dashboard_monitor.py"
    
    sleep 2
    
    print_info "Ready to run demo. Press Enter..."
    read
    
    run_demo_only
}

run_quick_demo() {
    print_section "Quick Demo Setup"
    
    if ! check_port $BACKEND_PORT; then
        print_error "Backend is not running on port $BACKEND_PORT"
        print_info "Please start the backend first:"
        echo ""
        echo "  cd '$PROJECT_ROOT'"
        echo "  python3 backend/src/main.py"
        echo ""
        exit 1
    fi
    
    print_success "Backend is running"
    
    print_section "Setup Complete - Running Demo"
    echo ""
    print_warning "IMPORTANT: Run this in a separate terminal window:"
    echo ""
    echo "  Terminal 1 (Dashboard Monitor):"
    echo "  cd '$PROJECT_ROOT'"
    echo "  python3 dashboard_monitor.py"
    echo ""
    
    read -p "Press Enter when dashboard is running..."
    
    run_demo_only
}

run_demo_only() {
    print_section "Running Self-Healing Demo"
    
    if ! check_port $BACKEND_PORT; then
        print_error "Backend is not running"
        exit 1
    fi
    
    echo ""
    cd "$PROJECT_ROOT"
    python3 demo_self_healing.py
}

show_demo_guide() {
    print_section "Demo Guide"
    echo ""
    
    if [ -f "$PROJECT_ROOT/DEMO_GUIDE.md" ]; then
        less "$PROJECT_ROOT/DEMO_GUIDE.md"
    else
        print_error "Demo guide not found"
        exit 1
    fi
}

# Run main
main
