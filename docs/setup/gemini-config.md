# Gemini CLI - MCP Servers Final Configuration
**Date:** October 9, 2025
**Status:** ✅ WORKING

---

## Summary

Successfully configured and tested **2 working MCP servers** for Gemini CLI:

| MCP Server | Status | Tested | Notes |
|------------|--------|--------|-------|
| ✅ **Gmail** (Custom) | WORKING | ✅ | Email search, read, send |
| ✅ **Filesystem** | WORKING | ✅ | File read/write/list operations |
| ❌ Brave Search | DISABLED | N/A | Invalid API token |
| ❌ Playwright | DISABLED | N/A | Browser lock issues |
| ❌ Puppeteer | DISABLED | ✅ | Requires X server (headless incompatible) |

---

## Final Configuration

**Config File:** `~/.gemini/settings.json`

```json
{
  "mcpServers": {
    "gmail": {
      "command": "/home/vjrana/custom-gmail-mcp/venv/bin/python",
      "args": [
        "/home/vjrana/custom-gmail-mcp/server.py"
      ],
      "env": {}
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/home/vjrana"
      ],
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
npm list -g | grep mcp
```

**Result:**
```
├── @modelcontextprotocol/server-filesystem@2025.8.21
├── chrome-devtools-mcp@0.6.0
├── puppeteer-mcp-server@0.7.2  # Disabled - requires X server
```

---

## Test Results

### ✅ Test 1: Gmail MCP
```bash
$ gemini -y -m gemini-2.5-flash -p "search my emails with query 'is:unread' and show count"

You have 10 unread emails.
```

**Status:** ✅ WORKING

---

### ✅ Test 2: Filesystem MCP - Read File
```bash
$ gemini -y -m gemini-2.5-flash -p "read test-mcp-file.txt"

The file `test-mcp-file.txt` contains the text "test file for mcp".
```

**Status:** ✅ WORKING

---

### ✅ Test 3: Filesystem MCP - List Files
```bash
$ gemini -y -m gemini-2.5-flash -p "list files in current directory that start with 'mcp'"

I found the following files in your current directory that start with 'mcp':
*   `/home/vjrana/mcp-gemini-test.sh`
*   `/home/vjrana/mcp-quick-reference.md`
*   `/home/vjrana/mcp-setup-summary.md`
*   `/home/vjrana/mcp-tools-test-results.md`
```

**Status:** ✅ WORKING

---

### ❌ Test 4: Puppeteer MCP - Browser Navigation
```bash
$ gemini -y -m gemini-2.5-flash -p "navigate to https://example.com"

Error executing tool puppeteer_navigate: MCP error -32603: Failed to launch the browser process!
Missing X server or $DISPLAY
```

**Status:** ❌ FAILED
**Reason:** Puppeteer requires graphical display server (X11), not available in headless environment
**Action:** Removed from configuration

---

## Disabled MCP Servers

### 1. Brave Search
- **Reason:** Invalid subscription token
- **Error:** `SUBSCRIPTION_TOKEN_INVALID (422)`
- **Fix Required:** Sign up at https://brave.com/search/api/ and add API key

### 2. Playwright
- **Reason:** Browser lock issues
- **Error:** `Browser is already in use`
- **Alternative:** Use Agent Browser MCP (available in Claude Code)

### 3. Puppeteer
- **Reason:** Requires X server for display
- **Error:** `Missing X server or $DISPLAY`
- **Environment:** Headless Linux server without GUI
- **Alternative:** Use Agent Browser MCP (available in Claude Code) or install headless browser

---

## Usage Examples

### Gmail MCP
```bash
# Search emails
gemini -p "search my emails for job opportunities"

# Read specific email
gemini -p "show me details of my latest unread email"

# Count unread
gemini -p "how many unread emails do I have?"
```

### Filesystem MCP
```bash
# Read file
gemini -p "read the file test.txt"

# List files
gemini -p "list all markdown files in current directory"

# Get file info
gemini -p "what's the size of email-digest.sh?"

# Search files
gemini -p "find Python files that contain 'mcp'"
```

---

## Model Recommendations

**Recommended Model:** `gemini-2.5-flash`

```bash
# Use 2.5 Flash (faster, better for MCP)
gemini -y -m gemini-2.5-flash -p "your prompt here"

# Alternative: 2.0 Flash Experimental
gemini -y -m gemini-2.0-flash-exp -p "your prompt here"
```

### Why Gemini 2.5 Flash?
- ✅ Faster response times
- ✅ Better MCP tool integration
- ✅ More reliable with filesystem operations
- ✅ Lower latency for interactive use

---

## MCP Server Capabilities

### Gmail MCP (Custom)
**Tools:**
- `search_emails(query, max_results)` - Search with Gmail syntax
- `read_email(message_id)` - Read full email content
- `send_email(to, subject, body)` - Send emails

**Features:**
- Gmail OAuth2 authentication
- Full Gmail API access
- Returns structured JSON
- Supports all Gmail search operators

**Examples:**
```bash
# Search queries
"is:unread newer_than:1d"
"from:recruiter job"
"subject:invoice"
"has:attachment"
```

### Filesystem MCP
**Tools:**
- `read_file(path)` - Read file contents
- `write_file(path, content)` - Create/overwrite files
- `list_files(directory)` - List directory contents
- `search_files(pattern)` - Find files by pattern
- `get_file_info(path)` - File metadata

**Scope:** `/home/vjrana` directory
**Note:** Current working directory determines access

**Features:**
- Supports text files
- Handles large files
- Directory traversal
- File search and filtering

---

## Troubleshooting

### Gmail MCP Not Working
```bash
# Re-authenticate
cd ~/custom-gmail-mcp
source venv/bin/activate
python server.py

# Test directly
~/gmail search "test" 1
```

### Filesystem MCP Permission Issues
```bash
# Check working directory
pwd  # Should be /home/vjrana or subdirectory

# Navigate to allowed directory
cd /home/vjrana

# Then run gemini command
gemini -p "read file.txt"
```

### MCP Server Not Loading
```bash
# Verify npm packages installed
npm list -g @modelcontextprotocol/server-filesystem

# Check gemini config syntax
cat ~/.gemini/settings.json | jq .

# View gemini logs (verbose mode)
gemini -v -p "test prompt"
```

### Gemini Timeout Issues
```bash
# Use shorter prompts
# Use -y flag to skip confirmations
# Use faster model (2.5-flash)
gemini -y -m gemini-2.5-flash -p "short prompt"
```

---

## Comparison: Claude Code vs Gemini CLI

### Claude Code (Built-in MCP)
**Pros:**
- ✅ All MCP servers work automatically
- ✅ Filesystem, GitHub, Agent Browser, TestSprite built-in
- ✅ No configuration needed
- ✅ Better integration

**MCP Servers:**
- ✅ Filesystem
- ✅ GitHub
- ✅ Gmail (custom)
- ✅ Agent Browser
- ✅ TestSprite
- ⚠️ Playwright (limited)
- ❌ Brave Search (no API key)

### Gemini CLI (Standalone MCP)
**Pros:**
- ✅ Can use latest Gemini models (2.5 Flash)
- ✅ Command-line interface
- ✅ Scriptable automation

**Cons:**
- ⚠️ Limited to standalone MCP packages
- ⚠️ Requires manual configuration
- ⚠️ No browser automation (headless limitation)

**MCP Servers:**
- ✅ Gmail (custom)
- ✅ Filesystem
- ❌ GitHub (no standalone package found)
- ❌ Browser automation (requires X server)
- ❌ Brave Search (no API key)

---

## Next Steps

### Add More MCP Servers
1. **Search for packages:**
   ```bash
   npm search @modelcontextprotocol
   ```

2. **Install package:**
   ```bash
   npm install -g <package-name>
   ```

3. **Add to config:**
   Edit `~/.gemini/settings.json`
   ```json
   "server-name": {
     "command": "npx",
     "args": ["-y", "package-name"],
     "env": {}
   }
   ```

4. **Test:**
   ```bash
   gemini -p "use server-name to do something"
   ```

### Potential MCP Servers to Add
- **@modelcontextprotocol/server-memory** - Persistent memory
- **@modelcontextprotocol/server-postgres** - Database access
- **Weather MCP** - Weather data
- **Slack MCP** - Slack messaging
- **Custom MCP** - Build your own (like Gmail)

---

## Test Script

**Location:** `~/mcp-gemini-test.sh`

```bash
#!/bin/bash
echo "=== Gemini CLI MCP Server Tests ==="
echo ""
echo "Test 1: Gmail MCP - Search emails"
gemini -y -m gemini-2.5-flash -p "search my emails with query 'is:unread' and show count"
echo ""
echo "Test 2: Filesystem MCP - Read file"
gemini -y -m gemini-2.5-flash -p "read test-mcp-file.txt"
echo ""
echo "Test 3: Filesystem MCP - List files"
