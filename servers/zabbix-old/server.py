#!/usr/bin/env python3
"""
Zabbix MCP Server - Wrapper for zabbix-cli
Version: 2.1.0

Provides MCP interface for Zabbix using zabbix-cli tool as backend

Changelog:
- v2.1.0: Fix stderr warning handling and timeout issues
- v2.0.0: Initial wrapper implementation
"""

import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

# Add template directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "template"))

from base_server import BaseMCPServer, create_json_schema

__version__ = "2.1.0"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZabbixMCPServer(BaseMCPServer):
    """MCP Server for Zabbix using zabbix-cli tool"""

    def __init__(self):
        super().__init__("zabbix")

        # Configuration
        self.zabbix_cli_path = "/usr/local/bin/zabbix-cli"

        # Setup tools
        self.setup_tools()

    def execute_cli_command(self, command: str, output_format: str = "json", timeout: int = 60) -> Dict[str, Any]:
        """Execute zabbix-cli command and return parsed output"""
        try:
            # Build command
            cmd = [self.zabbix_cli_path, "-o", output_format, "-C", command]

            # Execute command with stdin redirected to prevent interactive prompts
            logger.info(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,  # Prevent interactive prompts
                timeout=timeout
            )

            # Check for errors - only fail on non-zero return code
            # Ignore stderr warnings if command succeeded (returncode == 0)
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Command failed"
                logger.error(f"Command failed with return code {result.returncode}: {error_msg}")
                return self.format_error(f"Command failed: {error_msg}")

            # Log stderr warnings but don't fail
            if result.stderr:
                logger.warning(f"Command succeeded with warnings: {result.stderr.strip()}")

            # Parse output
            output = result.stdout.strip()

            # Try to parse as JSON
            if output_format == "json" and output:
                try:
                    data = json.loads(output)
                    return self.format_success("Command executed successfully", {"data": data})
                except json.JSONDecodeError:
                    # Return as text if not valid JSON
                    return self.format_success("Command executed successfully", {"output": output})
            else:
                return self.format_success("Command executed successfully", {"output": output})

        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout} seconds")
            return self.format_error(f"Command timed out after {timeout} seconds")
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return self.format_error(f"Error executing command: {str(e)}")

    def setup_tools(self):
        """Register Zabbix tools wrapping zabbix-cli commands"""

        # Host management
        self.register_tool(
            name="show_hosts",
            description="Show all monitored hosts",
            handler=self.show_hosts,
            schema=create_json_schema(
                properties={
                    "filter": {
                        "type": "string",
                        "description": "Optional filter pattern for host names"
                    }
                },
                required=[]
            )
        )

        self.register_tool(
            name="show_host",
            description="Show detailed information about a specific host",
            handler=self.show_host,
            schema=create_json_schema(
                properties={
                    "hostname": {
                        "type": "string",
                        "description": "Hostname to show details for"
                    }
                },
                required=["hostname"]
            )
        )

        self.register_tool(
            name="create_host",
            description="Create a new monitored host",
            handler=self.create_host,
            schema=create_json_schema(
                properties={
                    "hostname": {
                        "type": "string",
                        "description": "Hostname to create"
                    },
                    "hostgroups": {
                        "type": "string",
                        "description": "Comma-separated list of hostgroups"
                    },
                    "proxy": {
                        "type": "string",
                        "description": "Proxy name (optional)"
                    },
                    "ip": {
                        "type": "string",
                        "description": "IP address"
                    }
                },
                required=["hostname", "hostgroups", "ip"]
            )
        )

        self.register_tool(
            name="remove_host",
            description="Remove a monitored host",
            handler=self.remove_host,
            schema=create_json_schema(
                properties={
                    "hostname": {
                        "type": "string",
                        "description": "Hostname to remove"
                    }
                },
                required=["hostname"]
            )
        )

        # Host groups
        self.register_tool(
            name="show_hostgroups",
            description="Show all host groups",
            handler=self.show_hostgroups,
            schema=create_json_schema(properties={}, required=[])
        )

        self.register_tool(
            name="show_hostgroup",
            description="Show hosts in a specific hostgroup",
            handler=self.show_hostgroup,
            schema=create_json_schema(
                properties={
                    "hostgroup": {
                        "type": "string",
                        "description": "Hostgroup name"
                    }
                },
                required=["hostgroup"]
            )
        )

        self.register_tool(
            name="create_hostgroup",
            description="Create a new hostgroup",
            handler=self.create_hostgroup,
            schema=create_json_schema(
                properties={
                    "name": {
                        "type": "string",
                        "description": "Hostgroup name to create"
                    }
                },
                required=["name"]
            )
        )

        # Templates
        self.register_tool(
            name="show_templates",
            description="Show all templates",
            handler=self.show_templates,
            schema=create_json_schema(
                properties={
                    "filter": {
                        "type": "string",
                        "description": "Optional filter pattern for template names"
                    }
                },
                required=[]
            )
        )

        self.register_tool(
            name="show_template",
            description="Show detailed information about a template",
            handler=self.show_template,
            schema=create_json_schema(
                properties={
                    "template": {
                        "type": "string",
                        "description": "Template name"
                    }
                },
                required=["template"]
            )
        )

        self.register_tool(
            name="link_template_to_host",
            description="Link a template to a host",
            handler=self.link_template_to_host,
            schema=create_json_schema(
                properties={
                    "template": {
                        "type": "string",
