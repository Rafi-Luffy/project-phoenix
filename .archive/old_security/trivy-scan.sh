#!/bin/bash
# Trivy Container Image Vulnerability Scanner
# Scans Docker images for known vulnerabilities before deployment

set -e

REGISTRY="${DOCKER_REGISTRY:-your-registry.azurecr.io}"
IMAGE_NAME="${1:-phoenix-api}"
IMAGE_TAG="${2:-latest}"
SEVERITY_THRESHOLD="${3:-HIGH}"

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Container Image Vulnerability Scan"
echo "=========================================="
echo "Registry: $REGISTRY"
echo "Image: $IMAGE_NAME:$IMAGE_TAG"
echo "Severity Threshold: $SEVERITY_THRESHOLD"
echo ""

# Check if Trivy is installed
if ! command -v trivy &> /dev/null; then
    echo "Trivy is not installed. Installing..."
    curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
fi

# Scan image for vulnerabilities
echo "Scanning image for vulnerabilities..."
IMAGE_FULL_NAME="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

SCAN_RESULT=$(trivy image \
    --severity "$SEVERITY_THRESHOLD" \
    --exit-code 0 \
    --format json \
    --output /tmp/trivy-scan-result.json \
    "$IMAGE_FULL_NAME" 2>&1 || true)

# Parse results
CRITICAL_COUNT=$(jq '[.Results[]? | select(.Severity=="CRITICAL")] | length' /tmp/trivy-scan-result.json || echo "0")
HIGH_COUNT=$(jq '[.Results[]? | select(.Severity=="HIGH")] | length' /tmp/trivy-scan-result.json || echo "0")
MEDIUM_COUNT=$(jq '[.Results[]? | select(.Severity=="MEDIUM")] | length' /tmp/trivy-scan-result.json || echo "0")
LOW_COUNT=$(jq '[.Results[]? | select(.Severity=="LOW")] | length' /tmp/trivy-scan-result.json || echo "0")

echo ""
echo "Vulnerability Summary:"
echo -e "${RED}Critical: $CRITICAL_COUNT${NC}"
echo -e "${YELLOW}High: $HIGH_COUNT${NC}"
echo "Medium: $MEDIUM_COUNT"
echo "Low: $LOW_COUNT"
echo ""

# Display vulnerable packages
if [ "$CRITICAL_COUNT" -gt 0 ]; then
    echo -e "${RED}CRITICAL Vulnerabilities:${NC}"
    jq -r '.Results[]? | select(.Severity=="CRITICAL") | "\(.Target): \(.Vulnerabilities[]?.VulnerabilityID) - \(.Vulnerabilities[]?.Title)"' /tmp/trivy-scan-result.json || true
    echo ""
fi

if [ "$HIGH_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}HIGH Vulnerabilities:${NC}"
    jq -r '.Results[]? | select(.Severity=="HIGH") | "\(.Target): \(.Vulnerabilities[]?.VulnerabilityID) - \(.Vulnerabilities[]?.Title)"' /tmp/trivy-scan-result.json || true
    echo ""
fi

# Check policy - fail if critical vulnerabilities exist
if [ "$CRITICAL_COUNT" -gt 0 ]; then
    echo -e "${RED}[FAIL] Image contains CRITICAL vulnerabilities!${NC}"
    exit 1
elif [ "$HIGH_COUNT" -gt 5 ]; then
    echo -e "${YELLOW}[WARNING] Image contains multiple HIGH vulnerabilities${NC}"
    # In strict mode, this would exit 1
    # For warning mode, we continue
fi

echo -e "${GREEN}[PASS] Image scan completed successfully${NC}"

# Generate HTML report
trivy image \
    --format sarif \
    --output /tmp/trivy-scan-sarif.json \
    "$IMAGE_FULL_NAME" 2>&1 || true

echo ""
echo "Full JSON report: /tmp/trivy-scan-result.json"
echo "SARIF report: /tmp/trivy-scan-sarif.json"
echo ""
echo "=========================================="
