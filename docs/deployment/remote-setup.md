# Remote Services Configuration for MCP Servers

Configuration guide for using Zabbix and ELK MCP servers with remote instances on 192.168.1.2.

## Current Status

### Found on 192.168.1.2:

**Zabbix Deployment:**
- ✅ zabbix-db: Running (PostgreSQL 13)
- ⚠️  zabbix-server: Running but UNHEALTHY
- ⚠️  zabbix-web: Running but UNHEALTHY
- Port: 8082 (bound to localhost only)
- API Endpoint: http://localhost:8082/api_jsonrpc.php
- Credentials: Admin / zabbix (from docker-compose)

**ELK Stack Deployment:**
- ⚠️  Elasticsearch: Running but initializing
- ❌ Kibana: Restarting (has issues)
- ❌ Filebeat: Restarting (has issues)
- Port: 9200 (accessible externally)
- API Endpoint: http://192.168.1.2:9200
- Credentials: elastic / changeme

## Quick Start

### 1. Check Service Health

```bash
cd /home/vjrana/mcp-servers
./check_remote_services.sh
```

This script will:
- Check all container statuses
- Test API connectivity
- Offer to restart unhealthy containers
- Provide troubleshooting guidance

### 2. Configure Zabbix MCP

Once Zabbix is healthy:

```bash
cd /home/vjrana/mcp-servers/zabbix

# Option 1: Automatic configuration (creates SSH tunnel)
python3 config_remote.py

# Option 2: With custom settings
python3 config_remote.py --tunnel-port 18082 --username Admin --password zabbix

# Option 3: Skip tunnel (if Zabbix is publicly accessible)
python3 config_remote.py --no-tunnel --remote-host 192.168.1.2
```

Configuration saves to: `~/.zabbix-mcp/config.json`

### 3. Configure ELK MCP

Once Elasticsearch is responding:

```bash
cd /home/vjrana/mcp-servers/elk

# Automatic configuration
python3 config_remote.py

# With custom settings
python3 config_remote.py --host 192.168.1.2 --username elastic --password changeme
```

Configuration saves to: `~/.elk-mcp/config.json`

## Troubleshooting

### Zabbix Issues

**Problem: Containers are UNHEALTHY**

Check logs:
```bash
ssh 192.168.1.2 'docker logs zabbix-server 2>&1 | tail -50'
ssh 192.168.1.2 'docker logs zabbix-web 2>&1 | tail -50'
```

Common issues:
- Database connection problems
- Missing Zabbix agent on monitored hosts
- Configuration errors

**Fix: Restart containers**
```bash
ssh 192.168.1.2 'cd Projects/infra/ansible-nas/config/zabbix && docker-compose restart'

# Wait 30 seconds for initialization
sleep 30

# Check status
ssh 192.168.1.2 'docker ps | grep zabbix'
```

**Problem: API not responding**

Test manually:
```bash
ssh 192.168.1.2 'curl -X POST -H "Content-Type: application/json" \
  -d "{\"jsonrpc\":\"2.0\",\"method\":\"apiinfo.version\",\"params\":{},\"id\":1}" \
  http://localhost:8082/api_jsonrpc.php'
```

Expected response:
```json
{"jsonrpc":"2.0","result":"6.0.0","id":1}
```

**Problem: Cannot access from local machine**

Zabbix web is bound to localhost only. Use SSH tunnel:
```bash
# Create tunnel
ssh -f -N -L 18082:localhost:8082 192.168.1.2

# Test through tunnel
curl -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"apiinfo.version","params":{},"id":1}' \
  http://localhost:18082/api_jsonrpc.php
```

### Elasticsearch Issues

**Problem: Container is restarting**

Check logs:
```bash
ssh 192.168.1.2 'docker logs docker-elk-elasticsearch-1 2>&1 | tail -100'
```

Common issues:
- Out of memory (Elasticsearch needs 2GB+ RAM)
- Disk space issues
- Configuration errors
- Slow startup (can take 60+ seconds)

**Fix: Restart Elasticsearch**
```bash
ssh 192.168.1.2 'docker restart docker-elk-elasticsearch-1'

# Wait for startup (can take 30-60 seconds)
sleep 60

# Check if ready
ssh 192.168.1.2 'curl -u elastic:changeme http://localhost:9200/_cluster/health'
```

**Problem: Authentication fails**

Check credentials in docker-compose:
```bash
ssh 192.168.1.2 'docker inspect docker-elk-elasticsearch-1 | grep -A5 Env | grep ELASTIC_PASSWORD'
```

Test with credentials:
```bash
curl -u elastic:changeme http://192.168.1.2:9200
```

**Problem: Elasticsearch very slow**

Elasticsearch requires significant resources:
- Minimum: 2GB RAM, 2 CPU cores
- Recommended: 4GB+ RAM, 4 CPU cores

Check resource usage:
```bash
ssh 192.168.1.2 'docker stats --no-stream docker-elk-elasticsearch-1'
```

### Kibana Issues

Kibana depends on Elasticsearch being healthy. If Elasticsearch is down or initializing, Kibana will restart continuously.

**Fix:**
1. Ensure Elasticsearch is healthy first
2. Restart Kibana:
```bash
ssh 192.168.1.2 'docker restart docker-elk-kibana-1'
```

## Manual Configuration

If automatic scripts don't work, configure manually:

### Zabbix MCP Manual Config

1. Create config directory:
```bash
mkdir -p ~/.zabbix-mcp
```

2. Create config file `~/.zabbix-mcp/config.json`:
```json
{
  "api_url": "http://localhost:18082/api_jsonrpc.php"
}
```

3. Create SSH tunnel:
```bash
ssh -f -N -L 18082:localhost:8082 192.168.1.2
```

4. Test and get auth token:
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"user.login","params":{"username":"Admin","password":"zabbix"},"id":1}' \
  http://localhost:18082/api_jsonrpc.php
```

5. Save auth token to `~/.zabbix-mcp/auth.txt`

### ELK MCP Manual Config

1. Create config directory:
```bash
mkdir -p ~/.elk-mcp
```

2. Create config file `~/.elk-mcp/config.json`:
```json
{
  "elasticsearch_url": "http://192.168.1.2:9200",
  "username": "elastic",
  "password": "changeme"
}
```

3. Test connectivity:
```bash
curl -u elastic:changeme http://192.168.1.2:9200/_cluster/health
```

## Using MCP Servers

After configuration, the MCP servers will automatically connect to the remote instances.

### Add to Claude Desktop

Edit `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
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

### Test MCP Tools

**Zabbix:**
- `zabbix_login` - Authenticate
- `list_hosts` - List monitored hosts
- `list_problems` - See current issues
- `get_cluster_stats` - Get statistics

**ELK:**
- `get_cluster_health` - Check Elasticsearch health
- `list_indices` - List available indices
- `search_logs` - Search log entries
- `analyze_errors` - Analyze error patterns

## Container Management

### View all services:
```bash
ssh 192.168.1.2 'docker ps -a | grep -E "(zabbix|elastic|kibana)"'
```

### Restart everything:
```bash
# Zabbix
ssh 192.168.1.2 'cd Projects/infra/ansible-nas/config/zabbix && docker-compose restart'

# Elasticsearch
ssh 192.168.1.2 'docker restart docker-elk-elasticsearch-1'
```

### Stop services:
```bash
# Zabbix
ssh 192.168.1.2 'cd Projects/infra/ansible-nas/config/zabbix && docker-compose stop'

# ELK
ssh 192.168.1.2 'docker stop docker-elk-elasticsearch-1 docker-elk-kibana-1'
```

### View logs:
```bash
# Zabbix
ssh 192.168.1.2 'docker logs -f zabbix-server'
ssh 192.168.1.2 'docker logs -f zabbix-web'

# ELK
ssh 192.168.1.2 'docker logs -f docker-elk-elasticsearch-1'
```

## Configuration Files Locations

**On remote machine (192.168.1.2):**
- Zabbix docker-compose: `/home/vjrana/Projects/infra/ansible-nas/config/zabbix/docker-compose.yml`
- Zabbix volumes: `/mnt/docker-volumes/zabbix/`
- ELK docker-compose: Look for `docker-elk` directories

**On local machine:**
- Zabbix MCP config: `~/.zabbix-mcp/config.json`
- Zabbix auth token: `~/.zabbix-mcp/auth.txt`
- ELK MCP config: `~/.elk-mcp/config.json`

## Performance Considerations

**Zabbix:**
- Low resource usage (~200MB RAM per container)
- Fast API responses
- No special requirements

**Elasticsearch:**
- High resource usage (2GB+ RAM minimum)
- Slow startup (30-60 seconds)
- Requires disk space for indices
- CPU intensive for searches

**Recommendations:**
- Ensure remote machine has adequate RAM (8GB+ total)
- Use SSD storage for Elasticsearch data
- Monitor disk space usage
- Consider increasing Elasticsearch heap size if needed

## Security Notes

1. **Zabbix:** Currently bound to localhost only (good for security)
   - Access requires SSH tunnel
   - Default credentials should be changed in production

2. **Elasticsearch:** Accessible externally on port 9200
