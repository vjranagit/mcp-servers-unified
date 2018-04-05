# Encrypted Environment Deployment System - Implementation Plan

**Project Name**: `llm-env-deployer`
**Location**: `/home/vjrana/work/mcp-servers/llm-env-deployer/`
**Status**: Planning Phase (Implement AFTER all MCP servers are functional)
**Created**: 2025-10-11

---

## 🎯 Project Goals

Create a **secure, encrypted, one-command deployment system** that:
1. Bundles ALL MCP configurations + API keys + credentials
2. Encrypts sensitive data (non-reversible by attackers)
3. Deploys complete LLM environment on any machine with one command
4. Includes ALL dotfiles (vimrc, bashrc, tmux, ranger configs)
5. Handles LLM server installations and configurations

---

## 🏗️ Architecture Overview

### Core Components

```
llm-env-deployer/
├── bin/
│   ├── deploy.sh              # Main deployment entry point
│   ├── encrypt-config         # Config encryption binary (compiled)
│   ├── decrypt-config         # Config decryption binary (compiled)
│   └── restore-env            # Environment restoration script
├── src/
│   ├── crypto/
│   │   ├── encrypt.c          # C implementation for speed & security
│   │   ├── decrypt.c
│   │   └── key_manager.c      # Secure key storage
│   ├── config/
│   │   ├── mcp_collector.py   # Collects all MCP configs
│   │   ├── dotfile_manager.py # Manages dotfiles
│   │   └── api_key_vault.py   # API key management
│   └── deploy/
│       ├── orchestrator.py    # Main deployment logic
│       ├── mcp_installer.py   # MCP server installation
│       └── dotfile_linker.py  # Symlink dotfiles
├── configs/
│   ├── encrypted_bundle.bin   # Encrypted config bundle
│   ├── bundle.manifest        # Bundle metadata
│   └── version.txt            # Version tracking
├── dotfiles/
│   ├── vimrc
│   ├── bashrc
│   ├── tmux.conf
│   └── ranger/
├── mcp-configs/
│   ├── claude.json.template
│   ├── mcp-config.json.template
│   └── servers/               # Per-server configs
├── tests/
│   ├── test_encryption.py
│   ├── test_deployment.py
│   └── test_restore.py
├── docs/
│   ├── USAGE.md
│   ├── SECURITY.md
│   └── DEVELOPMENT.md
├── README.md
├── Makefile                    # Build encrypted binaries
└── deploy.conf                 # Deployment settings
```

---

## 🔐 Encryption Strategy

### **Recommended Approach: Hybrid C + Python**

**Why C for encryption?**
- ✅ Compiled binary (harder to reverse engineer)
- ✅ Fast AES-256-GCM encryption
- ✅ Can use libsodium for industry-standard crypto
- ✅ Memory-safe implementation possible
- ✅ No plaintext keys in memory after use

**Why Python for orchestration?**
- ✅ Easy to maintain and extend
- ✅ Rich ecosystem (cryptography, paramiko, etc.)
- ✅ Can call compiled C binaries for crypto operations
- ✅ Better error handling and logging

### Encryption Flow

```
1. Collection Phase:
   ~/.claude.json → Extract configs
   ~/.mcp/config.json → Extract configs
   ~/.vimrc, ~/.bashrc, etc → Collect dotfiles
   API keys from env/configs → Secure vault

2. Encryption Phase:
   All configs → JSON bundle
   API keys → Separate encrypted vault
   Master password → Derives AES-256 key (PBKDF2)
   Bundle + Vault → encrypted_bundle.bin

3. Deployment Phase:
   encrypted_bundle.bin → Decrypt with master password
   Extract configs → Restore to ~/.claude.json, etc.
   Extract vault → Set API keys in configs
   Link dotfiles → Create symlinks
   Install MCP servers → Verify connectivity
```

### Security Features

1. **AES-256-GCM encryption** (authenticated encryption)
2. **PBKDF2 key derivation** (100,000+ iterations)
3. **Salt + IV per encryption** (prevent rainbow tables)
4. **HMAC verification** (detect tampering)
5. **Secure memory wiping** (clear keys after use)
6. **No plaintext on disk** (all sensitive data encrypted)

---

## 📋 What Gets Bundled

### 1. MCP Server Configurations
```bash
# Collected from:
~/.claude.json          # Main MCP config
~/.mcp/config.json      # Global MCP config
```

**Servers to bundle:**
- gmail (with OAuth tokens)
- zabbix (with URL + credentials)
- elk (with credentials)
- filesystem (paths)
- github (with PAT)
- playwright, context7, agent-browser
- n8n-workflows, n8n-docs (with API keys)
- firefly-iii (with PAT + base URL)

### 2. API Keys & Credentials (Encrypted Vault)
```
- GitHub Personal Access Token
- n8n API Key
- Firefly III PAT
- Zabbix credentials
- ELK credentials
- Gmail OAuth tokens
- Context7 API key
```

### 3. Dotfiles
```bash
~/.vimrc
~/.bashrc
~/.bashrc_tmux_vim_env
~/.tmux.conf
~/.config/ranger/rc.conf
~/.gitconfig
```

### 4. LLM Server Configurations
```
- n8n server config
- Firefly III server config
- Zabbix server config
- Any Docker Compose files for LLM services
```

---

## 🚀 Deployment Workflow

### One-Command Deployment

```bash
# Download and run
git clone https://github.com/yourusername/llm-env-deployer.git
cd llm-env-deployer
./deploy.sh --install

# Prompts for master password
# Decrypts and restores everything
# Installs missing dependencies
# Links dotfiles
# Verifies all MCP servers
```

### Manual Steps (if needed)

```bash
# 1. Install dependencies
./deploy.sh --install-deps

# 2. Decrypt configs only
./deploy.sh --decrypt-only

# 3. Restore configs without installing
./deploy.sh --restore --no-install

# 4. Verify installation
./deploy.sh --verify

# 5. Update encrypted bundle
./deploy.sh --update-bundle
```

---

## 🛠️ Implementation Phases

### Phase 1: Core Encryption (Week 1)
- [ ] Implement C encryption module (AES-256-GCM + libsodium)
- [ ] Implement key derivation (PBKDF2)
- [ ] Build and test encryption/decryption binaries
- [ ] Create Python wrapper for C binaries

### Phase 2: Configuration Collector (Week 2)
- [ ] Write MCP config collector (Python)
- [ ] Write dotfile collector (Python)
- [ ] Create API key vault manager
- [ ] Bundle generator (JSON → encrypted binary)

### Phase 3: Deployment Engine (Week 3)
- [ ] Write deployment orchestrator (Python)
- [ ] MCP server installer script
- [ ] Dotfile linker (symlinks)
- [ ] Environment verification system

### Phase 4: Testing & Hardening (Week 4)
- [ ] Unit tests for encryption
- [ ] Integration tests for deployment
- [ ] Test on clean VM/container
- [ ] Security audit
- [ ] Documentation

### Phase 5: Repository Setup (Week 5)
- [ ] Create GitHub repository
- [ ] Setup CI/CD for binary compilation
- [ ] Write comprehensive README
- [ ] Create usage examples
- [ ] Release v1.0.0

---

## 🔧 Technology Stack

### Core Technologies
- **C (libsodium)**: Encryption/decryption binaries
- **Python 3.10+**: Orchestration and deployment
- **Bash**: Wrapper scripts and automation
- **Make**: Build system for C binaries
- **Git**: Version control

### Python Dependencies
```python
cryptography==41.0.0      # Fallback encryption
pyyaml==6.0              # Config parsing
click==8.1.0             # CLI framework
rich==13.0.0             # Beautiful terminal output
paramiko==3.0.0          # SSH operations (if needed)
requests==2.31.0         # API calls for verification
```

### C Dependencies
```bash
libsodium-dev            # Crypto library
gcc / clang              # Compiler
make                     # Build tool
```

---

## 📦 Deliverables

### 1. Compiled Binaries
```
bin/encrypt-config       # Statically linked, ~200KB
bin/decrypt-config       # Statically linked, ~200KB
```

### 2. Deployment Package
```
llm-env-deployer-v1.0.tar.gz
├── deploy.sh (executable)
├── bin/ (compiled binaries)
├── configs/ (encrypted bundle)
└── README.md
```

### 3. Repository Structure
```
GitHub: yourusername/llm-env-deployer
- Main branch: stable releases
- Dev branch: active development
- Tags: v1.0.0, v1.1.0, etc.
```

---

## 🔗 Integration Points

### Home Directory Link
```bash
# Create symlink in home for easy access
