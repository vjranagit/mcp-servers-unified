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
