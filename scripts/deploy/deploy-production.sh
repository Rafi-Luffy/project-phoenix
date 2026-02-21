#!/bin/bash

# ============================================================================
# PROJECT PHOENIX - PRODUCTION DEPLOYMENT SCRIPT
# Complete end-to-end deployment with PostgreSQL + Ollama
# Free, Open-Source, Zero-Cost Forever
# ============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${PROJECT_DIR}/deployment.log"

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║       PROJECT PHOENIX - PRODUCTION DEPLOYMENT (TONIGHT!)                   ║"
echo "║         PostgreSQL + Ollama + FastAPI = $0 Forever                         ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to log messages
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Step 1: Check prerequisites
log "${BLUE}[1/10] Checking prerequisites...${NC}"
{
    if ! command -v docker &> /dev/null; then
        log "${YELLOW}⚠ Docker not found, installing...${NC}"
        # Docker installation instructions
        log "Please install Docker from: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log "${YELLOW}⚠ Docker Compose not found, installing...${NC}"
        exit 1
    fi
    
    log "${GREEN}✓ Docker & Docker Compose available${NC}"
} >> "$LOG_FILE" 2>&1

# Step 2: Check environment file
log "${BLUE}[2/10] Checking environment configuration...${NC}"
{
    if [ ! -f "${PROJECT_DIR}/.env.production" ]; then
        log "${YELLOW}⚠ .env.production not found, creating from template...${NC}"
        cp "${PROJECT_DIR}/.env.example" "${PROJECT_DIR}/.env.production" 2>/dev/null || \
        {
            cat > "${PROJECT_DIR}/.env.production" << EOF
DATABASE_URL=postgresql://phoenix_admin:your_secure_password@postgres:5432/project_phoenix
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=mistral
ENVIRONMENT=production
LOG_LEVEL=info
LLM_ENABLED=true
SECRET_KEY=change-this-to-a-secure-random-string
EOF
        }
        log "${YELLOW}⚠ Created .env.production - UPDATE WITH SECURE VALUES!${NC}"
    fi
    
    log "${GREEN}✓ Environment file ready${NC}"
} >> "$LOG_FILE" 2>&1

# Step 3: Build Docker images
log "${BLUE}[3/10] Building Docker images...${NC}"
{
    cd "$PROJECT_DIR"
    
    # Build PostgreSQL init script
    log "Building PostgreSQL container..."
    
    # Build Ollama container
    log "Setting up Ollama container..."
    
    # Build Phoenix application container
    log "Building Phoenix application container..."
    docker-compose -f docker-compose.prod.yml build --no-cache phoenix 2>&1 | tail -20
    
    log "${GREEN}✓ Docker images built successfully${NC}"
} >> "$LOG_FILE" 2>&1

# Step 4: Start PostgreSQL
log "${BLUE}[4/10] Starting PostgreSQL database...${NC}"
{
    cd "$PROJECT_DIR"
    docker-compose -f docker-compose.prod.yml up -d postgres
    
    # Wait for PostgreSQL to be ready
    log "Waiting for PostgreSQL to be ready..."
    for i in {1..30}; do
        if docker exec phoenix_db pg_isready -U phoenix_admin -d project_phoenix &>/dev/null; then
            log "${GREEN}✓ PostgreSQL is ready${NC}"
            break
        fi
        echo -n "."
        sleep 2
    done
} >> "$LOG_FILE" 2>&1

# Step 5: Initialize database
log "${BLUE}[5/10] Initializing PostgreSQL database...${NC}"
{
    log "Running database migrations..."
    docker-compose -f docker-compose.prod.yml exec -T postgres \
        psql -U phoenix_admin -d project_phoenix -f /docker-entrypoint-initdb.d/init.sql 2>&1 | head -20
    
    log "${GREEN}✓ Database initialized${NC}"
} >> "$LOG_FILE" 2>&1

# Step 6: Start Ollama
log "${BLUE}[6/10] Starting Ollama LLM service...${NC}"
{
    cd "$PROJECT_DIR"
    docker-compose -f docker-compose.prod.yml up -d ollama
    
    # Wait for Ollama to be ready
    log "Waiting for Ollama to be ready..."
    for i in {1..30}; do
        if docker exec phoenix_ollama curl -f http://localhost:11434/api/tags &>/dev/null; then
            log "${GREEN}✓ Ollama is ready${NC}"
            break
        fi
        echo -n "."
        sleep 2
    done
} >> "$LOG_FILE" 2>&1

# Step 7: Pull Mistral model
log "${BLUE}[7/10] Downloading Mistral 7B model (4.1GB)...${NC}"
{
    log "This may take 5-15 minutes depending on internet speed..."
    docker exec phoenix_ollama ollama pull mistral 2>&1 | tail -20
    log "${GREEN}✓ Mistral model ready${NC}"
} >> "$LOG_FILE" 2>&1

# Step 8: Start Project Phoenix
log "${BLUE}[8/10] Starting Project Phoenix application...${NC}"
{
    cd "$PROJECT_DIR"
    docker-compose -f docker-compose.prod.yml up -d phoenix
    
    # Wait for Phoenix to be ready
    log "Waiting for Phoenix to be ready..."
    for i in {1..30}; do
        if docker exec project_phoenix_app curl -f http://localhost:8000/health &>/dev/null; then
            log "${GREEN}✓ Project Phoenix is operational${NC}"
            break
        fi
        echo -n "."
        sleep 2
    done
} >> "$LOG_FILE" 2>&1

# Step 9: Verify deployment
log "${BLUE}[9/10] Verifying deployment...${NC}"
{
    log "Checking system health..."
    
    # Check database
    if docker exec phoenix_db pg_isready -U phoenix_admin -d project_phoenix &>/dev/null; then
        log "${GREEN}✓ PostgreSQL: Healthy${NC}"
    else
        log "${RED}✗ PostgreSQL: Unhealthy${NC}"
    fi
    
    # Check Ollama
    if docker exec phoenix_ollama curl -f http://localhost:11434/api/tags &>/dev/null; then
        log "${GREEN}✓ Ollama: Healthy${NC}"
    else
        log "${RED}✗ Ollama: Unhealthy${NC}"
    fi
    
    # Check Phoenix
    if docker exec project_phoenix_app curl -f http://localhost:8000/health &>/dev/null; then
        log "${GREEN}✓ Project Phoenix: Healthy${NC}"
    else
        log "${RED}✗ Project Phoenix: Unhealthy${NC}"
    fi
    
    # Show container status
    log "\nContainer Status:"
    docker-compose -f docker-compose.prod.yml ps
    
} >> "$LOG_FILE" 2>&1

# Step 10: Display final summary
log "${BLUE}[10/10] Deployment complete!${NC}"
{
    echo ""
    log "${CYAN}"
    log "╔════════════════════════════════════════════════════════════════════════════╗"
    log "║                  ✅ DEPLOYMENT SUCCESSFUL                                  ║"
    log "╚════════════════════════════════════════════════════════════════════════════╝"
    log "${NC}"
    
    echo ""
    log "${GREEN}Services Running:${NC}"
    log "  📊 PostgreSQL Database  → localhost:5432"
    log "  🤖 Ollama LLM          → http://localhost:11434"
    log "  🚀 Project Phoenix      → http://localhost:8000"
    log ""
    
    log "${GREEN}API Endpoints:${NC}"
    log "  GET  http://localhost:8000/health              - System health"
    log "  GET  http://localhost:8000/llm/health          - LLM status"
    log "  POST http://localhost:8000/llm/analyze_error   - Error analysis"
    log "  POST http://localhost:8000/llm/detect_patterns - Pattern detection"
    log "  POST http://localhost:8000/llm/optimize        - Optimization"
    log ""
    
    log "${GREEN}Database Access:${NC}"
    log "  Host:     localhost"
    log "  Port:     5432"
    log "  User:     phoenix_admin"
    log "  Database: project_phoenix"
    log "  Password: Check .env.production"
    log ""
    
    log "${GREEN}Database Management:${NC}"
    log "  psql -h localhost -U phoenix_admin -d project_phoenix"
    log ""
    
    log "${GREEN}Useful Commands:${NC}"
    log "  View logs:      docker-compose -f docker-compose.prod.yml logs -f"
    log "  Stop system:    docker-compose -f docker-compose.prod.yml down"
    log "  Restart system: docker-compose -f docker-compose.prod.yml restart"
    log "  Check status:   docker-compose -f docker-compose.prod.yml ps"
    log ""
    
    log "${YELLOW}💰 COST: $0 FOREVER${NC}"
    log "  ✓ PostgreSQL       - Free, open-source"
    log "  ✓ Ollama           - Free, local LLM"
    log "  ✓ Mistral 7B       - Free model"
    log "  ✓ Docker           - Free container runtime"
    log "  ✓ Project Phoenix  - Free framework"
    log ""
    
    log "${YELLOW}🔒 SECURITY NOTES:${NC}"
    log "  ⚠ Change .env.production passwords immediately!"
    log "  ⚠ Enable firewall for production"
    log "  ⚠ Use HTTPS in production (update nginx.conf)"
    log "  ⚠ Regular database backups recommended"
    log ""
    
    log "${YELLOW}📝 DEPLOYMENT LOG:${NC}"
    log "  Log file: $LOG_FILE"
    log ""
    
} >> "$LOG_FILE" 2>&1

echo -e "${GREEN}✅ Deployment complete! System is running and ready to use.${NC}"
echo ""
echo "Next steps:"
echo "1. Update .env.production with secure passwords"
echo "2. Test endpoints: curl http://localhost:8000/health"
echo "3. Access database: psql -h localhost -U phoenix_admin -d project_phoenix"
echo ""
echo "See deployment.log for full details."
