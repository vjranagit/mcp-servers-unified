# MCP Servers - Unified Collection

**Consolidated repository for all Model Context Protocol (MCP) server implementations, deployment infrastructure, and automation tools.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Table of Contents

- [Overview](#overview)
- [Repository Structure](#repository-structure)
- [Available MCP Servers](#available-mcp-servers)
- [Quick Start](#quick-start)
- [Deployment Options](#deployment-options)
- [Configuration](#configuration)
- [Documentation](#documentation)
- [Scripts and Utilities](#scripts-and-utilities)
- [Contributing](#contributing)

## 🎯 Overview

This repository consolidates all MCP-related assets including:
- ✅ **5 MCP Server Implementations** (Gmail, Enhanced Gmail, Zabbix, ELK, Template)
- ✅ **3 Deployment Methods** (Kubernetes, Ansible, Docker)
- ✅ **10+ Utility Scripts** (Testing, CLI tools, Automation)
- ✅ **Comprehensive Documentation** (Setup, Deployment, Configuration)
- ✅ **Configuration Templates** (All servers with examples)

### What is MCP?

Model Context Protocol (MCP) is an open protocol that enables AI assistants like Claude to securely connect to external data sources and tools. This repository provides production-ready MCP server implementations for various services.

## 📁 Repository Structure

```
mcp-servers/
├── servers/                           # MCP Server Implementations
│   ├── gmail/                         # Gmail MCP Server v2.1
│   ├── enhanced-gmail/                # Enhanced Gmail with advanced features
│   ├── zabbix/                        # Zabbix Monitoring MCP Server
│   ├── elk/                           # Elasticsearch/Kibana MCP Server
│   └── template/                      # Base template for new servers
│
├── deployment/                        # Deployment Infrastructure
│   ├── kubernetes/                    # K8s manifests and configs
│   ├── ansible/                       # Ansible playbooks and roles
│   ├── docker/                        # Docker Compose configurations
│   └── scripts/                       # Deployment automation scripts
│
├── configs/                           # Configuration Templates
│   ├── gmail/                         # Gmail configuration examples
│   ├── elk/                           # ELK configuration examples
│   ├── zabbix/                        # Zabbix configuration examples
│   └── claude-mcp-examples/           # Claude integration examples
│
├── docs/                              # Documentation
│   ├── setup/                         # Setup guides for each server
│   ├── deployment/                    # Deployment documentation
│   ├── testing/                       # Testing guides and results
│   └── quick-reference.md             # Quick reference guide
│
├── scripts/                           # Utility Scripts
│   ├── testing/                       # Test scripts for all servers
│   ├── cli/                           # Command-line interface tools
│   ├── automation/                    # Automation and IaC scripts
│   └── utilities/                     # General utility scripts
│
└── reports/                           # Reports and Logs
    ├── test-results/                  # Test execution results
    └── deployment-reports/            # Deployment summaries

```

## 🚀 Available MCP Servers

### 1. Gmail MCP Server
**Version:** 2.1
**Location:** `servers/gmail/`
**Features:**
- 16 Gmail operations (search, send, read, modify)
- Label management and organization
- Attachment handling (list, download)
- Draft management (create, update, send)
- Thread conversation tracking
- HTML email support

**Quick Start:**
```bash
cd servers/gmail
pip install -r requirements.txt
python server.py
```

### 2. Enhanced Gmail MCP Server
**Location:** `servers/enhanced-gmail/`
**Features:**
- All standard Gmail operations
- Advanced search with filters
- Bulk operations support
- Email templates
- Scheduled sending
- Advanced attachment processing

### 3. Zabbix MCP Server
**Version:** 1.0
**Location:** `servers/zabbix/`
**Features:**
- Host and hostgroup management
- Template operations
- Monitoring item queries
- Trigger and alarm management
- User administration
- Maintenance window scheduling

**Quick Start:**
```bash
cd servers/zabbix
pip install -r requirements.txt
python server.py
```

### 4. ELK Stack MCP Server
**Location:** `servers/elk/`
**Features:**
- Elasticsearch cluster management
- Log searching and analysis
- Index management
- Aggregated analytics
- Error pattern detection
- Performance statistics

**Quick Start:**
```bash
cd servers/elk
pip install -r requirements.txt
python server.py
```

### 5. MCP Server Template
**Location:** `servers/template/`
**Purpose:** Base template for creating new MCP servers
**Includes:**
- Base server class with MCP protocol implementation
- Authentication patterns (OAuth, API Key, Basic Auth)
- Error handling and logging
- Configuration management
- Testing framework
- Documentation templates

## ⚡ Quick Start

### Prerequisites

- Python 3.8+ or Node.js 18+
- Claude Desktop or Claude Code CLI
- Git

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/vjranagit/mcp-servers-unified.git
cd mcp-servers-unified
```

2. **Choose a server and install dependencies:**
```bash
# Example: Gmail MCP Server
cd servers/gmail
pip install -r requirements.txt
```

3. **Configure the server:**
```bash
# Copy example config
cp ../../configs/gmail/config.example.json ~/.gmail-mcp/config.json
# Edit with your credentials
```

4. **Add to Claude configuration:**
```bash
# Add to ~/.claude.json
{
  "mcpServers": {
    "gmail": {
      "command": "python",
      "args": ["/absolute/path/to/servers/gmail/server.py"]
    }
  }
}
```

5. **Test the server:**
```bash
scripts/testing/test_gmail_mcp.sh
```

## 🏗️ Deployment Options

### Option 1: Local Docker Deployment

Perfect for development and testing:

```bash
cd deployment/docker
docker-compose up -d
```

**Features:**
- All MCP servers in containers
- Shared networking
- Persistent volumes
- Monitoring stack included

### Option 2: Kubernetes Deployment

Production-ready cluster deployment:

```bash
cd deployment/kubernetes
kubectl apply -f namespace.yaml
kubectl apply -f deployments/
```

**Features:**
- Auto-scaling
- High availability
- Health checks
- Resource management
- Secrets management

### Option 3: Ansible Automation

Infrastructure as Code deployment:

```bash
cd deployment/ansible
ansible-playbook -i inventory playbooks/deploy-all-mcp-servers.yml
```

**Features:**
- Multi-host deployment
- Configuration management
- Idempotent operations
- Role-based organization

## ⚙️ Configuration

### Environment Variables

Each MCP server supports configuration via environment variables:

**Gmail:**
```bash
export GMAIL_CREDENTIALS=/path/to/credentials.json
export GMAIL_TOKEN=/path/to/token.json
export GMAIL_PORT=8080
```

**Zabbix:**
```bash
export ZABBIX_URL=http://zabbix-server/api_jsonrpc.php
export ZABBIX_USERNAME=your_username
export ZABBIX_PASSWORD=REDACTED_PASSWORD
```

**ELK:**
```bash
export ELASTICSEARCH_URL=http://localhost:9200
export ELASTICSEARCH_USERNAME=elastic
export ELASTICSEARCH_PASSWORD=REDACTED_PASSWORD
```

### Configuration Files

All servers support JSON configuration files in `~/.{server-name}-mcp/config.json`

See [Configuration Guide](configs/README.md) for details.

## 📚 Documentation

### Setup Guides
- [Gmail MCP Setup](docs/setup/general-setup.md)
- [Gemini Integration Setup](docs/setup/gemini-setup.md)
- [GitHub MCP Setup](docs/setup/github-setup.md)
- [Configuration Guide](docs/setup/configuration-guide.md)

### Deployment Documentation
- [Kubernetes Deployment](docs/deployment/production-setup.md)
- [Ansible Deployment](docs/deployment/remote-setup.md)
- [Docker Deployment](docs/deployment/usage-guide.md)
