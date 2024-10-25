# Remote MCP Server Deployment Summary

**Date:** 2025-01-09
**Remote Host:** 192.168.1.2
**MCP Servers:** Zabbix, ELK Stack

## What Was Found

Successfully discovered and configured existing deployments on 192.168.1.2:

### Zabbix Monitoring System
- **Version:** 6.0 (Ubuntu-based containers)
- **Components:**
  - zabbix-server (PostgreSQL backend)
  - zabbix-web (Nginx + PHP)
  - zabbix-db (PostgreSQL 13)
- **Port:** 8082 (localhost only)
- **Credentials:** Admin / zabbix
- **Status:** Running but unhealthy (needs attention)
- **Location:** `/home/vjrana/Projects/infra/ansible-nas/config/zabbix/`

### ELK Stack
- **Version:** 8.15.0
- **Components:**
  - Elasticsearch
  - Kibana
  - Filebeat, Metricbeat, Heartbeat
- **Port:** 9200 (externally accessible)
- **Credentials:** elastic / changeme
- **Status:** Elasticsearch running, Kibana/beats restarting
- **Location:** Docker containers with `docker-elk-*` prefix

## What Was Created

### 1. Configuration Scripts

#### Zabbix Configuration Tool (`zabbix/config_remote.py`)
**Features:**
- Automatic SSH tunnel creation
- API connectivity testing
- Authentication and token management
- Configuration validation
- Troubleshooting guidance

**Usage:**
```bash
cd /home/vjrana/mcp-servers/zabbix
python3 config_remote.py

# Or with options:
python3 config_remote.py --tunnel-port 18082 --username Admin --password zabbix
```

**What it does:**
1. Creates SSH tunnel to access localhost:8082
2. Tests Zabbix API connectivity
3. Authenticates and saves auth token
4. Saves configuration to `~/.zabbix-mcp/config.json`

#### ELK Configuration Tool (`elk/config_remote.py`)
**Features:**
- Elasticsearch connectivity testing
- Cluster health monitoring
- Index listing
- Configuration management
- Troubleshooting guidance

**Usage:**
```bash
cd /home/vjrana/mcp-servers/elk
python3 config_remote.py

# Or with options:
python3 config_remote.py --host 192.168.1.2 --username elastic --password changeme
```

**What it does:**
1. Tests Elasticsearch connectivity on port 9200
2. Checks cluster health
3. Lists available indices
4. Saves configuration to `~/.elk-mcp/config.json`

### 2. Health Check Script (`check_remote_services.sh`)

Comprehensive service monitoring and repair tool.

**Features:**
- Container status checks
- API connectivity testing
- Log analysis
- Automatic repair option
- Color-coded output

**Usage:**
```bash
cd /home/vjrana/mcp-servers
./check_remote_services.sh

# Or specify different host:
./check_remote_services.sh 192.168.1.3
```

**What it checks:**
- All container statuses (Up/Down/Unhealthy/Restarting)
- Zabbix API responsiveness
- Elasticsearch API responsiveness
- Cluster health
- Recent error logs

**Repair capabilities:**
- Restart unhealthy containers
- Re-initialize failed services
- Verify repairs after restart

### 3. Documentation

#### REMOTE_SETUP.md
Complete guide including:
- Quick start instructions
- Detailed troubleshooting
- Manual configuration steps
- Container management commands
- Security considerations
- Performance tips

## Current Status

### Zabbix
```
✅ Database: Running
⚠️  Server: Running but UNHEALTHY
⚠️  Web: Running but UNHEALTHY
❌ API: Not responding
```

**Issue:** Containers are unhealthy, likely due to:
- Zabbix agent connection issues
- Database connectivity problems
- Configuration errors

**Fix:** Run health check script with repair option

### Elasticsearch
```
✅ Elasticsearch: Running (just restarted)
❌ Kibana: Restarting
❌ Filebeat: Restarting
❌ API: Not yet responding (initializing)
```

**Issue:** Services recently restarted, Elasticsearch needs time to initialize (30-60 seconds)

**Fix:** Wait for Elasticsearch to fully start, then Kibana will stabilize

## Quick Start Guide

### Step 1: Check Service Health

```bash
cd /home/vjrana/mcp-servers
./check_remote_services.sh
```

Answer 'y' when prompted to automatically repair services.

### Step 2: Wait for Services

After repair, wait 1-2 minutes for services to fully initialize:
- Zabbix: ~30 seconds
- Elasticsearch: ~60 seconds

### Step 3: Configure Zabbix MCP

```bash
cd /home/vjrana/mcp-servers/zabbix
python3 config_remote.py
```

Look for:
```
✅ Zabbix API responding - Version: 6.0.0
✅ Login successful!
✅ Configuration complete!
```

### Step 4: Configure ELK MCP

```bash
cd /home/vjrana/mcp-servers/elk
python3 config_remote.py
```

Look for:
```
✅ Elasticsearch responding
   Version: 8.15.0
   Cluster: docker-cluster
✅ Configuration complete!
```

### Step 5: Add to Claude Desktop

Edit `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "gmail": {
      "command": "python",
      "args": ["/home/vjrana/mcp-servers/gmail/enhanced_server.py"]
    },
    "zabbix": {
      "command": "python",
      "args": ["/home/vjrana/mcp-servers/zabbix/server.py"]
    },
    "elk": {
      "command": "python",
      "args": ["/home/vjrana/mcp-servers/elk/server.py"]
    }
  }
}
```

### Step 6: Test in Claude

Restart Claude Desktop, then try these commands:

**Zabbix:**
- "List all monitored hosts in Zabbix"
- "Show me current problems in Zabbix"
- "Get host details for [hostname]"

**ELK:**
- "Show Elasticsearch cluster health"
- "List all indices in Elasticsearch"
- "Search logs for errors in the last 24 hours"

## Configuration Files

After successful configuration:

```
~/.zabbix-mcp/
├── config.json          # API URL configuration
└── auth.txt            # Authentication token

~/.elk-mcp/
└── config.json          # Elasticsearch URL and credentials
```

## Troubleshooting

### Zabbix Not Responding

**Check container status:**
```bash
ssh 192.168.1.2 'docker ps | grep zabbix'
```

**View logs:**
```bash
ssh 192.168.1.2 'docker logs zabbix-web 2>&1 | tail -50'
```

**Restart containers:**
```bash
ssh 192.168.1.2 'cd Projects/infra/ansible-nas/config/zabbix && docker-compose restart'
```

**Test API manually:**
```bash
ssh 192.168.1.2 'curl -X POST -H "Content-Type: application/json" \
  -d "{\"jsonrpc\":\"2.0\",\"method\":\"apiinfo.version\",\"params\":{},\"id\":1}" \
  http://localhost:8082/api_jsonrpc.php'
```

### Elasticsearch Not Responding

**Check if still starting:**
```bash
ssh 192.168.1.2 'docker ps | grep elasticsearch'
```

If status shows "Up X seconds", wait longer (needs 30-60 seconds).

**Check logs:**
```bash
ssh 192.168.1.2 'docker logs docker-elk-elasticsearch-1 2>&1 | tail -100'
```

**Restart Elasticsearch:**
```bash
ssh 192.168.1.2 'docker restart docker-elk-elasticsearch-1'
sleep 60  # Wait for startup
```

**Test API:**
```bash
curl -u elastic:changeme http://192.168.1.2:9200/_cluster/health
```

### SSH Tunnel Issues

**Check if tunnel exists:**
```bash
ps aux | grep 'ssh.*18082'
```

**Kill existing tunnel:**
```bash
pkill -f 'ssh.*18082:localhost:8082'
```

**Recreate tunnel:**
```bash
ssh -f -N -L 18082:localhost:8082 192.168.1.2
```

### MCP Server Issues

**Test MCP server manually:**
```bash
cd /home/vjrana/mcp-servers/zabbix
python3 server.py
```

Should see: "Starting zabbix MCP Server..."

**Check configuration:**
```bash
cat ~/.zabbix-mcp/config.json
cat ~/.elk-mcp/config.json
```

**Reconfigure:**
```bash
cd /home/vjrana/mcp-servers/zabbix
python3 config_remote.py

cd /home/vjrana/mcp-servers/elk
python3 config_remote.py
```

## Architecture

```
┌──────────────────┐
│  Claude Desktop  │
│  (Local Machine) │
└────────┬─────────┘
         │
         ├─────────────────────────────────────┐
         │                                     │
    ┌────▼─────┐                         ┌────▼─────┐
    │ Zabbix   │                         │   ELK    │
    │   MCP    │                         │   MCP    │
    │  Server  │                         │  Server  │
    └────┬─────┘                         └────┬─────┘
         │                                     │
