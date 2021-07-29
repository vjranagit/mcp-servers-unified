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
