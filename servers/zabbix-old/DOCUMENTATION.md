# Zabbix MCP Server - Complete Documentation

**Version**: 2.1.0
**Last Updated**: October 2025
**License**: MIT

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Testing & Validation](#testing--validation)
7. [Security](#security)
8. [Version History](#version-history)
9. [Troubleshooting](#troubleshooting)
10. [API Reference](#api-reference)

---

## Overview

### What is Zabbix MCP Server?

Lightweight Model Context Protocol (MCP) server that provides AI assistants (Claude Code, Gemini, etc.) with comprehensive access to Zabbix monitoring infrastructure through natural language interactions.

### Architecture

**Implementation**: Subprocess wrapper around `zabbix-cli`

The server wraps the mature `zabbix-cli` command-line tool, executing commands via subprocess and parsing JSON output for MCP integration.

**Key Benefits**:
- **Minimal code**: 581 lines (60% reduction vs direct API)
- **Proven functionality**: Leverages battle-tested zabbix-cli
- **Easy maintenance**: No need to track Zabbix API changes
- **Comprehensive features**: Access to all zabbix-cli commands

---

## Features

### 24 MCP Tools Across 7 Categories

#### 1. Host Management (4 tools)
- `show_hosts` - List all monitored hosts with status and configuration
- `show_host` - Get detailed information about specific host
- `create_host` - Add new host to monitoring infrastructure
- `remove_host` - Remove host from monitoring

#### 2. Host Groups (3 tools)
- `show_hostgroups` - List all host groups with member counts
- `show_hostgroup` - Show detailed hosts in specific group
- `create_hostgroup` - Create new organizational host group

#### 3. Templates (4 tools)
- `show_templates` - List all available monitoring templates
- `show_template` - Get detailed template configuration
- `link_template_to_host` - Apply monitoring template to host
- `unlink_template_from_host` - Remove template from host

#### 4. Monitoring Items (2 tools)
- `show_items` - List all monitoring items for specific host
- `show_last_values` - Get current metric values for items

#### 5. Triggers & Alarms (3 tools)
- `show_triggers` - List configured triggers for host
- `show_alarms` - Show current active problems/alarms
- `acknowledge_event` - Acknowledge and comment on problems

#### 6. User Management (3 tools)
- `show_users` - List all Zabbix users with permissions
- `create_user` - Create new Zabbix user account
- `remove_user` - Remove user from system

#### 7. Maintenance Windows (3 tools)
- `show_maintenance_definitions` - List scheduled maintenance periods
- `create_maintenance_definition` - Schedule new maintenance window
- `remove_maintenance_definition` - Cancel maintenance period

---

## Installation

### Prerequisites

1. **Python 3.8+** with pip

2. **Install zabbix-cli**
   ```bash
   pip3 install zabbix-cli
   ```

3. **Initialize zabbix-cli**
   ```bash
   zabbix-cli-init -z http://your-zabbix-server/
   ```

### Setup MCP Server

```bash
# Clone repository
git clone https://github.com/vjranagit/zabbix-mcp-server.git
cd zabbix-mcp-server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configure Credentials

**Option 1: Configuration File**

Edit `~/.zabbix-cli/zabbix-cli.conf`:
```ini
[zabbix_api]
zabbix_api_url = http://your-zabbix-server/
cert_verify = ON
```

Create `~/.zabbix-cli_auth`:
```
username::password
```

**Option 2: Environment Variables**
```bash
export ZABBIX_URL="http://your-zabbix-server/"
export ZABBIX_USER="your-username"
export ZABBIX_PASSWORD=REDACTED_PASSWORD
```

---

## Configuration

### Claude Code Integration

Add to `~/.claude.json` (Linux) or `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "zabbix": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/zabbix-mcp-server/server.py"]
    }
  }
}
```

### Gemini CLI Integration

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "zabbix": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/zabbix-mcp-server/server.py"],
      "env": {}
    }
  }
}
```

### Other MCP Clients

The server follows standard MCP protocol and should work with any MCP-compatible client.

---

## Usage

### With Claude Code

Claude Code automatically discovers and uses MCP tools through natural language:

```
"Show me the current Zabbix alerts"
"List all monitored hosts"
"What Linux monitoring templates are available?"
"Show me all users in the Zabbix system"
"Create a maintenance window for the web servers"
```

### With Gemini CLI

```bash
# List all hosts
gemini -m gemini-2.5-flash -p 'use zabbix mcp to show all hosts'

# Show current alarms
gemini -m gemini-2.5-flash -p 'use zabbix mcp to show current alarms'

# List available templates
gemini -m gemini-2.5-flash -p 'use zabbix mcp to show all templates'

# Show users
gemini -m gemini-2.5-flash -p 'use zabbix mcp to show all users'
```

### Direct Server Testing

```bash
# Test server directly
source venv/bin/activate
python3 server.py

# Test with MCP inspector (if available)
mcp-inspector server.py
```

---

## Testing & Validation

### Comprehensive Test Results (v2.1.0)

**Test Environment**:
- Server: Subprocess wrapper (zabbix-cli backend)
- Zabbix Version: 6.0.41
- Tools Tested: 10 out of 24
- Success Rate: **100%** (all tested tools working)

**Tested Tools**:

✅ **Host Management**
- `show_hosts` - Retrieved hosts with full details (< 3s)
- `show_host` - Retrieved detailed host information (< 3s)

✅ **Host Groups**
- `show_hostgroups` - Retrieved 18+ hostgroups (< 2s)
- `show_hostgroup` - Retrieved group details (< 2s)

✅ **Templates**
- `show_templates` - Retrieved 384 templates including 20 Linux templates (< 5s)

✅ **Monitoring Items**
- `show_items` - Retrieved monitoring items for hosts (< 3s)

✅ **Triggers & Alarms**
- `show_triggers` - Retrieved trigger configurations (< 3s)
- `show_alarms` - Retrieved current active problems (< 5s)

✅ **User Management**
- `show_users` - Retrieved user accounts with permissions (< 2s)

✅ **Maintenance**
- `show_maintenance_definitions` - Retrieved maintenance schedules (< 5s)

**Performance Metrics**:
- Average response time: 2.6 seconds
- Timeout issues: 0% (fixed in v2.1.0)
- Error handling: Robust
- JSON parsing: 100% success

### Linux Templates Available

The comprehensive test discovered **20 Linux monitoring templates**:

**Main Templates (4)**:
1. Linux by Zabbix agent - Full-featured monitoring
2. Linux by Zabbix agent active - Active check mode
3. Linux by SNMP - Agentless monitoring
4. Linux by Prom - Prometheus integration

**Component Templates (16)**:
- CPU monitoring (3 variants)
- Memory monitoring (3 variants)
- Filesystem monitoring (3 variants)
- Block device monitoring (3 variants)
- Network interface monitoring (2 variants)
- Generic Linux monitoring (2 variants)

---

## Security

### Security Practices

✅ **No Hardcoded Credentials**
- All credentials via user configuration
- No default passwords in code
- CLI arguments require explicit values

✅ **Proper .gitignore**
```
# Credentials and config
*.env
.env.*
auth.txt
*.key
*.pem
credentials.json
config.json
*_auth
```

✅ **Safe Code Patterns**
- Credentials only in parameter schemas (metadata)
- No credential storage in source code
- User-provided values only

### Security Scan Results

**Repository Status**: SECURE ✅

**Findings**:
- No credentials committed to git
- Proper .gitignore protection
- Clean git history
- Auth files excluded from tracking
- All security checks passed

**Best Practices Implemented**:
1. Never commit credentials to version control
2. Use environment variables or config files (git-ignored)
3. Document credential setup without actual values
4. Use .gitignore to prevent accidents

---

## Version History

### v2.1.0 (October 2025) - Current Release

**Improvements**:
- ✅ Fixed stderr warning handling (fixes 4 tools)
