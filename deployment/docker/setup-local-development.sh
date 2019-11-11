#!/bin/bash

# Local Development Setup Script for MCP Servers
# Software House & Real Estate LLC MCP Development Environment

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/local-servers/docker-compose-dev.yml"
ENV_FILE="$PROJECT_ROOT/local-servers/.env.development"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."

    local missing_tools=()

    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    fi

    if ! command -v docker-compose &> /dev/null; then
        missing_tools+=("docker-compose")
    fi

    if ! command -v node &> /dev/null; then
        missing_tools+=("nodejs")
    fi

    if ! command -v python3 &> /dev/null; then
        missing_tools+=("python3")
    fi

    if ! command -v git &> /dev/null; then
        missing_tools+=("git")
    fi

    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        error "Missing required tools: ${missing_tools[*]}"
        info "Please install the missing tools and run this script again."
        exit 1
    fi

    log "All prerequisites are installed"
}

# Create development environment file
create_env_file() {
    log "Creating development environment file..."

    cat > "$ENV_FILE" << 'EOF'
# MCP Servers Development Environment
# Copy this file and update with your actual credentials

# Environment
NODE_ENV=development
MCP_ENVIRONMENT=development
LOG_LEVEL=debug

# Development ports (starting from 3001)
GITHUB_PORT=3001
DOCKER_PORT=3002
POSTGRESQL_PORT=3003
POSTMAN_PORT=3004
AZUREDEVOPS_PORT=3005
JFROG_PORT=3006
CLOUDFLARE_PORT=3007
SLACK_PORT=3008
NOTION_PORT=3009
XERO_PORT=3010
REALESTATE_CRM_PORT=3011
BATCHDATA_REALESTATE_PORT=3012
ZILLOW_PORT=3013
FILESYSTEM_PORT=3014
CALENDAR_PORT=3015

# Development credentials (replace with your actual credentials)
GITHUB_TOKEN=REDACTED_TOKEN
POSTGRESQL_CONNECTION_STRING=postgresql://REDACTED_USER:REDACTED_PASS@REDACTED_HOST
POSTMAN_API_KEY=REDACTED_API_KEY
AZURE_DEVOPS_TOKEN=REDACTED_TOKEN
AZURE_DEVOPS_ORG=your_organization

# Security & Monitoring
JFROG_URL=https://your-org.jfrog.io
JFROG_TOKEN=your_jfrog_token
CLOUDFLARE_API_TOKEN=REDACTED_TOKEN
CLOUDFLARE_ZONE_ID=your_zone_id

# Business Operations
SLACK_BOT_TOKEN=REDACTED_TOKEN
SLACK_SIGNING_SECRET=your_slack_signing_secret
NOTION_TOKEN=REDACTED_TOKEN
XERO_CLIENT_ID=your_xero_client_id
XERO_CLIENT_SECRET=your_xero_client_secret

# Real Estate
RECRM_API_KEY=REDACTED_API_KEY
BATCHDATA_API_KEY=REDACTED_API_KEY
ZILLOW_API_KEY=your_zillow_api_key

# Productivity
GOOGLE_CALENDAR_CREDENTIALS=your_google_calendar_json_credentials
ALLOWED_FILE_PATHS=/home,/tmp,/workspace

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
GRAFANA_ADMIN_PASSWORD=admin

# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=REDACTED_PASSWORD
POSTGRES_DB=mcp_dev
REDIS_PORT=6379
EOF

    info "Environment file created at $ENV_FILE"
    warn "Please edit $ENV_FILE and add your actual API keys and credentials"
}

# Create development Docker Compose file
create_docker_compose() {
    log "Creating development Docker Compose file..."

    cat > "$DOCKER_COMPOSE_FILE" << 'EOF'
version: '3.8'

services:
  # Infrastructure services
  postgres:
    image: postgres:15-alpine
    container_name: mcp-postgres-dev
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD=REDACTED_PASSWORD
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    networks:
      - mcp-dev
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: mcp-redis-dev
    ports:
      - "${REDIS_PORT}:6379"
    volumes:
      - redis_data:/data
    networks:
      - mcp-dev
    command: redis-server --appendonly yes

  # Core Development MCP Servers
  github-mcp:
    build:
      context: ./servers/github
      dockerfile: Dockerfile.dev
    container_name: mcp-github-dev
    environment:
      - PORT=${GITHUB_PORT}
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - NODE_ENV=development
    ports:
      - "${GITHUB_PORT}:${GITHUB_PORT}"
    volumes:
      - ./servers/github:/app
      - /app/node_modules
    networks:
      - mcp-dev
    depends_on:
      - redis

  docker-mcp:
    build:
      context: ./servers/docker
      dockerfile: Dockerfile.dev
    container_name: mcp-docker-dev
    environment:
      - PORT=${DOCKER_PORT}
      - DOCKER_HOST=unix:///var/run/docker.sock
    ports:
      - "${DOCKER_PORT}:${DOCKER_PORT}"
    volumes:
      - ./servers/docker:/app
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - mcp-dev

  postgresql-mcp:
    build:
      context: ./servers/postgresql
      dockerfile: Dockerfile.dev
    container_name: mcp-postgresql-dev
    environment:
      - PORT=${POSTGRESQL_PORT}
      - DATABASE_URI=${POSTGRESQL_CONNECTION_STRING}
    ports:
      - "${POSTGRESQL_PORT}:${POSTGRESQL_PORT}"
    volumes:
      - ./servers/postgresql:/app
    networks:
      - mcp-dev
    depends_on:
      postgres:
        condition: service_healthy

  postman-mcp:
    build:
      context: ./servers/postman
      dockerfile: Dockerfile.dev
    container_name: mcp-postman-dev
    environment:
      - PORT=${POSTMAN_PORT}
      - POSTMAN_API_KEY=${POSTMAN_API_KEY}
    ports:
      - "${POSTMAN_PORT}:${POSTMAN_PORT}"
    volumes:
      - ./servers/postman:/app
      - /app/node_modules
    networks:
      - mcp-dev

  # Business Operations MCP Servers
  slack-mcp:
    build:
      context: ./servers/slack
      dockerfile: Dockerfile.dev
    container_name: mcp-slack-dev
    environment:
      - PORT=${SLACK_PORT}
      - SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN}
      - SLACK_SIGNING_SECRET=${SLACK_SIGNING_SECRET}
    ports:
      - "${SLACK_PORT}:${SLACK_PORT}"
    volumes:
      - ./servers/slack:/app
      - /app/node_modules
    networks:
      - mcp-dev

  notion-mcp:
    build:
      context: ./servers/notion
      dockerfile: Dockerfile.dev
    container_name: mcp-notion-dev
    environment:
      - PORT=${NOTION_PORT}
      - NOTION_TOKEN=${NOTION_TOKEN}
    ports:
      - "${NOTION_PORT}:${NOTION_PORT}"
    volumes:
      - ./servers/notion:/app
      - /app/node_modules
    networks:
      - mcp-dev

  # Real Estate MCP Servers
  realestate-crm-mcp:
    build:
      context: ./servers/realestate-crm
      dockerfile: Dockerfile.dev
    container_name: mcp-realestate-crm-dev
    environment:
      - PORT=${REALESTATE_CRM_PORT}
      - RECRM_API_KEY=${RECRM_API_KEY}
    ports:
      - "${REALESTATE_CRM_PORT}:${REALESTATE_CRM_PORT}"
    volumes:
      - ./servers/realestate-crm:/app
      - /app/node_modules
    networks:
      - mcp-dev

  zillow-mcp:
    build:
      context: ./servers/zillow
      dockerfile: Dockerfile.dev
    container_name: mcp-zillow-dev
    environment:
      - PORT=${ZILLOW_PORT}
      - ZILLOW_API_KEY=${ZILLOW_API_KEY}
    ports:
      - "${ZILLOW_PORT}:${ZILLOW_PORT}"
    volumes:
      - ./servers/zillow:/app
    networks:
      - mcp-dev

  # Monitoring & Management
  prometheus:
    image: prom/prometheus:latest
    container_name: mcp-prometheus-dev
    ports:
      - "${PROMETHEUS_PORT}:9090"
    volumes:
      - ./monitoring/prometheus-dev.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    networks:
      - mcp-dev

  grafana:
    image: grafana/grafana:latest
    container_name: mcp-grafana-dev
    ports:
      - "${GRAFANA_PORT}:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=REDACTED_PASSWORD
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning
    networks:
      - mcp-dev
    depends_on:
      - prometheus

  # Development tools
  mcp-dev-dashboard:
    build:
      context: ./tools/dashboard
      dockerfile: Dockerfile
    container_name: mcp-dashboard-dev
    ports:
      - "8080:8080"
    environment:
      - MCP_SERVERS_CONFIG=/app/config/servers.json
    volumes:
      - ./tools/dashboard:/app
      - ./config:/app/config
    networks:
      - mcp-dev

networks:
  mcp-dev:
    driver: bridge
    ipam:
      config:
        - subnet: 172.21.0.0/16

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
EOF

    log "Development Docker Compose file created"
}

# Create server directories with basic Dockerfiles
create_server_structure() {
    log "Creating server directory structure..."

    local servers=(
        "github:nodejs"
        "docker:python"
        "postgresql:golang"
        "postman:nodejs"
        "slack:nodejs"
        "notion:nodejs"
        "realestate-crm:nodejs"
        "zillow:python"
    )

    for server_info in "${servers[@]}"; do
        IFS=':' read -r server type <<< "$server_info"
        local server_dir="$PROJECT_ROOT/local-servers/servers/$server"

        mkdir -p "$server_dir"

        # Create development Dockerfile
        case "$type" in
            "nodejs")
                cat > "$server_dir/Dockerfile.dev" << 'EOF'
FROM node:20-alpine

WORKDIR /app

# Install development dependencies
RUN apk add --no-cache git curl

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Development command with hot reload
CMD ["npm", "run", "dev"]
EOF
                ;;
            "python")
                cat > "$server_dir/Dockerfile.dev" << 'EOF'
FROM python:3.11-alpine

WORKDIR /app

# Install development dependencies
RUN apk add --no-cache git curl gcc musl-dev

# Copy requirements
COPY requirements*.txt ./

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Development command
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000", "--reload"]
EOF
                ;;
            "golang")
                cat > "$server_dir/Dockerfile.dev" << 'EOF'
FROM golang:1.21-alpine

WORKDIR /app

# Install development dependencies
RUN apk add --no-cache git curl

# Copy go mod files
COPY go.* ./

# Download dependencies
RUN go mod download

# Copy source code
COPY . .

# Build application
RUN go build -o main .

# Expose port
EXPOSE 3000

# Development command
CMD ["./main"]
EOF
                ;;
        esac

        # Create basic package.json for Node.js servers
        if [[ "$type" == "nodejs" ]]; then
            cat > "$server_dir/package.json" << EOF
{
  "name": "mcp-$server-server",
  "version": "1.0.0",
  "description": "MCP Server for $server",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "dev": "nodemon index.js",
    "test": "jest"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0",
    "express": "^4.18.0",
    "dotenv": "^16.0.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.0",
    "jest": "^29.0.0"
  }
}
EOF
        fi

        # Create basic requirements.txt for Python servers
        if [[ "$type" == "python" ]]; then
            cat > "$server_dir/requirements.txt" << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
python-dotenv==1.0.0
httpx==0.25.0
pydantic==2.5.0
mcp==1.0.0
EOF
        fi

        info "Created server structure for $server ($type)"
    done
}

# Create monitoring configuration
create_monitoring_config() {
    log "Creating monitoring configuration..."

    mkdir -p "$PROJECT_ROOT/local-servers/monitoring"

    # Prometheus configuration
    cat > "$PROJECT_ROOT/local-servers/monitoring/prometheus-dev.yml" << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'mcp-servers'
    static_configs:
      - targets:
        - 'github-mcp:3001'
        - 'docker-mcp:3002'
        - 'postgresql-mcp:3003'
        - 'postman-mcp:3004'
        - 'slack-mcp:3008'
        - 'notion-mcp:3009'
        - 'realestate-crm-mcp:3011'
        - 'zillow-mcp:3013'
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'infrastructure'
    static_configs:
      - targets:
        - 'postgres:5432'
        - 'redis:6379'
EOF

    # Grafana provisioning
    mkdir -p "$PROJECT_ROOT/local-servers/monitoring/grafana/provisioning/datasources"
    mkdir -p "$PROJECT_ROOT/local-servers/monitoring/grafana/provisioning/dashboards"

    cat > "$PROJECT_ROOT/local-servers/monitoring/grafana/provisioning/datasources/prometheus.yml" << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

    log "Monitoring configuration created"
}

# Create management scripts
create_management_scripts() {
    log "Creating management scripts..."

    # Start script
    cat > "$PROJECT_ROOT/local-servers/start-dev.sh" << 'EOF'
#!/bin/bash
set -e

echo "Starting MCP Development Environment..."

# Check if .env file exists
if [[ ! -f .env.development ]]; then
    echo "Error: .env.development file not found!"
    echo "Please run setup-local-development.sh first"
    exit 1
fi

# Load environment variables
export $(grep -v '^#' .env.development | xargs)

# Start services
docker-compose -f docker-compose-dev.yml up -d

echo "Development environment started!"
echo ""
echo "Services available at:"
echo "  - MCP Dashboard: http://localhost:8080"
echo "  - Grafana: http://localhost:${GRAFANA_PORT} (admin/admin)"
echo "  - Prometheus: http://localhost:${PROMETHEUS_PORT}"
echo ""
echo "MCP Servers:"
echo "  - GitHub: http://localhost:${GITHUB_PORT}"
echo "  - Docker: http://localhost:${DOCKER_PORT}"
echo "  - PostgreSQL: http://localhost:${POSTGRESQL_PORT}"
echo "  - Postman: http://localhost:${POSTMAN_PORT}"
echo "  - Slack: http://localhost:${SLACK_PORT}"
echo "  - Notion: http://localhost:${NOTION_PORT}"
echo "  - Real Estate CRM: http://localhost:${REALESTATE_CRM_PORT}"
echo "  - Zillow: http://localhost:${ZILLOW_PORT}"
EOF

    chmod +x "$PROJECT_ROOT/local-servers/start-dev.sh"

    # Stop script
    cat > "$PROJECT_ROOT/local-servers/stop-dev.sh" << 'EOF'
#!/bin/bash
set -e

echo "Stopping MCP Development Environment..."

docker-compose -f docker-compose-dev.yml down

echo "Development environment stopped!"
EOF

    chmod +x "$PROJECT_ROOT/local-servers/stop-dev.sh"

    # Status script
    cat > "$PROJECT_ROOT/local-servers/status-dev.sh" << 'EOF'
#!/bin/bash

echo "MCP Development Environment Status:"
echo "=================================="

docker-compose -f docker-compose-dev.yml ps

echo ""
echo "Health Checks:"
echo "=============="

services=("github-mcp:3001" "docker-mcp:3002" "postgresql-mcp:3003" "postman-mcp:3004")

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if curl -sf "http://localhost:$port/health" >/dev/null 2>&1; then
        echo "✅ $name - Healthy"
    else
        echo "❌ $name - Unhealthy"
    fi
done
EOF

    chmod +x "$PROJECT_ROOT/local-servers/status-dev.sh"

    log "Management scripts created"
}

# Main setup function
main() {
    log "Setting up MCP Servers Local Development Environment"
    log "=================================================="

    check_prerequisites

    # Create directory structure
    mkdir -p "$PROJECT_ROOT/local-servers"
    mkdir -p "$PROJECT_ROOT/local-servers/servers"
    mkdir -p "$PROJECT_ROOT/local-servers/config"
    mkdir -p "$PROJECT_ROOT/local-servers/tools/dashboard"

    create_env_file
    create_docker_compose
