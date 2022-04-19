# Enhanced Gmail MCP Server

A production-ready Model Context Protocol (MCP) server providing comprehensive Gmail integration for Claude Code and other MCP-compatible clients.

[![Security Rating](https://img.shields.io/badge/Security-A%20(Excellent)-brightgreen)]()
[![Test Pass Rate](https://img.shields.io/badge/Tests-100%25%20Pass-success)]()
[![Features](https://img.shields.io/badge/Features-16-blue)]()
[![Version](https://img.shields.io/badge/Version-2.1-informational)]()

---

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Gmail API Credentials Setup](#gmail-api-credentials-setup)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)
- [Security](#security)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Support](#support)

---

## Features (16 Total)

### 📧 Email Reading & Search
- **search_emails** - Search with Gmail query syntax (`is:unread`, `from:REDACTED_EMAIL`, etc.)
- **read_email** - Full email content, headers, body
- **get_thread** - All messages in conversation thread
- **list_attachments** - List all attachments in an email ⭐ NEW
- **download_attachment** - Download attachments to local storage ⭐ NEW

### ✉️ Email Sending & Composing
- **send_email** - Send with CC/BCC support
- **reply_to_email** - Reply maintaining thread context
- **create_draft** - Save emails as drafts

### 🏷️ Email Organization
- **mark_as_read** / **mark_as_unread** - Manage read status
- **star_email** - Star/unstar important emails
- **archive_email** - Remove from inbox
- **delete_email** - Move to trash (recoverable)

### 📁 Label Management
- **list_labels** - List all Gmail labels/folders
- **add_label** / **remove_label** - Organize emails with labels

---

## Quick Start

```bash
# 1. Clone repository
git clone https://github.com/vjranagit/enhanced-gmail-mcp.git
cd enhanced-gmail-mcp

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up Gmail API credentials (see detailed guide below)
# Follow "Gmail API Credentials Setup" section

# 5. Authenticate
python enhanced_server.py --authenticate

# 6. Configure in Claude Code
# Add to ~/.claude.json (see Configuration section)

# 7. Test
python test_all_features.py
```

---

## Installation

### Prerequisites
- **Python 3.8+** (tested with 3.10)
- **Gmail account** with API access enabled
- **Google Cloud account** (free tier works)
- **Claude Code** or **Claude Desktop** (or any MCP-compatible client)
- **Git** (for cloning repository)

### Step 1: Clone Repository

```bash
git clone https://github.com/vjranagit/enhanced-gmail-mcp.git
cd enhanced-gmail-mcp
```

### Step 2: Create Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Verify activation:**
```bash
which python  # Linux/macOS
where python  # Windows
# Should show path inside venv folder
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Dependencies installed:**
- `google-auth-oauthlib` - OAuth 2.0 authentication
- `google-auth-httplib2` - HTTP client for Google APIs
- `google-api-python-client` - Gmail API client
- `mcp` - Model Context Protocol framework

**Verify installation:**
```bash
pip list | grep google
# Should show: google-api-python-client, google-auth, google-auth-httplib2, google-auth-oauthlib
```

---

## Gmail API Credentials Setup

This is the most important step. Follow this detailed guide to set up Gmail API access.

### Overview

You'll need to:
1. Create a Google Cloud Project
2. Enable Gmail API
3. Configure OAuth Consent Screen
4. Create OAuth 2.0 Credentials
5. Download and place credentials file
6. Authenticate with your Gmail account

**Time required:** ~10-15 minutes (first time)

---

### Step 1: Create Google Cloud Project

1. **Open Google Cloud Console**
   - Go to: https://console.cloud.google.com/
   - Sign in with your Google account (any Gmail account works)

2. **Create New Project**
   - Click the project dropdown at the top (says "Select a project")
   - Click **"NEW PROJECT"** button (top right)
   - **Project name**: Enter `Gmail MCP Server` (or any name you prefer)
   - **Organization**: Leave as "No organization" (unless you have one)
   - Click **"CREATE"**
   - Wait ~30 seconds for project creation

3. **Select Your Project**
   - Once created, click the project dropdown again
   - Select your new project (`Gmail MCP Server`)
   - The project name should appear in the top blue bar

---

### Step 2: Enable Gmail API

1. **Open API Library**
   - In the left sidebar, click **"APIs & Services"** → **"Library"**
   - Or use direct link: https://console.cloud.google.com/apis/library

2. **Find Gmail API**
   - In the search box, type: `Gmail API`
   - Click on **"Gmail API"** from the results (by Google)

3. **Enable the API**
   - Click the blue **"ENABLE"** button
   - Wait for activation (~1-2 minutes)
   - You'll see "API enabled" confirmation

---

### Step 3: Configure OAuth Consent Screen

This screen is shown to users (you) when authenticating.

1. **Open OAuth Consent Screen**
   - Left sidebar → **"APIs & Services"** → **"OAuth consent screen"**
   - Or direct link: https://console.cloud.google.com/apis/credentials/consent

2. **Choose User Type**
   - Select **"External"** (allows any Gmail account to use it)
   - Click **"CREATE"**

3. **App Information** (Page 1 of 4)
   - **App name**: `Gmail MCP Server` (or your choice)
   - **User support email**: Select your Gmail address from dropdown
   - **App logo**: Leave blank (optional)
   - **App domain**: Leave blank (not needed for personal use)
   - **Developer contact information**: Enter your Gmail address
   - Click **"SAVE AND CONTINUE"**

4. **Scopes** (Page 2 of 4)
   - Click **"ADD OR REMOVE SCOPES"**
   - In the filter box, search for: `gmail`
   - Find and select: **`https://www.googleapis.com/auth/gmail.modify`**
     - This scope allows reading, sending, and modifying emails
   - Click **"UPDATE"** at bottom
   - Click **"SAVE AND CONTINUE"**

5. **Test Users** (Page 3 of 4)
   - Click **"ADD USERS"**
   - Enter your Gmail address (the one you'll use with this MCP server)
   - Click **"ADD"**
   - Click **"SAVE AND CONTINUE"**
   - ⚠️ **IMPORTANT**: Only test users can use the app until it's published

6. **Summary** (Page 4 of 4)
   - Review your settings
   - Click **"BACK TO DASHBOARD"**

---

### Step 4: Create OAuth 2.0 Credentials

1. **Open Credentials Page**
   - Left sidebar → **"APIs & Services"** → **"Credentials"**
   - Or direct link: https://console.cloud.google.com/apis/credentials

2. **Create Credentials**
   - Click **"+ CREATE CREDENTIALS"** (top of page)
   - Select **"OAuth client ID"** from dropdown

3. **Choose Application Type**
   - **Application type**: Select **"Desktop app"**
     - ⚠️ **DO NOT select "Web application"** - it won't work!
   - **Name**: Enter `Gmail MCP Client` (or any name)
   - Click **"CREATE"**

4. **Download Credentials**
   - A popup appears: "OAuth client created"
   - Click **"DOWNLOAD JSON"** button
   - Save file as `credentials.json`
   - **Remember the download location** (usually `~/Downloads/credentials.json`)
   - Click **"OK"** to close popup

---

### Step 5: Place Credentials File

The credentials file must be placed in `~/.gmail-mcp/` directory (outside the repository for security).

**Linux/macOS:**
```bash
# Create directory for Gmail MCP credentials
mkdir -p ~/.gmail-mcp

# Copy credentials file (adjust path if needed)
cp ~/Downloads/credentials.json ~/.gmail-mcp/credentials.json

# Verify file exists and has content
ls -lh ~/.gmail-mcp/credentials.json
cat ~/.gmail-mcp/credentials.json | head -n 5
```

**Windows (PowerShell):**
```powershell
# Create directory
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.gmail-mcp"

# Copy credentials (adjust path if needed)
Copy-Item "$env:USERPROFILE\Downloads\credentials.json" "$env:USERPROFILE\.gmail-mcp\credentials.json"

# Verify
Get-Item "$env:USERPROFILE\.gmail-mcp\credentials.json"
```

**Expected credentials.json format:**
```json
{
  "installed": {
    "client_id": "123456789-abcdefg.apps.googleusercontent.com",
    "project_id": "gmail-mcp-server-123456",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_secret": "GOCSPX-xxxxxxxxxxxxx",
    ...
  }
}
```

⚠️ **Security Note**: This file contains your OAuth client secret. Never commit it to git or share it publicly.

---

### Step 6: Authenticate with Gmail

Now authenticate your Gmail account to generate an access token.

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Run authentication
python enhanced_server.py --authenticate
```

**What happens:**

1. **Browser Opens Automatically**
   - A browser window/tab opens to Google sign-in page
   - If browser doesn't open, copy/paste the URL shown in terminal

2. **Sign In**
   - Sign in with your Gmail account
   - ⚠️ Must be the same account you added as "Test User" in Step 3

3. **Grant Permissions**
   - You'll see: "Gmail MCP Server wants to access your Google Account"
   - Review permissions:
     - ✅ Read, compose, send, and permanently delete all your email from Gmail
   - Click **"Continue"** or **"Allow"**

4. **Success Confirmation**
   - Browser shows: "The authentication flow has completed"
   - Terminal shows: "Authentication successful! Token saved."
   - Token saved to: `~/.gmail-mcp/token.json`

5. **Close Browser**
   - You can now close the browser tab/window

**Token file created:**
```bash
ls -lh ~/.gmail-mcp/
# Should show:
# credentials.json  (OAuth client credentials)
# token.json        (Your access token) ← Just created
```

---

### Troubleshooting Credentials Setup

#### Error: "Access blocked: This app's request is invalid"

**Cause**: OAuth consent screen not configured properly.

**Solution**:
1. Go back to OAuth consent screen
2. Verify your email is added as **Test User**
3. Verify scope `https://www.googleapis.com/auth/gmail.modify` is added
4. Try authenticating again

---

#### Error: "Redirect URI mismatch"

**Cause**: Wrong application type selected (Web app instead of Desktop app).

**Solution**:
1. Go to Credentials page
2. Delete the existing OAuth client ID
3. Create new one with **Application type: Desktop app**
4. Download new credentials.json
5. Replace `~/.gmail-mcp/credentials.json`
6. Try authenticating again

---

#### Error: "The file credentials.json is not found"

**Cause**: Credentials file not in correct location.

**Solution**:
```bash
# Check if file exists
ls -la ~/.gmail-mcp/credentials.json

# If not found, copy it again
cp ~/Downloads/credentials.json ~/.gmail-mcp/credentials.json
```

---

#### Error: "Invalid client"

**Cause**: Corrupted or invalid credentials.json file.

**Solution**:
1. Open credentials.json in text editor
2. Verify it's valid JSON (starts with `{`, ends with `}`)
3. If corrupted, download fresh copy from Google Cloud Console
4. Replace file and try again

---

#### Error: "This app isn't verified"

**Cause**: Your app is in testing mode (normal for personal use).

**Solution**:
1. Click **"Advanced"** (bottom left)
2. Click **"Go to Gmail MCP Server (unsafe)"**
3. This is safe - it's your own app
4. Continue with authentication

---

### Verifying Credentials Are Working

After successful authentication, verify everything works:

```bash
# Test authentication and API access
python -c "
from enhanced_server import get_gmail_service
service = get_gmail_service()
profile = service.users().getProfile(userId='me').execute()
print(f'✅ Authenticated as: {profile[\"emailAddress\"]}')
print(f'✅ Total messages: {profile[\"messagesTotal\"]}')
"
```

**Expected output:**
```
✅ Authenticated as: REDACTED_EMAIL
✅ Total messages: 12345
```

---

## Configuration

After credentials are set up and authentication is complete, configure your MCP client.

### For Claude Code

**Config file**: `~/.claude.json`

**Find your installation path:**
```bash
cd /path/to/enhanced-gmail-mcp
pwd
# Copy the output - this is your absolute path
```

**Edit ~/.claude.json:**

**Linux/macOS:**
```json
{
  "mcpServers": {
    "gmail": {
      "type": "stdio",
      "command": "/absolute/path/to/enhanced-gmail-mcp/venv/bin/python",
      "args": [
        "/absolute/path/to/enhanced-gmail-mcp/enhanced_server.py"
      ],
      "env": {}
    }
  }
}
```

**Windows:**
```json
{
  "mcpServers": {
    "gmail": {
      "type": "stdio",
      "command": "C:\\absolute\\path\\to\\enhanced-gmail-mcp\\venv\\Scripts\\python.exe",
      "args": [
        "C:\\absolute\\path\\to\\enhanced-gmail-mcp\\enhanced_server.py"
      ],
      "env": {}
    }
  }
}
```

**Important notes:**
- ⚠️ Replace `/absolute/path/to/` with your actual path
- ✅ Use **absolute paths** (not `~/` or relative paths)
- ✅ Ensure `command` points to Python **inside venv** folder
- ✅ On Windows, use double backslashes `\\` or forward slashes `/`

**Restart Claude Code** completely (quit and relaunch) after configuration.

---

### For Claude Desktop

**Config file locations:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**Configuration:**

**macOS/Linux:**
```json
{
  "mcpServers": {
    "gmail": {
      "command": "/absolute/path/to/enhanced-gmail-mcp/venv/bin/python",
      "args": ["/absolute/path/to/enhanced-gmail-mcp/enhanced_server.py"]
    }
  }
}
```

**Windows:**
```json
{
  "mcpServers": {
    "gmail": {
      "command": "C:\\absolute\\path\\to\\enhanced-gmail-mcp\\venv\\Scripts\\python.exe",
      "args": ["C:\\absolute\\path\\to\\enhanced-gmail-mcp\\enhanced_server.py"]
    }
  }
}
```

**After configuration:**
1. **Restart** Claude Desktop completely (quit and relaunch)
2. Tools should appear in MCP tools menu
3. Look for: `gmail:search_emails`, `gmail:read_email`, etc.

---

### Verifying Configuration

**Method 1: Check MCP tools in Claude**

After restarting, ask Claude:
```
Can you list my Gmail labels?
```

If configured correctly, Claude should use `mcp__gmail__list_labels` tool.

**Method 2: Direct test**

```bash
# Activate virtual environment
source venv/bin/activate

# Test server directly
python -c "
from enhanced_server import search_emails
result = search_emails(query='is:inbox', max_results=3)
print(result)
"
```

**Method 3: Run test suite**

```bash
cd /path/to/enhanced-gmail-mcp
python test_all_features.py
# Expected: ✅ All executed tests PASSED!
```

---

## Usage Examples

### Search and Read Emails

```python
# Search unread emails
search_emails(query="is:unread", max_results=10)

# Search by sender
search_emails(query="from:REDACTED_EMAIL")

# Complex search
search_emails(query="is:unread subject:urgent has:attachment")

# Read full email
read_email(message_id="abc123")
```

### Manage Email Attachments ⭐ NEW

```python
# List all attachments in an email
attachments = list_attachments(message_id="abc123")
# Returns:
# {
#   "status": "success",
#   "message_id": "abc123",
#   "attachment_count": 2,
#   "attachments": [
#     {
#       "filename": "document.pdf",
#       "mimeType": "application/pdf",
#       "size": 42826,
#       "attachmentId": "ANGjdJ..."
#     },
#     {
#       "filename": "image.png",
#       "mimeType": "image/png",
#       "size": 6479,
#       "attachmentId": "ANGjdJ..."
#     }
#   ]
# }

# Download attachment to ~/Downloads (default)
download_attachment(
    message_id="abc123",
    attachment_id="ANGjdJ...",
    filename="document.pdf"
)

# Download to custom location
download_attachment(
    message_id="abc123",
    attachment_id="ANGjdJ...",
    filename="report.pdf",
    save_path="/home/user/Documents"
)
```

### Organize Emails

```python
# Mark as read
mark_as_read(message_id="abc123")

# Mark as unread
mark_as_unread(message_id="abc123")

# Star important email
star_email(message_id="abc123", star=True)

# Unstar
star_email(message_id="abc123", star=False)

# Add label
labels = list_labels()  # Get label IDs first
add_label(message_id="abc123", label_id="Label_123")

# Remove label
remove_label(message_id="abc123", label_id="Label_123")

# Archive (remove from inbox)
archive_email(message_id="abc123")

# Delete (move to trash, recoverable for 30 days)
delete_email(message_id="abc123")
```

### Send Emails

```python
# Simple email
send_email(
    to="recipient@example.com",
    subject="Meeting Tomorrow",
    body="Let's meet at 2 PM in conference room A."
)

# Email with CC and BCC
send_email(
    to="recipient@example.com",
    subject="Team Update",
    body="Here's the weekly update...",
    cc="REDACTED_EMAIL",
    bcc="REDACTED_EMAIL"
)

# Reply to email
reply_to_email(
    message_id="abc123",
    body="Thanks for your email. I'll look into this."
)

# Create draft
create_draft(
    to="client@example.com",
    subject="Project Proposal",
    body="Attached is the proposal we discussed..."
)
```

### Work with Threads

```python
# Get entire email conversation
thread = get_thread(thread_id="thread_abc123")
# Returns all messages in the thread with full content
```

### Automate Email Workflows

```python
# Automated job email organization
jobs = search_emails(query='subject:(job OR opportunity) is:unread', max_results=10)

for job in jobs['messages']:
    email = read_email(job['id'])

    # Filter for engineering jobs
    if 'engineer' in email['subject'].lower() or 'developer' in email['subject'].lower():
        star_email(job['id'])  # Star important ones
        add_label(job['id'], "Label_job_opportunities")  # Add job label
        mark_as_read(job['id'])  # Mark as processed

# Save attachments from important emails
important = search_emails(query='is:starred has:attachment', max_results=5)
for msg in important['messages']:
    attachments = list_attachments(msg['id'])
    for att in attachments['attachments']:
        if att['filename'].endswith('.pdf'):
            download_attachment(
                message_id=msg['id'],
                attachment_id=att['attachmentId'],
                filename=att['filename'],
                save_path="/home/user/important-docs"
            )
```

### Gmail Search Syntax

Powerful search operators:

**Status filters:**
- `is:unread` / `is:read` / `is:starred` / `is:important`
- `is:sent` / `is:draft` / `is:inbox`

**Sender/Recipient:**
- `from:sender@example.com`
- `to:recipient@example.com`

**Content:**
- `subject:keyword` - Subject contains keyword
- `body:keyword` - Body contains keyword
- `has:attachment` - Has attachments
- `filename:pdf` - Has PDF attachment

**Date filters:**
- `after:2025/01/01` / `before:2025/12/31`
- `newer_than:2d` (2 days) / `older_than:1m` (1 month)
- `newer_than:1h` (1 hour)

**Labels:**
- `label:work` / `label:important`

**Combine with AND/OR:**
- `is:unread from:REDACTED_EMAIL` (AND is implicit)
- `subject:urgent OR subject:important`
- `from:(alice@example.com OR bob@example.com)`

**Advanced:**
- `has:drive` - Has Google Drive attachment
- `has:youtube` - Has YouTube video
- `larger:5M` - Larger than 5MB
- `smaller:1M` - Smaller than 1MB
- `-from:spam@example.com` - Exclude sender

---

## API Reference

### search_emails(query, max_results)
Search Gmail messages using Gmail query syntax.

**Parameters:**
- `query` (str, optional): Gmail search query. Default: `"is:unread"`
- `max_results` (int, optional): Maximum results to return. Default: `10`

**Returns:**
```json
{
  "status": "success",
  "count": 5,
  "query": "is:unread",
  "messages": [
    {
      "id": "abc123",
      "subject": "Meeting Tomorrow",
      "from": "REDACTED_EMAIL",
      "date": "Thu, 9 Oct 2025 14:30:00 +0000",
      "unread": true
    }
  ]
}
```

---

### read_email(message_id)
Read full email content including body, headers, and metadata.

**Parameters:**
- `message_id` (str, required): Gmail message ID

**Returns:**
```json
{
  "status": "success",
  "message_id": "abc123",
  "subject": "Meeting Tomorrow",
  "from": "Boss <REDACTED_EMAIL>",
  "to": "REDACTED_EMAIL",
  "date": "Thu, 9 Oct 2025 14:30:00 +0000",
  "body": "Full email body content here...",
  "labels": ["INBOX", "UNREAD", "IMPORTANT"]
}
```

---

### list_attachments(message_id) ⭐ NEW
List all attachments in an email with metadata.

**Parameters:**
- `message_id` (str, required): Gmail message ID

**Returns:**
```json
{
  "status": "success",
  "message_id": "abc123",
  "attachment_count": 2,
  "attachments": [
    {
      "filename": "document.pdf",
      "mimeType": "application/pdf",
      "size": 42826,
      "attachmentId": "ANGjdJ_12345"
    }
  ]
}
```

---

### download_attachment(message_id, attachment_id, filename, save_path) ⭐ NEW
Download email attachment to local storage.

**Parameters:**
- `message_id` (str, required): Gmail message ID
- `attachment_id` (str, required): Attachment ID from `list_attachments`
- `filename` (str, required): Filename to save as
- `save_path` (str, optional): Directory path. Default: `~/Downloads`

**Returns:**
```json
{
  "status": "success",
  "message_id": "abc123",
  "attachment_id": "ANGjdJ_12345",
  "filename": "document.pdf",
  "saved_to": "/home/user/Downloads/document.pdf",
  "size_bytes": 42826
}
```

---

### send_email(to, subject, body, cc, bcc)
Send an email with optional CC and BCC recipients.

**Parameters:**
- `to` (str, required): Recipient email address
- `subject` (str, required): Email subject line
- `body` (str, required): Email body content
- `cc` (str, optional): CC recipients (comma-separated)
- `bcc` (str, optional): BCC recipients (comma-separated)

**Returns:**
```json
{
  "status": "success",
  "message_id": "xyz789",
  "to": "recipient@example.com",
  "subject": "Meeting Tomorrow"
}
```

---

### mark_as_read(message_id) / mark_as_unread(message_id)
Mark email as read or unread.

**Parameters:**
- `message_id` (str, required): Gmail message ID

**Returns:**
```json
{
  "status": "success",
  "message_id": "abc123",
  "action": "marked_as_read"
}
```

---

### star_email(message_id, star)
Star or unstar an email.

**Parameters:**
- `message_id` (str, required): Gmail message ID
- `star` (bool, optional): `true` to star, `false` to unstar. Default: `true`

**Returns:**
```json
{
  "status": "success",
  "message_id": "abc123",
  "action": "starred"
}
```

---

### list_labels()
List all Gmail labels (folders).

**Parameters:** None

**Returns:**
```json
{
  "status": "success",
  "count": 26,
  "labels": [
    {
      "id": "INBOX",
      "name": "INBOX",
      "type": "system"
    },
    {
      "id": "Label_123",
      "name": "Work",
      "type": "user"
    }
  ]
}
```

---

### add_label(message_id, label_id) / remove_label(message_id, label_id)
Add or remove a label from an email.

**Parameters:**
- `message_id` (str, required): Gmail message ID
- `label_id` (str, required): Label ID from `list_labels`

**Returns:**
```json
{
  "status": "success",
  "message_id": "abc123",
  "label_id": "Label_123",
  "action": "label_added"
}
```

---

### create_draft(to, subject, body)
Create a draft email.

**Parameters:**
- `to` (str, required): Recipient email address
- `subject` (str, required): Email subject
- `body` (str, required): Email body content

**Returns:**
```json
{
  "status": "success",
  "draft_id": "r123456789",
  "message_id": "abc123",
  "to": "recipient@example.com",
  "subject": "Draft Subject"
}
```

---

### reply_to_email(message_id, body)
Reply to an email, maintaining thread context.

**Parameters:**
- `message_id` (str, required): Original message ID to reply to
- `body` (str, required): Reply content

**Returns:**
```json
{
  "status": "success",
  "message_id": "xyz789",
  "thread_id": "thread_abc123",
  "action": "replied"
}
```

---

### get_thread(thread_id)
Get all messages in an email conversation.

**Parameters:**
- `thread_id` (str, required): Gmail thread ID

**Returns:**
```json
{
  "status": "success",
  "thread_id": "thread_abc123",
  "message_count": 5,
  "messages": [
    {
