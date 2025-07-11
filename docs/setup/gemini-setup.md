# Gemini CLI - Complete MCP Setup
**Date:** October 9, 2025
**Status:** ✅ FULLY OPERATIONAL
**Model:** Gemini 2.5 Flash (Recommended)

---

## Executive Summary

Successfully configured **3 working MCP servers** for Gemini CLI with comprehensive testing and verification.

| MCP Server | Status | Capabilities |
|------------|--------|--------------|
| ✅ **Gmail** (Custom) | WORKING | Search, read, send emails |
| ✅ **Filesystem** | WORKING | Read, write, list, search files |
| ✅ **Agent Browser** | WORKING | Navigate web, extract content |
| ❌ Playwright | DISABLED | Browser lock conflict |
| ❌ Puppeteer | DISABLED | Requires X server |
| ❌ Git MCP | DISABLED | Model stream compatibility issue |

---

## Final Configuration

**Config File:** `~/.gemini/settings.json`

```json
{
  "mcpServers": {
    "gmail": {
      "command": "/home/vjrana/custom-gmail-mcp/venv/bin/python",
      "args": ["/home/vjrana/custom-gmail-mcp/server.py"],
      "env": {}
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/vjrana"],
      "env": {}
    },
    "agent-browser": {
      "command": "npx",
      "args": ["-y", "@agent-infra/mcp-server-browser"],
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

---

## Installed MCP Packages

```bash
$ npm list -g | grep mcp

/home/vjrana/.nvm/versions/node/v22.16.0/lib
├── @agent-infra/mcp-server-browser@1.2.23       ✅ ACTIVE
├── @cyanheads/git-mcp-server@2.3.5              ❌ DISABLED
├── @modelcontextprotocol/server-filesystem@2025.8.21  ✅ ACTIVE
├── @playwright/mcp@0.0.41                       ❌ DISABLED
├── chrome-devtools-mcp@0.6.0
├── puppeteer-mcp-server@0.7.2                   ❌ DISABLED
```

---

## Verification Test Results

### All Tests Passed ✅

```bash
$ bash ~/mcp-final-test.sh

╔════════════════════════════════════════════════════════════════╗
║         GEMINI CLI - ALL MCP SERVERS FINAL TEST                ║
╚════════════════════════════════════════════════════════════════╝

Test 1: Gmail MCP - Search and count unread emails
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ RESULT: "You have 10 unread emails."

Test 2: Filesystem MCP - Read file
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ RESULT: "The content of test-mcp-file.txt is: test file for mcp"

Test 3: Filesystem MCP - List files
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ RESULT: Found 3 files containing 'mcp' in name

Test 4: Agent Browser MCP - Navigate and extract
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ RESULT: "The main heading on https://example.com is 'Example Domain'."

╔════════════════════════════════════════════════════════════════╗
║                    ALL TESTS COMPLETE - 100% PASS              ║
╚════════════════════════════════════════════════════════════════╝
```

---

## MCP Server Details

### 1. ✅ Gmail MCP (Custom)

**Type:** Custom Python MCP server
**Location:** `/home/vjrana/custom-gmail-mcp/server.py`
**Status:** WORKING

**Capabilities:**
- Search emails with Gmail query syntax
- Read full email content (subject, from, to, body)
- Send emails via Gmail API
- OAuth2 authentication

**Tools:**
- `search_emails(query, max_results)` - Gmail search
- `read_email(message_id)` - Read email
- `send_email(to, subject, body)` - Send email

**Usage Examples:**
```bash
# Search unread emails
gemini -y -m gemini-2.5-flash -p "search my emails with query 'is:unread' and count them"

# Search by sender
gemini -y -m gemini-2.5-flash -p "search emails from REDACTED_EMAIL"

# Search by subject
gemini -y -m gemini-2.5-flash -p "find emails about job opportunities from last week"

# Read specific email
gemini -y -m gemini-2.5-flash -p "read the latest unread email and summarize it"
```

**Gmail Search Operators:**
```
is:unread           - Unread emails
newer_than:1d       - From last 24 hours
from:REDACTED_EMAIL - From specific sender
subject:invoice     - With subject
has:attachment      - With attachments
```

**CLI Wrapper:** `~/gmail`
```bash
~/gmail search "is:unread" 10
~/gmail read <message_id>
```

---

### 2. ✅ Filesystem MCP

**Package:** `@modelcontextprotocol/server-filesystem@2025.8.21`
**Type:** Official MCP server
**Status:** WORKING

**Capabilities:**
- Read text files
- Write/create files
- List directory contents
- Search files by pattern
- Get file metadata
- Directory operations

**Scope:** `/home/vjrana` directory
**Note:** Working directory determines accessible files

**Tools:**
- `read_file(path)` - Read file contents
- `write_file(path, content)` - Create/overwrite file
- `list_files(directory)` - List directory
- `search_files(pattern)` - Find files
- `get_file_info(path)` - File metadata
- `create_directory(path)` - Create directory
- `move_file(source, dest)` - Move/rename file

**Usage Examples:**
```bash
# Read file
gemini -y -m gemini-2.5-flash -p "read the file email-digest.sh"

# List files
gemini -y -m gemini-2.5-flash -p "list all Python files in current directory"

# Search files
gemini -y -m gemini-2.5-flash -p "find files containing 'mcp' in the name"

# Get file info
gemini -y -m gemini-2.5-flash -p "what's the size of test.txt?"

# Create file
gemini -y -m gemini-2.5-flash -p "create a file called notes.txt with content 'Hello World'"
```

---

### 3. ✅ Agent Browser MCP

**Package:** `@agent-infra/mcp-server-browser@1.2.23`
**Type:** Third-party MCP server
**Status:** WORKING

**Capabilities:**
- Navigate to websites
- Extract page content (text, markdown, HTML)
- Click elements
- Fill forms
- Take screenshots
- Execute JavaScript
- Handle tabs

**Tools:**
- `browser_navigate(url)` - Navigate to URL
- `browser_get_text()` - Extract page text
- `browser_get_markdown()` - Get markdown
- `browser_click(index)` - Click element
- `browser_screenshot()` - Take screenshot
- `browser_evaluate(script)` - Run JavaScript
- `browser_read_links()` - Get all links

**Usage Examples:**
```bash
# Navigate and extract
gemini -y -m gemini-2.5-flash -p "use agent-browser to navigate to https://example.com and extract the main heading"

# Get page content
gemini -y -m gemini-2.5-flash -p "navigate to anthropic.com and summarize the page content"

# Extract links
gemini -y -m gemini-2.5-flash -p "go to github.com/modelcontextprotocol and list all repositories"

# Take screenshot
gemini -y -m gemini-2.5-flash -p "navigate to example.com and take a screenshot"
```

**Advantages:**
- ✅ Works in headless environment
- ✅ No X server required
- ✅ No browser lock issues
- ✅ Better than Playwright for Gemini CLI

---

## Disabled MCP Servers

### ❌ Playwright MCP

**Package:** `@playwright/mcp@0.0.41`
**Reason:** Browser lock conflict
**Error:** `Browser is already in use for /home/vjrana/.cache/ms-playwright/mcp-chrome-0a921a2`

**Issue:** Cannot run multiple concurrent browser instances without `--isolated` flag

**Alternative:** Use Agent Browser MCP instead

---

### ❌ Puppeteer MCP

