#!/bin/bash

###############################################################################
# Project Phoenix - Kubernetes Quick Deploy Script
# 
# This script automates the deployment of Project Phoenix to a Kubernetes cluster
# Usage: ./deploy-kubernetes.sh [command] [options]
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="phoenix"
MANIFEST_DIR="kubernetes"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-docker.io}"
DOCKER_IMAGE="${DOCKER_REGISTRY}/phoenix-api"
DOCKER_TAG="${DOCKER_TAG:-latest}"
TIMEOUT=300

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking requirements..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl not found. Please install kubectl."
        exit 1
    fi
    log_success "kubectl found: $(kubectl version --client --short)"
    
    # Check cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster."
        exit 1
    fi
    log_success "Connected to Kubernetes cluster"
    
    # Check helm (optional)
    if command -v helm &> /dev/null; then
        log_success "Helm found: $(helm version --short)"
    else
        log_warning "Helm not found (optional for Helm deployments)"
    fi
    
    # Check docker (for image building)
    if command -v docker &> /dev/null; then
        log_success "Docker found: $(docker --version)"
    else
        log_warning "Docker not found (required for building images)"
    fi
}

check_cluster_resources() {
    log_info "Checking cluster resources..."
    
    # Get node count
    local node_count=$(kubectl get nodes --no-headers | wc -l)
    log_info "Nodes: $node_count"
    
    # Get available resources
    log_info "Node resources:"
    kubectl top nodes 2>/dev/null || log_warning "Metrics server not available"
    
    # Check storage classes
    local storage_classes=$(kubectl get storageclass --no-headers 2>/dev/null | wc -l)
    log_info "Storage classes: $storage_classes"
    
    if [ "$storage_classes" -eq 0 ]; then
        log_warning "No storage classes found. Persistent volumes may not work."
    fi
}

deploy_manifests() {
    log_info "Deploying Kubernetes manifests..."
    
    # Step 1: Deploy namespace and RBAC
    log_info "Step 1/9: Creating namespace and RBAC..."
    kubectl apply -f "$MANIFEST_DIR/namespace.yaml"
    sleep 5
    
    # Step 2: Deploy secrets and config
    log_info "Step 2/9: Creating secrets and configuration..."
    kubectl apply -f "$MANIFEST_DIR/secrets-config.yaml"
    sleep 5
    
    # Step 3: Deploy PostgreSQL
    log_info "Step 3/9: Deploying PostgreSQL database..."
    kubectl apply -f "$MANIFEST_DIR/postgres-statefulset.yaml"
    log_info "Waiting for PostgreSQL to be ready (timeout: ${TIMEOUT}s)..."
    kubectl wait --for=condition=Ready pod -l app=postgres -n "$NAMESPACE" --timeout="${TIMEOUT}s" 2>/dev/null || log_warning "PostgreSQL not ready within timeout"
    sleep 10
    
    # Step 4: Deploy Redis
    log_info "Step 4/9: Deploying Redis cache..."
    kubectl apply -f "$MANIFEST_DIR/redis-statefulset.yaml"
    log_info "Waiting for Redis to be ready (timeout: ${TIMEOUT}s)..."
    kubectl wait --for=condition=Ready pod -l app=redis -n "$NAMESPACE" --timeout="${TIMEOUT}s" 2>/dev/null || log_warning "Redis not ready within timeout"
    sleep 10
    
    # Step 5: Deploy API
    log_info "Step 5/9: Deploying FastAPI backend..."
    kubectl apply -f "$MANIFEST_DIR/api-deployment.yaml"
    log_info "Waiting for API to be ready (timeout: ${TIMEOUT}s)..."
    kubectl wait --for=condition=Ready pod -l app=phoenix-api -n "$NAMESPACE" --timeout="${TIMEOUT}s" 2>/dev/null || log_warning "API not ready within timeout"
    sleep 10
    
    # Step 6: Deploy Celery
    log_info "Step 6/9: Deploying Celery workers and scheduler..."
    kubectl apply -f "$MANIFEST_DIR/celery-deployment.yaml"
    sleep 10
    
    # Step 7: Deploy Prometheus
    log_info "Step 7/9: Deploying Prometheus monitoring..."
    kubectl apply -f "$MANIFEST_DIR/prometheus-deployment.yaml"
    sleep 10
    
    # Step 8: Deploy Grafana
    log_info "Step 8/9: Deploying Grafana visualization..."
    kubectl apply -f "$MANIFEST_DIR/grafana-deployment.yaml"
    sleep 10
    
    # Step 9: Deploy Ingress
    log_info "Step 9/9: Deploying Ingress and TLS configuration..."
    kubectl apply -f "$MANIFEST_DIR/ingress.yaml"
    sleep 10
    
    log_success "All manifests deployed successfully"
}

verify_deployment() {
    log_info "Verifying deployment..."
    
    local all_ready=true
    
    # Check pods
    log_info "Checking pod status..."
    local not_ready=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase!=Running,status.phase!=Succeeded --no-headers 2>/dev/null | wc -l)
    
    if [ "$not_ready" -gt 0 ]; then
        log_warning "Some pods are not running:"
        kubectl get pods -n "$NAMESPACE" --field-selector=status.phase!=Running,status.phase!=Succeeded
        all_ready=false
    else
        log_success "All pods are running"
    fi
    
    # Check services
    log_info "Checking services..."
    kubectl get svc -n "$NAMESPACE"
    
    # Check PVCs
    log_info "Checking persistent volumes..."
    kubectl get pvc -n "$NAMESPACE"
    
    # Check ingress
    log_info "Checking ingress..."
    kubectl get ingress -n "$NAMESPACE"
    
    if [ "$all_ready" = true ]; then
        log_success "Deployment verified successfully"
        return 0
    else
        log_warning "Some resources are not ready. Please check logs for details."
        return 1
    fi
}

show_access_info() {
    log_info "Deployment Access Information:"
    
    echo ""
    echo -e "${YELLOW}=== Port Forwarding ===${NC}"
    echo "API: kubectl port-forward -n $NAMESPACE svc/phoenix-api 8000:8000"
    echo "Prometheus: kubectl port-forward -n $NAMESPACE svc/prometheus 9090:9090"
    echo "Grafana: kubectl port-forward -n $NAMESPACE svc/grafana 3000:80"
    echo "PostgreSQL: kubectl port-forward -n $NAMESPACE svc/phoenix-postgres-lb 5432:5432"
    echo "Redis: kubectl port-forward -n $NAMESPACE svc/phoenix-redis-lb 6379:6379"
    
    echo ""
    echo -e "${YELLOW}=== Credentials ===${NC}"
    echo "Grafana Admin: admin/grafana (change in secrets)"
    echo "PostgreSQL: postgres/password (change in secrets)"
    echo "Redis: password (change in secrets)"
    
    echo ""
    echo -e "${YELLOW}=== Useful Commands ===${NC}"
    echo "View all resources: kubectl get all -n $NAMESPACE"
    echo "View pod logs: kubectl logs -n $NAMESPACE -l app=phoenix-api -f"
    echo "View resource usage: kubectl top pods -n $NAMESPACE"
    echo "Scale API: kubectl scale deployment phoenix-api -n $NAMESPACE --replicas=5"
    echo "Delete everything: kubectl delete namespace $NAMESPACE"
    
    echo ""
    echo -e "${YELLOW}=== API Endpoints (after port forwarding) ===${NC}"
    echo "Health: http://localhost:8000/api/v1/health/live"
    echo "Docs: http://localhost:8000/docs"
    echo "Swagger UI: http://localhost:8000/redoc"
    
    echo ""
    echo -e "${YELLOW}=== Monitoring (after port forwarding) ===${NC}"
    echo "Prometheus: http://localhost:9090"
    echo "Grafana: http://localhost:3000 (admin/grafana)"
}

build_docker_image() {
    log_info "Building Docker image..."
    
    if [ ! -f "Dockerfile.backend" ]; then
        log_error "Dockerfile.backend not found"
        return 1
    fi
    
    log_info "Building: $DOCKER_IMAGE:$DOCKER_TAG"
    docker build -f Dockerfile.backend -t "$DOCKER_IMAGE:$DOCKER_TAG" .
    
    if [ -n "$DOCKER_REGISTRY" ] && [ "$DOCKER_REGISTRY" != "docker.io" ]; then
        log_info "Pushing to registry: $DOCKER_REGISTRY"
        docker push "$DOCKER_IMAGE:$DOCKER_TAG"
        log_success "Image pushed to registry"
    else
        log_success "Image built successfully (use 'docker push' to upload to registry)"
    fi
}

update_image() {
    log_info "Updating API image in deployment..."
    
    kubectl set image deployment/phoenix-api -n "$NAMESPACE" \
        phoenix-api="$DOCKER_IMAGE:$DOCKER_TAG"
    
    log_info "Waiting for rollout to complete..."
    kubectl rollout status deployment/phoenix-api -n "$NAMESPACE"
    
    log_success "Image updated and deployment rolled out"
}

cleanup() {
    log_warning "Deleting all Phoenix resources..."
    
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl delete namespace "$NAMESPACE"
        log_success "Namespace and all resources deleted"
    else
        log_info "Cleanup cancelled"
    fi
}

rollback() {
    log_info "Rolling back deployment..."
    kubectl rollout undo deployment/phoenix-api -n "$NAMESPACE"
    kubectl rollout status deployment/phoenix-api -n "$NAMESPACE"
    log_success "Deployment rolled back"
}

tail_logs() {
    local app="${1:-phoenix-api}"
    log_info "Tailing logs for app=$app..."
    kubectl logs -n "$NAMESPACE" -l "app=$app" -f --timestamps=true
}

# Help function
show_help() {
    cat <<EOF
Project Phoenix - Kubernetes Quick Deploy Script

Usage: $0 [command] [options]

Commands:
    check           Check requirements and cluster resources
    deploy          Deploy all manifests to Kubernetes (full deployment)
    verify          Verify deployment status
    info            Show access information and credentials
    build-image     Build Docker image locally
    update-image    Update deployed image
    logs [app]      Tail logs for an application (default: phoenix-api)
    cleanup         Delete all Phoenix resources
    rollback        Rollback to previous deployment
    help            Show this help message

Options:
    --registry      Docker registry (default: docker.io)
    --tag           Docker image tag (default: latest)
    --timeout       Timeout for waiting (default: 300s)
    --namespace     Kubernetes namespace (default: phoenix)

Examples:
    # Full deployment
    $0 deploy

    # Check cluster before deployment
    $0 check

    # Verify deployment
    $0 verify

    # Show access information
    $0 info

    # Build and deploy new image
    $0 build-image --registry my.registry.com --tag v1.0.0
    $0 update-image --registry my.registry.com --tag v1.0.0

    # View logs
    $0 logs phoenix-api
    $0 logs celery-worker

    # Cleanup
    $0 cleanup

EOF
}

# Parse arguments
COMMAND="${1:-help}"

case "$COMMAND" in
    check)
        check_requirements
        check_cluster_resources
        ;;
    deploy)
        check_requirements
        check_cluster_resources
        deploy_manifests
        sleep 30
        verify_deployment
        show_access_info
        ;;
    verify)
        verify_deployment
        show_access_info
        ;;
    info)
        show_access_info
        ;;
    build-image)
        build_docker_image
        ;;
    update-image)
        update_image
        ;;
    logs)
        tail_logs "${2:-phoenix-api}"
        ;;
    cleanup)
        cleanup
        ;;
    rollback)
        rollback
        ;;
    help)
        show_help
        ;;
    *)
        log_error "Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac
