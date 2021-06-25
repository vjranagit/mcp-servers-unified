# ELK MCP Server

MCP Server for ELK Stack (Elasticsearch-Logstash-Kibana) - Search logs, analyze data, and monitor your infrastructure through Claude.

## Features

- **Cluster Management**: Monitor cluster health and statistics
- **Index Operations**: List and manage Elasticsearch indices
- **Log Search**: Powerful log search with time ranges and filters
- **Analytics**: Aggregated searches for data analysis
- **Error Analysis**: Identify and analyze error patterns
- **Document Operations**: Get specific documents by ID
- **Statistics**: Log level distribution and timeline analysis

## Installation

```bash
cd elk
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

### Elasticsearch Setup

The server will create configuration files in `~/.elk-mcp/`:

```
~/.elk-mcp/
└── config.json       # Elasticsearch connection config
```

### Initial Configuration

Create `~/.elk-mcp/config.json` or use the `configure_elk` tool:

```json
{
  "elasticsearch_url": "http://localhost:9200",
  "username": "elastic",
  "password": "your-password"
}
```

### MCP Configuration

Add to your MCP settings file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "elk": {
      "command": "python",
      "args": [
        "/absolute/path/to/mcp-servers/elk/server.py"
      ]
    }
  }
}
```

## Available Tools

### configure_elk

Configure Elasticsearch connection settings.

**Parameters:**
- `elasticsearch_url` (string, required): Elasticsearch URL (e.g., http://localhost:9200)
- `username` (string, required): Elasticsearch username
- `password` (string, required): Elasticsearch password

**Example:**
```json
{
  "elasticsearch_url": "http://localhost:9200",
  "username": "elastic",
  "password": "changeme"
}
```

### get_cluster_health

Get Elasticsearch cluster health status.

**Parameters:** None

**Response:**
```json
{
  "status": "success",
  "message": "Cluster status: green",
  "health": {
    "cluster_name": "docker-cluster",
    "status": "green",
    "number_of_nodes": 1,
    "active_primary_shards": 5,
    "active_shards": 5,
    "relocating_shards": 0,
    "initializing_shards": 0,
    "unassigned_shards": 0
  }
}
```

### get_cluster_stats

Get detailed cluster statistics.

**Parameters:** None

**Response:** Returns comprehensive cluster statistics including nodes, indices, and storage.

### list_indices

List all Elasticsearch indices with optional pattern filtering.

**Parameters:**
- `pattern` (string, optional): Index pattern (e.g., 'logs-*', default: '*')

**Example:**
```json
{
  "pattern": "logs-*"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Found 5 indices",
  "count": 5,
  "indices": [
    {
      "index": "logs-2024.01.09",
      "health": "green",
      "status": "open",
      "pri": "1",
      "rep": "0",
      "docs.count": "12345",
      "store.size": "5.2mb"
    }
  ]
}
```

### get_index_info

Get detailed information about a specific index.

**Parameters:**
- `index` (string, required): Index name

**Example:**
```json
{
  "index": "logs-2024.01.09"
}
```

### search_logs

Search logs with advanced filtering and time ranges.

**Parameters:**
- `index` (string, required): Index name or pattern (e.g., 'logs-*')
- `query` (string, optional): Search query string (default: '*')
- `from_time` (string, optional): Start time (ISO format: '2024-01-01T00:00:00')
- `to_time` (string, optional): End time (ISO format: '2024-01-02T00:00:00')
- `size` (integer, optional): Number of results (default: 10)
- `sort_field` (string, optional): Sort field (default: '@timestamp')

**Example:**
```json
{
  "index": "logs-*",
  "query": "error AND service:api",
  "from_time": "2024-01-09T00:00:00",
  "to_time": "2024-01-09T12:00:00",
  "size": 50
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Found 1234 results (showing 50)",
  "total": 1234,
  "count": 50,
  "results": [
    {
      "_index": "logs-2024.01.09",
      "_id": "abc123",
      "_source": {
        "@timestamp": "2024-01-09T10:30:00Z",
        "level": "error",
        "message": "Connection timeout",
        "service": "api"
      }
    }
  ]
}
```

### aggregated_search

Perform aggregated searches for analytics.

**Parameters:**
- `index` (string, required): Index name or pattern
- `field` (string, required): Field to aggregate on
- `agg_type` (string, optional): Aggregation type ('terms', 'date_histogram', etc., default: 'terms')
- `size` (integer, optional): Number of buckets (default: 10)

**Example - Top error messages:**
```json
{
  "index": "logs-*",
  "field": "message.keyword",
  "agg_type": "terms",
  "size": 10
}
```

**Example - Errors over time:**
```json
{
  "index": "logs-*",
  "field": "@timestamp",
  "agg_type": "date_histogram"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Aggregation results for message.keyword",
  "aggregations": {
    "aggregation": {
      "buckets": [
        {
          "key": "Connection timeout",
          "doc_count": 456
        },
        {
          "key": "Database error",
          "doc_count": 234
        }
      ]
    }
  }
}
```

### get_document

Get a specific document by ID.

**Parameters:**
- `index` (string, required): Index name
- `doc_id` (string, required): Document ID

**Example:**
```json
{
  "index": "logs-2024.01.09",
  "doc_id": "abc123"
}
```

### analyze_errors

Analyze error patterns in logs over a time range.

**Parameters:**
- `index` (string, required): Index name or pattern
- `time_range` (string, optional): Time range ('1h', '24h', '7d', default: '24h')

**Example:**
```json
{
  "index": "logs-*",
  "time_range": "24h"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Error analysis for last 24h",
  "total_errors": 1234,
  "analysis": {
    "error_types": {
      "buckets": [
        {"key": "Connection timeout", "doc_count": 456},
        {"key": "Database error", "doc_count": 234}
      ]
    },
    "error_timeline": {
      "buckets": [
        {"key_as_string": "2024-01-09T00:00:00", "doc_count": 45},
        {"key_as_string": "2024-01-09T01:00:00", "doc_count": 67}
      ]
    }
  }
}
```

### get_log_stats

Get statistics for log entries including level distribution and timeline.

**Parameters:**
- `index` (string, required): Index name or pattern
- `time_range` (string, optional): Time range ('1h', '24h', '7d', default: '24h')

**Example:**
```json
{
  "index": "logs-*",
  "time_range": "24h"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Log statistics for logs-*",
  "total_logs": 12345,
  "statistics": {
    "log_levels": {
      "buckets": [
        {"key": "info", "doc_count": 8000},
        {"key": "warning", "doc_count": 3000},
        {"key": "error", "doc_count": 1234},
        {"key": "debug", "doc_count": 111}
      ]
    },
    "timeline": {
      "buckets": [...]
    }
  }
}
```

## Usage Examples

### Typical Workflow

1. **Check Cluster Health:**
```
Use get_cluster_health to verify cluster is healthy
```

2. **List Available Indices:**
```
Use list_indices to see what data is available
```

3. **Search for Issues:**
```
Use search_logs to find specific errors or events
Use analyze_errors to see error patterns
```

4. **Analyze Trends:**
```
Use aggregated_search to see trends over time
Use get_log_stats to understand log distribution
```

### Common Search Patterns

**Find errors in last hour:**
```json
{
  "index": "logs-*",
  "query": "level:error",
  "from_time": "2024-01-09T11:00:00",
  "to_time": "2024-01-09T12:00:00"
}
```

**Find application-specific logs:**
```json
{
  "index": "logs-*",
  "query": "service:api AND (error OR warning)"
}
```

**Top error messages:**
```json
{
  "index": "logs-*",
  "field": "message.keyword",
  "agg_type": "terms",
  "size": 20
}
```

## Development

### Project Structure

```
elk/
├── server.py           # Main MCP server implementation
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

### Extending the Server

