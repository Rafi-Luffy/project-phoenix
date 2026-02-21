#!/bin/bash
# Stop and remove all Phoenix containers

echo "🛑 Stopping Project Phoenix deployment..."

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

docker-compose -f "$PROJECT_DIR/docker-compose.prod.yml" down -v

echo "✅ All services stopped and cleaned up"
echo ""
echo "To redeploy: bash deploy.sh"
