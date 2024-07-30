# MCP Servers Collection

A collection of Model Context Protocol (MCP) servers for various services and platforms. This repository provides a reusable template framework for building MCP servers quickly and consistently.

## Repository Structure

```
mcp-servers/
├── README.md                  # This file
├── template/                  # Base template for new MCP servers
│   ├── base_server.py        # Base MCP server class
│   ├── base_auth.py          # Authentication patterns
│   ├── README_template.md    # Documentation template
│   └── requirements_template.txt
├── gmail/                     # Gmail MCP server
├── zabbix/                    # Zabbix monitoring MCP server
└── elk/                       # ELK Stack MCP server
```

## Available MCP Servers

### 1. Gmail MCP Server (v2.1)

Full-featured Gmail MCP server with 16 operations including email search, send, drafts, labels, and attachments.

**Features:**
- Email search with Gmail query syntax
- Send emails with HTML content
- Manage drafts (create, read, update, send, delete)
- Label management
- Attachment handling (list, download)
- Email operations (read, modify, delete, archive, star)

**Directory:** `gmail/`
**Documentation:** [Gmail README](gmail/README.md)

### 2. Zabbix MCP Server (v1.0)

Monitor and manage Zabbix infrastructure through MCP interface.

**Features:**
- Host management (list, get details)
- Monitoring items and history
- Trigger and problem tracking
- Host group management
- API authentication

**Directory:** `zabbix/`
**Documentation:** [Zabbix README](zabbix/README.md)

### 3. ELK MCP Server (v1.0)

Search and analyze logs in Elasticsearch through MCP interface.

**Features:**
- Cluster health and statistics
- Index management
- Log search with time ranges
- Aggregated analytics
- Error pattern analysis
- Document retrieval

**Directory:** `elk/`
**Documentation:** [ELK README](elk/README.md)

## Template Framework

The `template/` directory contains reusable base classes for building new MCP servers:

### Base Server (`base_server.py`)

Provides common MCP server functionality:

```python
from base_server import BaseMCPServer, create_json_schema

class MyMCPServer(BaseMCPServer):
    def __init__(self):
        super().__init__("my-service")
        self.setup_tools()

    def setup_tools(self):
        self.register_tool(
            name="my_operation",
            description="Perform operation",
            handler=self.my_operation,
            schema=create_json_schema(
                properties={
                    "param": {"type": "string", "description": "Parameter"}
                },
                required=["param"]
            )
        )

    def my_operation(self, args: dict) -> dict:
        return self.format_success("Operation completed")
```

**Key Features:**
- Automatic tool registration
- Standardized response formatting
- Error handling
- JSON schema helpers

### Authentication (`base_auth.py`)

Multiple authentication patterns:

- **OAuth2Handler**: OAuth 2.0 flow (like Gmail)
- **TokenAuthHandler**: Token-based auth (like Zabbix)
- **BasicAuthHandler**: Basic username/password auth (like ELK)

```python
from base_auth import create_auth_handler

# Create OAuth2 handler
auth = create_auth_handler(
    'oauth2',
    'gmail',
    scopes=['https://www.googleapis.com/auth/gmail.modify'],
    client_secrets_file='credentials.json'
)

# Create token auth handler
auth = create_auth_handler(
    'token',
    'zabbix',
    api_url='http://localhost/api_jsonrpc.php'
)
```

## Creating a New MCP Server

### 1. Create Directory Structure

```bash
mkdir -p mcp-servers/myservice
cd mcp-servers/myservice
```

### 2. Copy Template Files

```bash
cp ../template/README_template.md README.md
cp ../template/requirements_template.txt requirements.txt
```

### 3. Create Server Implementation

```python
#!/usr/bin/env python3
"""My Service MCP Server"""

import sys
from pathlib import Path

# Add template directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "template"))

from base_server import BaseMCPServer, create_json_schema

class MyServiceMCP(BaseMCPServer):
    def __init__(self):
        super().__init__("myservice")
        self.setup_authentication()
        self.setup_tools()

    def setup_authentication(self):
        # Initialize your API client
        pass

    def setup_tools(self):
        # Register your tools
        self.register_tool(
            name="my_operation",
            description="Perform operation",
            handler=self.my_operation,
            schema=create_json_schema(
                properties={"param": {"type": "string"}},
                required=["param"]
            )
        )

    def my_operation(self, args: dict) -> dict:
        # Implement your operation
        return self.format_success("Success!")

if __name__ == "__main__":
    server = MyServiceMCP()
    server.run()
```

### 4. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Configure MCP

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "myservice": {
      "command": "python",
      "args": ["/absolute/path/to/mcp-servers/myservice/server.py"]
    }
  }
}
```

## Quick Start

### Installing a Server

```bash
# Navigate to server directory
cd mcp-servers/gmail  # or zabbix, elk

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run authentication setup (if required)
python server.py --auth  # (if implemented)
```

### Adding to Claude Desktop

Edit your Claude Desktop configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "gmail": {
      "command": "python",
      "args": ["/absolute/path/to/mcp-servers/gmail/enhanced_server.py"]
    },
    "zabbix": {
      "command": "python",
      "args": ["/absolute/path/to/mcp-servers/zabbix/server.py"]
    },
    "elk": {
      "command": "python",
      "args": ["/absolute/path/to/mcp-servers/elk/server.py"]
    }
  }
}
```

## Development

### Template Components

The template framework provides:

1. **BaseMCPServer**: Core server functionality
   - Tool registration and handling
   - Response formatting
   - Error management
   - Async server execution

2. **BaseAuthHandler**: Authentication patterns
   - OAuth2 (with token refresh)
   - Token-based (API tokens)
   - Basic auth (username/password)

3. **Helper Functions**:
   - `create_json_schema()`: Build JSON schemas easily
   - `format_success()`: Standardized success responses
   - `format_error()`: Standardized error responses

### Best Practices

1. **Use the template framework** for consistency
2. **Follow naming conventions**:
   - Server names: lowercase with hyphens (e.g., `my-service`)
   - Tool names: snake_case (e.g., `get_user_info`)
3. **Provide clear descriptions** for all tools
4. **Include examples** in documentation
5. **Handle errors gracefully** with descriptive messages
6. **Use type hints** for better code clarity
7. **Test thoroughly** before deployment

## Requirements

- Python 3.7+
- mcp >= 0.9.0
- Service-specific dependencies (see individual requirements.txt)

## License

MIT License - See individual server LICENSE files for details

## Contributing

To add a new MCP server:

1. Create new directory in `mcp-servers/`
2. Use template framework from `template/`
3. Implement server using `BaseMCPServer`
4. Add authentication if needed
5. Create comprehensive README
6. Test thoroughly
7. Update this main README

## Version History

### Repository
- v1.0.0 (2025-01-09): Initial multi-server repository
  - Template framework
  - Gmail MCP v2.1
  - Zabbix MCP v1.0
  - ELK MCP v1.0

### Individual Servers
- **Gmail**: v2.1.0 - 16 features, attachments, full email management
