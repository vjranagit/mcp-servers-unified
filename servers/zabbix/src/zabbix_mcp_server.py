#!/usr/bin/env python3
"""
Zabbix MCP Server - Complete integration with Zabbix API using python-zabbix-utils

This server provides comprehensive access to Zabbix API functionality through
the Model Context Protocol (MCP), enabling AI assistants and other tools to
interact with Zabbix monitoring systems.

Author: Zabbix MCP Server Contributors
License: MIT
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional
from fastmcp import FastMCP
from zabbix_utils import ZabbixAPI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO if os.getenv("DEBUG") else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastMCP
mcp = FastMCP("Zabbix MCP Server")

# Global Zabbix API client
zabbix_api: Optional[ZabbixAPI] = None


def get_zabbix_client() -> ZabbixAPI:
    """Get or create Zabbix API client with proper authentication.
    
    Returns:
        ZabbixAPI: Authenticated Zabbix API client
        
    Raises:
        ValueError: If required environment variables are missing
        Exception: If authentication fails
    """
    global zabbix_api
    
    if zabbix_api is None:
        url = os.getenv("ZABBIX_URL")
        if not url:
            raise ValueError("ZABBIX_URL environment variable is required")
        
        logger.info(f"Initializing Zabbix API client for {url}")
        
        # Initialize client
        zabbix_api = ZabbixAPI(url=url)
        
        # Authenticate using token or username/password
        token = os.getenv("ZABBIX_TOKEN")
        if token:
            logger.info("Authenticating with API token")
            zabbix_api.login(token=token)
        else:
            user = os.getenv("ZABBIX_USER")
            password=REDACTED_PASSWORDZABBIX_PASSWORD")
            if not user or not password:
                raise ValueError("Either ZABBIX_TOKEN or ZABBIX_USER/ZABBIX_PASSWORD must be set")
            logger.info(f"Authenticating with username: {user}")
            zabbix_api.login(user=user, password=REDACTED_PASSWORD
        
        logger.info("Successfully authenticated with Zabbix API")
    
    return zabbix_api


def is_read_only() -> bool:
    """Check if server is in read-only mode.
    
    Returns:
        bool: True if read-only mode is enabled
    """
    return os.getenv("READ_ONLY", "true").lower() in ("true", "1", "yes")


def format_response(data: Any) -> str:
    """Format response data as JSON string.
    
    Args:
        data: Data to format
        
    Returns:
        str: JSON formatted string
    """
    return json.dumps(data, indent=2, default=str)


def validate_read_only() -> None:
    """Validate that write operations are allowed.
    
    Raises:
        ValueError: If server is in read-only mode
    """
    if is_read_only():
        raise ValueError("Server is in read-only mode - write operations are not allowed")


# HOST MANAGEMENT
@mcp.tool()
def host_get(hostids: Optional[List[str]] = None, 
             groupids: Optional[List[str]] = None,
             templateids: Optional[List[str]] = None,
             output: str = "extend",
             search: Optional[Dict[str, str]] = None,
             filter: Optional[Dict[str, Any]] = None,
             limit: Optional[int] = None) -> str:
    """Get hosts from Zabbix with optional filtering.
    
    Args:
        hostids: List of host IDs to retrieve
        groupids: List of host group IDs to filter by
        templateids: List of template IDs to filter by
        output: Output format (extend, shorten, or specific fields)
        search: Search criteria
        filter: Filter criteria
        limit: Maximum number of results
        
    Returns:
        str: JSON formatted list of hosts
    """
    client = get_zabbix_client()
    params = {"output": output}
    
    if hostids:
        params["hostids"] = hostids
    if groupids:
        params["groupids"] = groupids
    if templateids:
        params["templateids"] = templateids
    if search:
        params["search"] = search
    if filter:
        params["filter"] = filter
    if limit:
        params["limit"] = limit
    
    result = client.host.get(**params)
    return format_response(result)


@mcp.tool()
def host_create(host: str, groups: List[Dict[str, str]], 
                interfaces: List[Dict[str, Any]],
                templates: Optional[List[Dict[str, str]]] = None,
                inventory_mode: int = -1,
                status: int = 0) -> str:
    """Create a new host in Zabbix.
    
    Args:
        host: Host name
        groups: List of host groups (format: [{"groupid": "1"}])
        interfaces: List of host interfaces
        templates: List of templates to link (format: [{"templateid": "1"}])
        inventory_mode: Inventory mode (-1=disabled, 0=manual, 1=automatic)
        status: Host status (0=enabled, 1=disabled)
        
    Returns:
        str: JSON formatted creation result
    """
    validate_read_only()
    
    client = get_zabbix_client()
    params = {
        "host": host,
        "groups": groups,
        "interfaces": interfaces,
        "inventory_mode": inventory_mode,
        "status": status
    }
    
    if templates:
        params["templates"] = templates
    
    result = client.host.create(**params)
    return format_response(result)


@mcp.tool()
def host_update(hostid: str, host: Optional[str] = None, 
                name: Optional[str] = None, status: Optional[int] = None) -> str:
    """Update an existing host in Zabbix.
    
    Args:
        hostid: Host ID to update
        host: New host name
        name: New visible name
        status: New status (0=enabled, 1=disabled)
        
    Returns:
        str: JSON formatted update result
    """
    validate_read_only()
    
    client = get_zabbix_client()
    params = {"hostid": hostid}
    
    if host:
        params["host"] = host
    if name:
        params["name"] = name
    if status is not None:
        params["status"] = status
    
    result = client.host.update(**params)
    return format_response(result)


@mcp.tool()
def host_delete(hostids: List[str]) -> str:
    """Delete hosts from Zabbix.
    
    Args:
        hostids: List of host IDs to delete
        
    Returns:
        str: JSON formatted deletion result
    """
    validate_read_only()
    
    client = get_zabbix_client()
    result = client.host.delete(*hostids)
    return format_response(result)


# HOST GROUP MANAGEMENT
@mcp.tool()
def hostgroup_get(groupids: Optional[List[str]] = None,
                  output: str = "extend",
                  search: Optional[Dict[str, str]] = None,
                  filter: Optional[Dict[str, Any]] = None) -> str:
    """Get host groups from Zabbix.
    
    Args:
        groupids: List of group IDs to retrieve
        output: Output format
        search: Search criteria
        filter: Filter criteria
        
    Returns:
        str: JSON formatted list of host groups
    """
    client = get_zabbix_client()
    params = {"output": output}
    
    if groupids:
        params["groupids"] = groupids
    if search:
        params["search"] = search
    if filter:
        params["filter"] = filter
    
    result = client.hostgroup.get(**params)
    return format_response(result)


@mcp.tool()
def hostgroup_create(name: str) -> str:
    """Create a new host group in Zabbix.
    
    Args:
        name: Host group name
        
    Returns:
        str: JSON formatted creation result
    """
    validate_read_only()
    
    client = get_zabbix_client()
    result = client.hostgroup.create(name=name)
    return format_response(result)


@mcp.tool()
def hostgroup_update(groupid: str, name: str) -> str:
    """Update an existing host group in Zabbix.
    
    Args:
        groupid: Group ID to update
        name: New group name
        
    Returns:
        str: JSON formatted update result
    """
    validate_read_only()
    
    client = get_zabbix_client()
    result = client.hostgroup.update(groupid=groupid, name=name)
