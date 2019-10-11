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
