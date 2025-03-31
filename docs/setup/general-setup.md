# MCP Tools Setup Summary
**Date:** October 9, 2025

## Test Results Overview

Tested **7 MCP servers** available in Claude Code:

| Server | Status | Gemini CLI Ready |
|--------|--------|------------------|
| Filesystem | ✅ Working | Built-in to Claude Code |
| Brave Search | ❌ No API Key | Requires setup |
| GitHub | ✅ Working | Built-in to Claude Code |
| Gmail | ✅ Working | ✅ Already configured |
| Playwright | ⚠️ Limited | Built-in to Claude Code |
| Agent Browser | ✅ Working | Built-in to Claude Code |
| TestSprite | ✅ Working | Built-in to Claude Code |

---

## MCP Servers in Claude Code (Built-in)

These MCP servers are **built into Claude Code** and work automatically:

### ✅ Filesystem MCP
- **Access:** Automatic (no setup needed)
- **Scope:** `/home/vjrana` directory only
- **Functions:** read, write, edit, search, move files
- **Use:** File operations without bash commands

### ✅ GitHub MCP
- **Access:** Automatic (authenticated via GitHub token)
- **Functions:** Search repos/code, create/read files, manage PRs/issues
- **Tested:** ✅ Search returned 42,767+ repositories

### ✅ Gmail MCP (Custom)
- **Location:** `/home/vjrana/custom-gmail-mcp/`
- **Type:** Custom Python server we built
- **Functions:** search_emails, read_email, send_email
- **Status:** ✅ Configured in Gemini CLI
- **CLI Wrapper:** `/home/vjrana/gmail` command

### ✅ Agent Browser MCP
- **Access:** Automatic
- **Functions:** Navigate, scrape, click, screenshot
- **Tested:** ✅ Successfully loaded https://example.com
- **Better than:** Playwright (no lock issues)

### ✅ TestSprite MCP
- **Access:** Automatic
- **Functions:** Test generation, code analysis, PRD creation
- **Use Case:** Automated testing workflows

### ⚠️ Playwright MCP
- **Status:** Limited (browser lock issue)
- **Recommendation:** Use Agent Browser instead

### ❌ Brave Search MCP
- **Status:** Not working
- **Issue:** Missing API subscription token
- **Fix:** Need to sign up at https://brave.com/search/api/

---

## Gemini CLI Configuration

**Current Config:** `~/.gemini/settings.json`

```json
{
  "mcpServers": {
    "gmail": {
      "command": "/home/vjrana/custom-gmail-mcp/venv/bin/python",
      "args": ["/home/vjrana/custom-gmail-mcp/server.py"],
      "env": {}
    }
  },
  "security": {
    "auth": {
      "selectedType": "gemini-api-key"
    }
  }
}
```

### Why Only Gmail is Configured for Gemini?

**Built-in MCP Servers** (Filesystem, GitHub, Agent Browser, TestSprite, Playwright):
- These are **native to Claude Code**
- They use Claude Code's internal MCP protocol implementation
- Cannot be easily exported to other MCP clients like Gemini CLI
- Would require finding/installing standalone versions

**Custom Gmail MCP:**
- We built this as a **standalone Python MCP server**
- It follows the standard MCP protocol
- Can be shared across different MCP clients
- That's why it works with both Claude Code and Gemini CLI

---

## Using MCP Tools

### In Claude Code (CLI)
All MCP tools are available automatically:

```bash
# Example: Search GitHub repos
"Search for MCP servers on GitHub and show top 5"

# Example: Read emails
"Show me my latest 10 unread emails"

# Example: Web scraping
"Navigate to example.com and extract all text"
```

### In Gemini CLI
Only Gmail MCP is configured:

```bash
# Using gemini-cli with Gmail MCP
gemini -p "Search my unread emails and summarize"

# Direct Gmail CLI wrapper
~/gmail search "is:unread" 10
~/gmail read <message_id>
```

### Command Line Scripts
We also built standalone tools:

```bash
# Send email/SMS
echo "Test message" | sendmail REDACTED_EMAIL

# Email digest (automated)
~/email-digest.sh  # Runs daily at 8 AM

# Test email digest
~/test-email-digest.sh
```

---

## MCP Architecture Explanation

### How MCP Servers Work

**Model Context Protocol (MCP)** is a standardized way for AI assistants to access external tools and data sources.

```
┌─────────────────┐
│   AI Assistant  │ (Claude Code, Gemini CLI, etc.)
└────────┬────────┘
         │ MCP Protocol (JSON-RPC)
         │
┌────────┴────────┐
│   MCP Server    │ (Gmail, GitHub, Filesystem, etc.)
└────────┬────────┘
         │
┌────────┴────────┐
│  External API   │ (Gmail API, GitHub API, Local Files)
└─────────────────┘
```

**Built-in vs Custom MCP Servers:**

1. **Built-in** (Filesystem, GitHub, Agent Browser, TestSprite):
   - Bundled with Claude Code
   - Configured automatically
   - Not easily portable to other MCP clients

2. **Custom** (Our Gmail server):
   - Standalone Python/Node scripts
   - Follow MCP SDK specification
   - Portable across MCP clients
   - Require manual configuration

---

## Building Custom MCP Servers

### Example: Our Gmail MCP Server

**Location:** `/home/vjrana/custom-gmail-mcp/server.py`

**Structure:**
```python
from mcp.server import Server, stdio_server
from mcp.types import Tool, TextContent

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(name="search_emails", description="Search Gmail"),
        Tool(name="read_email", description="Read email"),
        Tool(name="send_email", description="Send email")
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "search_emails":
        # Gmail API implementation
        ...
```

**Configuration:**
```json
{
  "mcpServers": {
    "gmail": {
      "command": "/path/to/python",
      "args": ["/path/to/server.py"],
      "env": {}
    }
  }
}
```

### Why We Built Custom Gmail MCP

1. Existing Gmail MCP servers had issues
2. Needed specific functionality (search, read, send)
3. Wanted control over authentication
4. Needed it to work with both Claude Code and Gemini CLI

---

## Files Created

```
~/custom-gmail-mcp/           # Custom Gmail MCP server
  ├── server.py              # Main MCP server
  ├── venv/                  # Python virtual environment
  └── credentials.json       # Gmail OAuth credentials

~/gmail                       # Gmail CLI wrapper script
~/sendmail.sh                 # Universal email/SMS sender
~/email-digest.sh             # Automated email digest
~/test-email-digest.sh        # Manual testing tool
~/email-importance-analyzer.py # AI email scorer

~/mcp-test.txt                # Test file from MCP testing
~/mcp-tools-test-results.md   # Detailed test results
~/mcp-setup-summary.md        # This file
```

---

## Usage Examples

### 1. Gmail MCP (via CLI wrapper)
```bash
# Search emails
~/gmail search "is:unread newer_than:1d" 50

# Read specific email
~/gmail read 199c71d09d501dd6

# Used by email-digest.sh
EMAILS_JSON=$(~/gmail search "is:unread newer_than:1d" 50)
```

### 2. SendMail Script
```bash
# Send email
echo "Hello from CLI" | sendmail REDACTED_EMAIL

# Send SMS (via email gateway)
echo "Alert: Server down" | sendmail REDACTED_EMAIL

# With subject
SUBJECT="Important" echo "Message body" | sendmail REDACTED_EMAIL
```

### 3. Email Digest System
```bash
# Manual test (terminal output)
~/test-email-digest.sh

# Full run (sends SMS)
~/email-digest.sh

# Automated (cron)
# Runs daily at 8:00 AM automatically
```

### 4. MCP Tools in Claude Code
Just ask in natural language:

```
"Search GitHub for mcp servers"
"Read my unread emails from today"
"Navigate to example.com and get the page text"
"Create a file called test.txt with hello world"
```

---

## Next Steps

### To Add More MCP Servers to Gemini CLI:

1. **Find or Build Standalone MCP Server**
   - Search npm: `npm search @modelcontextprotocol`
   - Or build custom (Python/Node) following MCP SDK

2. **Install/Setup Server**
   ```bash
   npm install -g @modelcontextprotocol/server-name
   # or for Python
   pip install mcp-server-name
   ```

3. **Add to ~/.gemini/settings.json**
   ```json
   {
     "mcpServers": {
       "gmail": { ... },
       "new-server": {
         "command": "npx",
