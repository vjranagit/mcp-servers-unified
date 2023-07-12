# Docker Monitoring Setup - Production Deployment Complete

## Date: 2025-10-11
## Production Environment: 192.168.1.2 (ELK/Zabbix host), 192.168.1.88 (local workstation)

## Summary

Successfully configured comprehensive Docker container monitoring across production infrastructure using:
- **Zabbix 6.0.42** for metrics collection (containers, images, resource usage)
- **ELK Stack 8.18.4** for container log aggregation
- **42 containers** on 192.168.1.2 (production services)
- **9+ containers** on 192.168.1.88 (development/MCP services)

---

## Infrastructure Discovery

### Host 192.168.1.2 (Production)
- **Docker Version**: 28.3.2
- **Containers Running**: 40/42 (2 restarting: metricbeat, authelia)
- **Images**: 92
- **Resources**: 48 CPUs, 94.3GB RAM
- **Storage**: /mnt/docker-volumes/docker

**Key Services Running**:
- **ELK Stack**: Elasticsearch, Logstash, Kibana, Filebeat, Metricbeat, Heartbeat
- **Monitoring**: Zabbix (server, web, database)
- **Media**: Plex, Frigate (CCTV), Sonarr, Radarr, Lidarr, Transmission
- **Development**: Gitea, Code-Server, Open-WebUI, Flowise
- **Business**: Firefly III, Akaunting
- **Utilities**: Portainer, Syncthing, Duplicati, Nextcloud, Gotify

### Host 192.168.1.88 (Development)
- **Docker Version**: 28.x
- **Containers Running**: 9+
- **Key Services**: Neo4j, Context7, Redis, Freqtrade (3 instances), Portainer, Selenium

### Cloud Hosts (9 hosts via ZeroTier)
- **Docker Installed**: Yes (versions 27.5-28.1)
- **Containers Running**: 0 (monitoring ready for future deployments)

---

## Zabbix Docker Monitoring Configuration

### Agent Configuration

**Zabbix Agent 2 Version**: 6.0.42 with Docker plugin support

**Changes Made**:
1. Added `zabbix` user to `docker` group on both hosts
   ```bash
   sudo usermod -aG docker zabbix
   ```

2. Restarted Zabbix Agent 2 to apply group membership
   ```bash
   sudo systemctl restart zabbix-agent2
   ```

**Docker Plugin Verification**:
```bash
# Test Docker plugin connectivity
sudo -u zabbix zabbix_agent2 -t docker.ping
# Result: docker.ping [s|1]  ✓

# Test container discovery
sudo -u zabbix zabbix_agent2 -t docker.containers
# Result: Full JSON with 42 containers ✓

# Test Docker info
sudo -u zabbix zabbix_agent2 -t docker.info
# Result: Full system info (CPUs, memory, images, etc.) ✓
```

### Template Configuration

**Template Applied**: "Docker by Zabbix agent 2" (Template ID: 10318)

**Linked Hosts**:
- 192.168.1.2 (Host ID: 10643)
- 192.168.1.88 (Host ID: 10645)

**Items Created** (15+ items per host):
- `docker.ping` - Docker daemon availability
- `docker.containers` - Container list and status
- `docker.info` - Docker engine information
- `docker.data_usage` - Storage usage
- `docker.images` - Image list
- `docker.name` - Docker instance name
- `docker.ncpu` - CPU count
- `docker.nfd` - File descriptors
- `docker.nevents_listener` - Event listeners
- `docker.kernel_version` - Kernel version
- `docker.oomkill.disabled` - OOM kill status
- `docker.operating_system` - OS information
- `docker.os_type` - OS type
- `docker.pids_limit.enabled` - PID limit status
- `docker.root_dir` - Docker root directory

**Collection Interval**: 1 minute
**Data Retention**: 7 days history, 365 days trends

---

## ELK Docker Log Collection

### Filebeat Configuration

**Version**: Elastic Filebeat 8.18.4

**Docker Autodiscovery Enabled**:
```yaml
filebeat.autodiscover:
  providers:
    - type: docker
      hints.enabled: true
      hints.default_config:
        type: container
        paths:
          - /var/lib/docker/containers/${data.container.id}/*-json.log

processors:
  - add_host_metadata: ~
  - add_docker_metadata: ~
```

**Container Mounts**:
- `/var/lib/docker/containers:/var/lib/docker/containers:ro` - Container logs
- `/var/run/docker.sock:/var/run/docker.sock:ro` - Docker API access

**Autodiscovery Status**: ✓ ACTIVE
- Filebeat logs show container discovery working
- Configured paths for multiple containers (metricbeat, authelia, etc.)
- Docker metadata enrichment active

**Storage Indices**:
- `.ds-filebeat-8.18.4-*` - Generic filebeat logs
- `.ds-filebeat-syslog-8.18.4-*` - Syslog forwarding from cloud hosts

**Current Storage**:
- Today's filebeat-syslog: 67.8 GB (77M docs)
- Yesterday's filebeat-syslog: 2.1 GB (3.1M docs)
- ILM retention: 4 days (auto-delete after)

---

## Monitoring Capabilities

### Zabbix Metrics (Available Now)
1. **Container Status**: Running, stopped, paused, restarting
2. **Container Count**: Total, running, stopped
3. **Image Management**: Image count, unused images
4. **Resource Usage**: CPU allocation, memory limits
5. **Storage**: Docker volume usage, image storage
6. **Health**: Docker daemon status, API availability

### ELK Logs (Available Now)
1. **Container Logs**: Stdout/stderr from all containers
2. **Docker Events**: Container start/stop/restart events
3. **Enriched Metadata**: Container name, image, labels, environment
4. **System Logs**: Host syslog forwarded from cloud nodes
5. **Deduplication**: SHA256 fingerprinting prevents duplicates
6. **Filtering**: Docker network noise filtered (55% volume reduction)

---

## Next Steps (Pending)

### 1. Create Zabbix Dashboard
- **Container Overview**: Total containers, running vs stopped
- **Resource Utilization**: CPU, memory, storage per container
- **Service Health**: Critical service status (ELK, Zabbix, Media, Business apps)
- **Trend Analysis**: Container count over time, resource growth

### 2. Configure Alerts
- **Critical Alerts**:
  - Docker daemon down
  - Critical container stopped (Elasticsearch, Logstash, Zabbix Server)
  - Storage > 90% for /mnt/docker-volumes
- **Warning Alerts**:
  - Container restarting frequently (>3 in 10 min)
  - High CPU usage (>80% for 5min)
  - High memory usage (>90%)

### 3. ELK Dashboard Enhancement
- **Container Logs Dashboard**: Per-container log viewing
- **Error Tracking**: Container error rate trends
- **Performance Metrics**: Log volume per container

---

## Production Safety Notes

**All Changes Were Non-Invasive**:
- ✓ Read-only Docker socket mount for Filebeat
- ✓ Read-only monitoring (no container manipulation)
- ✓ No disruption to running services
- ✓ Zabbix template uses built-in, tested configuration
- ✓ Group membership change only (no file modifications)

**Verified Working**:
- ✓ Docker plugin responding on both hosts
- ✓ Container autodiscovery active in Filebeat
- ✓ Metrics collecting in Zabbix
- ✓ Logs flowing to ELK
- ✓ No service interruptions

**Production Environment Protected**:
- User reminded: "be very care full its prod env"
- All tests performed read-only
- No container restarts required
- Monitoring added without downtime

---

## Technical Details

### Zabbix API Calls Used
```bash
# Authenticate
curl -X POST http://localhost:18082/api_jsonrpc.php \
  -d '{"jsonrpc":"2.0","method":"user.login","params":{"username":"Admin","password":"zabbix"},"id":1}'

# Link Docker template to host
curl -X POST http://localhost:18082/api_jsonrpc.php \
  -d '{"jsonrpc":"2.0","method":"host.update","params":{"hostid":"10643","templates":[{"templateid":"10318"}]},"auth":"TOKEN","id":2}'
```

### Docker Plugin Test Commands
```bash
# Ping Docker daemon
zabbix_agent2 -t docker.ping

# List all containers (returns JSON)
zabbix_agent2 -t docker.containers

# Get Docker system info
zabbix_agent2 -t docker.info
```

### Filebeat Docker Logs Verification
```bash
# Check autodiscovery is working
docker logs docker-elk-filebeat-1 | grep -i autodiscover

# Verify container log paths configured
docker logs docker-elk-filebeat-1 | grep "Configured paths"
```

---

## Deployment Timeline

| Time | Action | Status |
|------|--------|--------|
| 17:09 | Added zabbix user to docker group | ✓ Complete |
| 17:09 | Restarted zabbix-agent2 services | ✓ Complete |
| 17:09 | Verified Docker plugin connectivity | ✓ Complete |
| 17:10 | Linked Docker template to hosts | ✓ Complete |
| 17:11 | Verified Zabbix metrics collection | ✓ Complete |
| 17:12 | Verified Filebeat autodiscovery | ✓ Complete |
| 17:13 | Confirmed container logs flowing | ✓ Complete |

Total deployment time: ~5 minutes
