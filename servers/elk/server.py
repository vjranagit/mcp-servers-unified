#!/usr/bin/env python3
"""
ELK (Elasticsearch-Logstash-Kibana) MCP Server
Version: 1.0.0

Provides MCP interface for ELK Stack (Elasticsearch primarily)
"""

import sys
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

# Add template directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "template"))

from base_server import BaseMCPServer, create_json_schema
import requests
from requests.auth import HTTPBasicAuth

__version__ = "1.0.0"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ELKMCPServer(BaseMCPServer):
    """MCP Server for ELK Stack (Elasticsearch)"""

    def __init__(self):
        super().__init__("elk")

        # Configuration
        self.config_dir = Path.home() / ".elk-mcp"
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "config.json"

        # Elasticsearch connection
        self.es_url = None
        self.username = None
        self.password = None

        # Load configuration
        self.load_configuration()

        # Setup tools
        self.setup_tools()

    def load_configuration(self):
        """Load ELK configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.es_url = config.get("elasticsearch_url", "http://localhost:9200")
                self.username = config.get("username", "elastic")
                self.password=REDACTED_PASSWORDpassword", "")
        else:
            # Default configuration
            self.es_url = "http://localhost:9200"
            self.username = "elastic"
            self.password = ""
            self.save_configuration()

    def save_configuration(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump({
                "elasticsearch_url": self.es_url,
                "username": self.username,
                "password": self.password
            }, f, indent=2)

    def setup_tools(self):
        """Register ELK tools"""

        # Configuration
        self.register_tool(
            name="configure_elk",
            description="Configure Elasticsearch connection",
            handler=self.configure_elk,
            schema=create_json_schema(
                properties={
                    "elasticsearch_url": {
                        "type": "string",
                        "description": "Elasticsearch URL (e.g., http://localhost:9200)"
                    },
                    "username": {
                        "type": "string",
                        "description": "Elasticsearch username"
                    },
                    "password": {
                        "type": "string",
                        "description": "Elasticsearch password"
                    }
                },
                required=["elasticsearch_url", "username", "password"]
            )
        )

        # Cluster operations
        self.register_tool(
            name="get_cluster_health",
            description="Get Elasticsearch cluster health",
            handler=self.get_cluster_health,
            schema=create_json_schema(properties={}, required=[])
        )

        self.register_tool(
            name="get_cluster_stats",
            description="Get cluster statistics",
            handler=self.get_cluster_stats,
            schema=create_json_schema(properties={}, required=[])
        )

        # Index operations
        self.register_tool(
            name="list_indices",
            description="List all Elasticsearch indices",
            handler=self.list_indices,
            schema=create_json_schema(
                properties={
                    "pattern": {
                        "type": "string",
                        "description": "Index pattern (e.g., 'logs-*')"
                    }
                },
                required=[]
            )
        )

        self.register_tool(
            name="get_index_info",
            description="Get detailed information about an index",
            handler=self.get_index_info,
            schema=create_json_schema(
                properties={
                    "index": {
                        "type": "string",
                        "description": "Index name"
                    }
                },
                required=["index"]
            )
        )

        # Search operations
        self.register_tool(
            name="search_logs",
            description="Search logs in Elasticsearch",
            handler=self.search_logs,
            schema=create_json_schema(
                properties={
                    "index": {
                        "type": "string",
                        "description": "Index name or pattern (e.g., 'logs-*')"
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query string"
                    },
                    "from_time": {
                        "type": "string",
                        "description": "Start time (e.g., '2024-01-01T00:00:00')"
                    },
                    "to_time": {
                        "type": "string",
                        "description": "End time (e.g., '2024-01-02T00:00:00')"
                    },
                    "size": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 10
                    },
                    "sort_field": {
                        "type": "string",
                        "description": "Field to sort by",
                        "default": "@timestamp"
                    }
                },
                required=["index"]
            )
        )

        self.register_tool(
            name="aggregated_search",
            description="Perform aggregated search for analytics",
            handler=self.aggregated_search,
            schema=create_json_schema(
                properties={
                    "index": {
                        "type": "string",
                        "description": "Index name or pattern"
                    },
                    "field": {
                        "type": "string",
                        "description": "Field to aggregate on"
                    },
                    "agg_type": {
                        "type": "string",
                        "description": "Aggregation type (terms, date_histogram, avg, sum, etc.)",
                        "default": "terms"
                    },
                    "size": {
                        "type": "integer",
                        "description": "Number of buckets",
                        "default": 10
                    }
                },
                required=["index", "field"]
            )
        )

        # Document operations
        self.register_tool(
            name="get_document",
            description="Get a specific document by ID",
            handler=self.get_document,
            schema=create_json_schema(
                properties={
                    "index": {
                        "type": "string",
                        "description": "Index name"
                    },
                    "doc_id": {
                        "type": "string",
                        "description": "Document ID"
                    }
                },
                required=["index", "doc_id"]
            )
        )

        # Data analysis
        self.register_tool(
            name="analyze_errors",
            description="Analyze error patterns in logs",
            handler=self.analyze_errors,
            schema=create_json_schema(
                properties={
                    "index": {
                        "type": "string",
                        "description": "Index name or pattern"
                    },
                    "time_range": {
                        "type": "string",
                        "description": "Time range (e.g., '1h', '24h', '7d')",
                        "default": "24h"
                    }
                },
                required=["index"]
            )
        )

        self.register_tool(
            name="get_log_stats",
            description="Get statistics for log entries",
            handler=self.get_log_stats,
            schema=create_json_schema(
                properties={
                    "index": {
                        "type": "string",
                        "description": "Index name or pattern"
                    },
                    "time_range": {
                        "type": "string",
                        "description": "Time range (e.g., '1h', '24h', '7d')",
                        "default": "24h"
                    }
                },
                required=["index"]
            )
        )

    def es_request(self, method: str, endpoint: str, data: Optional[dict] = None) -> dict:
        """Make Elasticsearch REST API request

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request body (for POST/PUT)

        Returns:
            Response dict
        """
        if not self.es_url:
            return self.format_error("Elasticsearch URL not configured")

        url = f"{self.es_url.rstrip('/')}/{endpoint.lstrip('/')}"
        auth = HTTPBasicAuth(self.username, self.password) if self.username else None

        try:
            if method.upper() == "GET":
                response = requests.get(url, auth=auth, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, auth=auth, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, auth=auth, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, auth=auth, timeout=30)
            else:
                return self.format_error(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            return self.format_error(f"Request failed: {str(e)}")
        except Exception as e:
            return self.format_error(f"Unexpected error: {str(e)}")

    def configure_elk(self, args: dict) -> dict:
        """Configure Elasticsearch connection"""
        self.es_url = args.get("elasticsearch_url")
        self.username = args.get("username")
        self.password=REDACTED_PASSWORDpassword")
        self.save_configuration()

        # Test connection
        result = self.es_request("GET", "/")
        if "status" in result and result["status"] == "error":
            return result

        return self.format_success(
            "Successfully configured Elasticsearch connection",
            {"config_saved": str(self.config_file)}
        )

    def get_cluster_health(self, args: dict) -> dict:
        """Get cluster health"""
        result = self.es_request("GET", "/_cluster/health")

        if "status" in result and result["status"] != "error":
            return self.format_success(
                f"Cluster status: {result.get('status', 'unknown')}",
                {"health": result}
            )

        return result

    def get_cluster_stats(self, args: dict) -> dict:
        """Get cluster statistics"""
        result = self.es_request("GET", "/_cluster/stats")

        if "status" not in result or result["status"] != "error":
            return self.format_success("Retrieved cluster statistics", {"stats": result})

        return result

    def list_indices(self, args: dict) -> dict:
        """List indices"""
        pattern = args.get("pattern", "*")
        result = self.es_request("GET", f"/_cat/indices/{pattern}?format=json&s=index")

        if isinstance(result, list):
            return self.format_success(
                f"Found {len(result)} indices",
                {
                    "count": len(result),
                    "indices": result
                }
            )

        return result

    def get_index_info(self, args: dict) -> dict:
        """Get index information"""
        index = args.get("index")
        result = self.es_request("GET", f"/{index}")

        if "status" not in result or result["status"] != "error":
            return self.format_success(f"Index info for {index}", {"info": result})

        return result

    def search_logs(self, args: dict) -> dict:
        """Search logs"""
        index = args.get("index")
        query_string = args.get("query", "*")
        size = args.get("size", 10)
        sort_field = args.get("sort_field", "@timestamp")

        # Build Elasticsearch query
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"query_string": {"query": query_string}}
                    ]
                }
            },
            "size": size,
            "sort": [{sort_field: {"order": "desc"}}]
        }

        # Add time range if provided
        if args.get("from_time") or args.get("to_time"):
            time_range = {}
            if args.get("from_time"):
                time_range["gte"] = args["from_time"]
            if args.get("to_time"):
                time_range["lte"] = args["to_time"]

            query["query"]["bool"]["must"].append({
                "range": {
                    "@timestamp": time_range
                }
            })

        result = self.es_request("POST", f"/{index}/_search", query)

        if "hits" in result:
            hits = result["hits"]["hits"]
            return self.format_success(
                f"Found {result['hits']['total']['value']} results (showing {len(hits)})",
                {
                    "total": result["hits"]["total"]["value"],
                    "count": len(hits),
                    "results": hits
                }
            )

        return result

    def aggregated_search(self, args: dict) -> dict:
        """Perform aggregated search"""
        index = args.get("index")
        field = args.get("field")
        agg_type = args.get("agg_type", "terms")
        size = args.get("size", 10)

        # Build aggregation query
        agg_body = {}
        if agg_type == "terms":
            agg_body = {
                "terms": {
                    "field": field,
                    "size": size
                }
            }
        elif agg_type == "date_histogram":
            agg_body = {
                "date_histogram": {
                    "field": field,
                    "calendar_interval": "1h"
                }
            }

        query = {
            "size": 0,
            "aggs": {
                "aggregation": agg_body
            }
        }

        result = self.es_request("POST", f"/{index}/_search", query)

        if "aggregations" in result:
            return self.format_success(
                f"Aggregation results for {field}",
                {"aggregations": result["aggregations"]}
            )

        return result

    def get_document(self, args: dict) -> dict:
        """Get document by ID"""
        index = args.get("index")
        doc_id = args.get("doc_id")

        result = self.es_request("GET", f"/{index}/_doc/{doc_id}")

        if "found" in result and result["found"]:
            return self.format_success(
                f"Found document {doc_id}",
                {"document": result}
            )
        elif "found" in result and not result["found"]:
            return self.format_error(f"Document not found: {doc_id}")

        return result

    def analyze_errors(self, args: dict) -> dict:
        """Analyze error patterns"""
        index = args.get("index")
        time_range = args.get("time_range", "24h")

        # Convert time range to timestamp
        now = datetime.utcnow()
        if time_range.endswith('h'):
            hours = int(time_range[:-1])
            from_time = now - timedelta(hours=hours)
        elif time_range.endswith('d'):
