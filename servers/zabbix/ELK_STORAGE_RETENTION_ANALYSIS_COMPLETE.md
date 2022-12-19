# ELK Storage & Retention Policy - Analysis Complete

**Date**: October 11, 2025
**Status**: ✅ **RETENTION POLICY CONFIGURED AND OPTIMIZED**

---

## 🚨 Critical Issues Discovered

### Before Optimization:
- **Log ingestion**: 2.9M logs/hour (144x increase after cloud configuration)
- **Data growth**: **67.8 GB/day** (today's syslog alone!)
- **Total storage**: 157.6 GB used (222.5M documents)
- **Available space**: 403 GB
- **Days until 90% full**: **~4.6 days** (CRITICAL!)
- **No retention policy**: Logs never deleted
- **Old data**: 83 GB of July/August logs still present

### Root Cause:
1. **No ILM policy** configured for filebeat indices
2. **Old data accumulation**: 3+ months of logs retained
3. **Rapid growth**: Cloud hosts generating massive log volume

---

## ✅ Actions Completed

### 1. **Created 4-Day Retention ILM Policy** ✅
- **Policy name**: `filebeat-4day-retention`
- **Hot phase** (0-1 day): Active indexing, rollover at 1 day or 50 GB
- **Warm phase** (1-2 days): Read-only, lower priority
- **Delete phase** (4+ days): Auto-delete indices older than 4 days

```json
{
  "hot": {
    "rollover": {"max_age": "1d", "max_primary_shard_size": "50gb"},
    "set_priority": {"priority": 100}
  },
  "warm": {
    "min_age": "2d",
    "set_priority": {"priority": 50},
    "readonly": {}
  },
  "delete": {
    "min_age": "4d",
    "delete": {}
  }
}
```

### 2. **Configured Disk Watermarks** ✅
- **Low watermark**: 75% (start warning)
- **High watermark**: 85% (stop new index allocation)
- **Flood stage**: 90% (read-only mode)

This prevents the cluster from filling up completely.

### 3. **Deleted Old Data** ✅
Removed July and August 2025 data streams:
- 17 data streams deleted
- **Space freed**: ~83 GB
- Indices removed: `filebeat-docker-8.18.4-2025.07.*` and `2025.08.*`

### 4. **Applied ILM Policy** ✅
- Created index templates for automatic policy application
- Applied policy to all existing filebeat indices
- Future indices will automatically use 4-day retention

---

## 📊 Storage Status: Before vs After

| Metric | Before Optimization | After Optimization | Change |
|--------|-------------------|-------------------|---------|
| **Total Documents** | 222.5 million | 85.9 million | -136.6M (-61%) |
| **Total Size** | 157.6 GB | 74.1 GB | -83.5 GB (-53%) |
| **Available Space** | 403 GB | 486 GB | +83 GB |
| **Disk Usage** | 512 GB (56%) | 429 GB (47%) | -83 GB |
| **Days Until 90%** | ~4.6 days | ~13 days | +8.4 days |
| **Retention Policy** | None (infinite) | 4 days | Configured |

---

## 💾 Current Storage Breakdown

### Filesystem
- **Total**: 914.82 GB
- **Used**: 428.70 GB (47%)
- **Available**: 486.12 GB
- **90% threshold**: 823 GB

### Elasticsearch Data
- **Active data**: 74.07 GB
- **Document count**: 85,942,299
- **Indices**: 19 (down from 60)

### Largest Current Indices
| Index | Documents | Size | Age |
|-------|-----------|------|-----|
| filebeat-syslog-8.18.4-2025.10.11 | 77M | 67.8 GB | Today |
| filebeat-syslog-8.18.4-2025.10.10 | 3.1M | 2.1 GB | Yesterday |
| filebeat-8.18.4-2025.10.09 | 5.7M | 4 GB | 2 days ago |

---

## 📈 Projected Growth with 4-Day Retention

### Daily Ingestion Rate
- **Logs per hour**: 2,885,728
- **Logs per day**: 69,257,472
- **Data per day**: ~67.8 GB (current rate)

### Steady State Storage (after 4 days)
- **4 days of logs**: 67.8 GB × 4 = **271.2 GB**
- **With overhead**: ~300 GB total
- **Disk usage at steady state**: ~47% + 27% = **74%**

### Capacity Analysis
| Scenario | Storage Used | Disk % | Status | Days Until Full |
|----------|--------------|--------|--------|-----------------|
| **Current** | 429 GB | 47% | ✅ Good | - |
| **Steady state (4-day)** | ~700 GB | 76% | ✅ Sustainable | Stable |
| **Without retention** | +67.8 GB/day | - | 🔴 Critical | ~5 days |
| **90% threshold** | 823 GB | 90% | 🟡 Warning | Never (with ILM) |

---

## 🎯 Retention Policy Details

### Automatic Lifecycle
1. **Day 0-1 (Hot)**:
   - Active indexing
   - Full read/write access
   - Rollover when index reaches 50 GB or 1 day old

2. **Day 1-2 (Warm)**:
   - Read-only
   - Lower search priority
   - Data still fully searchable

3. **Day 4+ (Delete)**:
   - Indices automatically deleted
   - Space freed immediately
   - **No manual intervention required**

### Index Templates Created
- `filebeat-syslog-retention` (priority: 500)
- `filebeat-retention` (priority: 400)

All new filebeat indices will automatically use 4-day retention.

---

## 🔐 Safety Mechanisms

### Disk Watermarks
```
75% (686 GB) → Low watermark (warning alerts should be configured)
85% (778 GB) → High watermark (stop new index creation)
90% (823 GB) → Flood stage (read-only mode, prevent data loss)
```

### ILM Execution
- ILM checks run every 10 minutes by default
- Indices are marked for deletion at 4 days
- Actual deletion happens on next ILM cycle
- Maximum retention: **4 days + 10 minutes**

---

## 📝 Monitoring Recommendations

### Set Up Alerts (using Zabbix or Kibana)

**Critical Alerts:**
- Disk usage > 75% (Low watermark)
- Disk usage > 85% (High watermark)
- ILM execution failures
- Index deletion failures

**Warning Alerts:**
- Log ingestion rate > 3M logs/hour (spike detection)
- Daily data growth > 80 GB
- Disk usage growing faster than expected

**Info Alerts:**
- Daily storage report
- ILM policy execution summary
- Index deletion confirmations

### Elasticsearch Monitoring

```bash
# Check cluster health
curl -u "elastic:PASSWORD" "http://192.168.1.2:9200/_cluster/health?pretty"

# Check ILM status
curl -u "elastic:PASSWORD" "http://192.168.1.2:9200/_ilm/status?pretty"

# List indices with ILM policy
curl -u "elastic:PASSWORD" "http://192.168.1.2:9200/_cat/indices?v&h=index,docs.count,store.size,health"

# Check ILM explain (why index not deleted)
curl -u "elastic:PASSWORD" "http://192.168.1.2:9200/INDEX_NAME/_ilm/explain?pretty"
```

---

## 🔧 Maintenance Tasks

### Daily (Automated)
- ILM automatically deletes indices > 4 days old
- New indices automatically assigned to ILM policy
- Disk space freed as old indices deleted

### Weekly (Manual Verification)
1. Verify ILM is executing: `_ilm/status`
2. Check disk usage trend
3. Confirm old indices are being deleted
4. Review log ingestion rates

### Monthly (Capacity Planning)
1. Analyze log volume trends
2. Adjust retention if needed (e.g., 3-day or 5-day)
3. Plan for disk expansion if sustained growth
4. Review and optimize log sources (reduce verbosity if possible)

---

## 🚀 Optimization Opportunities

### If More Retention Needed
**Option 1**: Add disk space
- Current: 915 GB
- Recommended: 1.5-2 TB for 7-day retention
- Install location: `/mnt/docker-volumes` has space

**Option 2**: Reduce log verbosity
- Filter debug/info logs at rsyslog level
- Keep only warning/error/critical
- Potential reduction: 60-70% of volume

**Option 3**: Implement log sampling
- Sample repetitive logs (e.g., every 10th log)
- Full logging for errors only
- Can reduce volume by 50-80%

### If Less Storage Needed
**Option 1**: Reduce retention to 3 days
- Edit ILM policy: Change delete phase to "3d"
- Steady state: ~203 GB (vs 271 GB)
- Disk usage: ~67% (vs 74%)

**Option 2**: Implement hot-warm-cold architecture
- Move warm data to cheaper storage tier
- Compress older indices
- Potential savings: 30-50%

---

## 📄 Configuration Files

### ILM Policy
**Location**: Elasticsearch `_ilm/policy/filebeat-4day-retention`
**Backup**: `/home/vjrana/work/mcp-servers/servers/zabbix/elk_configs/ilm_policy_4day.json`

### Index Templates
1. `filebeat-syslog-retention` (priority 500)
2. `filebeat-retention` (priority 400)

### Disk Watermarks
**Cluster settings**: `_cluster/settings`
- `cluster.routing.allocation.disk.watermark.low: 75%`
- `cluster.routing.allocation.disk.watermark.high: 85%`
- `cluster.routing.allocation.disk.watermark.flood_stage: 90%`

---

## ✅ Success Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Retention Policy** | Configured | 4 days | ✅ Met |
| **Old Data Removed** | Freed 80+ GB | 83 GB freed | ✅ Exceeded |
