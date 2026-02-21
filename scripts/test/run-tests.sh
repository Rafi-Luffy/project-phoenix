#!/usr/bin/env zsh
# Project Phoenix - Test Execution Script
# Usage: ./run-tests.sh [command] [verbose]
# Commands: all, unit, integration, api, database, queue, performance, slow, coverage, parallel, lint, docker

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Output functions
print_header() {
    echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "${BLUE}📊 $1${NC}"
    echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    if ! command -v pytest &> /dev/null; then
        print_error "pytest not found. Install with: pip install -r tests-requirements.txt"
        exit 1
    fi
    print_success "pytest found"
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose not found. Install Docker Desktop"
        exit 1
    fi
    print_success "docker-compose found"
    
    if ! command -v docker &> /dev/null; then
        print_error "docker not found. Install Docker Desktop"
        exit 1
    fi
    print_success "docker found"
}

# Setup test environment
setup_environment() {
    print_header "Setting Up Test Environment"
    
    # Start Docker Compose services
    print_warning "Starting Docker Compose services..."
    docker-compose -f docker-compose.test.yml up -d
    
    # Wait for services to be healthy
    print_warning "Waiting for services to be healthy (30s timeout)..."
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose -f docker-compose.test.yml ps | grep -q "Up"; then
            print_success "All services are running"
            break
        fi
        sleep 1
        attempt=$((attempt + 1))
    done
    
    print_success "Test environment ready"
}

# Test commands
run_all_tests() {
    print_header "Running All Tests"
    pytest tests/ \
        --cov=backend \
        --cov-report=html \
        --cov-report=term-missing \
        --cov-fail-under=80 \
        -v \
        --tb=short
    print_success "All tests completed"
}

run_unit_tests() {
    print_header "Running Unit Tests"
    pytest tests/ \
        -m "not slow and not integration" \
        --cov=backend \
        --cov-report=term \
        -v \
        --tb=short
    print_success "Unit tests completed"
}

run_integration_tests() {
    print_header "Running Integration Tests"
    pytest tests/ \
        -m "integration or database or cache or queue" \
        --cov=backend \
        --cov-report=term \
        -v \
        --tb=short
    print_success "Integration tests completed"
}

run_api_tests() {
    print_header "Running API Endpoint Tests"
    pytest tests/test_api_endpoints.py \
        -v \
        --tb=short \
        --cov=backend.routes \
        --cov-report=term-missing
    print_success "API endpoint tests completed"
}

run_database_tests() {
    print_header "Running Database Operation Tests"
    pytest tests/test_database_operations.py \
        -v \
        --tb=short \
        --cov=backend.models \
        --cov-report=term-missing
    print_success "Database operation tests completed"
}

run_queue_tests() {
    print_header "Running Queue/Celery Tests"
    pytest tests/test_queue_operations.py \
        -v \
        --tb=short \
        --cov=backend.tasks \
        --cov-report=term-missing
    print_success "Queue/Celery tests completed"
}

run_performance_tests() {
    print_header "Running Performance Tests"
    pytest tests/ \
        -m "performance" \
        -v \
        --tb=short \
        --durations=10
    print_success "Performance tests completed"
}

run_slow_tests() {
    print_header "Running Slow Tests (10+ minutes)"
    pytest tests/ \
        -m "slow" \
        -v \
        --timeout=600 \
        --tb=short
    print_success "Slow tests completed"
}

run_coverage_report() {
    print_header "Generating Coverage Report"
    pytest tests/ \
        --cov=backend \
        --cov-report=html \
        --cov-report=term-missing \
        --cov-fail-under=80 \
        -q
    
    print_success "Coverage report generated at: htmlcov/index.html"
    
    # Try to open in browser
    if command -v open &> /dev/null; then
        open htmlcov/index.html
    elif command -v xdg-open &> /dev/null; then
        xdg-open htmlcov/index.html
    fi
}

run_parallel_tests() {
    print_header "Running Tests in Parallel"
    local workers=$(($(sysctl -n hw.ncpu 2>/dev/null || echo 4)))
    print_warning "Using $workers workers"
    
    pytest tests/ \
        -n $workers \
        --cov=backend \
        --cov-report=term \
        -v \
        --tb=short
    print_success "Parallel tests completed"
}

run_linting() {
    print_header "Running Code Quality Checks"
    
    print_warning "Running black (code formatting)..."
    black tests/ backend/ --check || true
    
    print_warning "Running isort (import sorting)..."
    isort tests/ backend/ --check-only || true
    
    print_warning "Running flake8 (linting)..."
    flake8 tests/ backend/ || true
    
    print_warning "Running mypy (type checking)..."
    mypy backend/ --ignore-missing-imports || true
    
    print_success "Code quality checks completed"
}

run_docker_tests() {
    print_header "Running Tests in Docker Container"
    
    # Build test image if needed
    docker build -t phoenix-test:latest \
        -f Dockerfile.test .
    
    # Run tests in container
    docker run --rm \
        --network host \
        -v "$(pwd):/app" \
        -w /app \
        phoenix-test:latest \
        pytest tests/ \
        --cov=backend \
        --cov-report=term \
        -v
    
    print_success "Docker tests completed"
}

# Main execution
main() {
    local command="${1:-all}"
    local verbose="${2:-}"
    
    # Setup
    print_header "Project Phoenix Test Suite"
    check_prerequisites
    setup_environment
    
    # Execute command
    case "$command" in
        all)
            run_all_tests
            ;;
        unit)
            run_unit_tests
            ;;
        integration)
            run_integration_tests
            ;;
        api)
            run_api_tests
            ;;
        database)
            run_database_tests
            ;;
        queue)
            run_queue_tests
            ;;
        performance)
            run_performance_tests
            ;;
        slow)
            run_slow_tests
            ;;
        coverage)
            run_coverage_report
            ;;
        parallel)
            run_parallel_tests
            ;;
        lint)
            run_linting
            ;;
        docker)
            run_docker_tests
            ;;
        *)
            print_error "Unknown command: $command"
            echo ""
            echo "Available commands:"
            echo "  all              - Run all tests"
            echo "  unit             - Run unit tests only"
            echo "  integration      - Run integration tests"
            echo "  api              - Run API endpoint tests"
            echo "  database         - Run database tests"
            echo "  queue            - Run queue/Celery tests"
            echo "  performance      - Run performance tests"
            echo "  slow             - Run slow tests (10+ min)"
            echo "  coverage         - Generate coverage report"
            echo "  parallel         - Run tests in parallel"
            echo "  lint             - Run code quality checks"
            echo "  docker           - Run tests in Docker"
            exit 1
            ;;
    esac
}

# Run main
main "$@"
