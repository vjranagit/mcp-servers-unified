#!/bin/bash
# MCP GitHub Upload Orchestrator
# Processes all projects: scan, git init, create GitHub repos (via MCP), push
# Security-first approach with automatic quarantine

set -euo pipefail

# Configuration
PROJECTS_ROOT="/home/vjrana/work"
PROJECTS_LIST="/tmp/mcp_all_projects.txt"
QUARANTINE_BASE="/var/mcp_quarantine"
LOG="/var/log/mcp_repo_upload.log"
SUMMARY="/var/log/mcp_repo_upload_summary.json"
SECRET_SCANNER="/home/vjrana/work/mcp_secret_scanner.sh"
GITHUB_OWNER="vjranagit"
TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")

# Statistics
TOTAL_PROJECTS=0
REPOS_CREATED=0
REPOS_PUSHED=0
SECRETS_QUARANTINED=0
SKIPPED_PROJECTS=0
FAILED_PROJECTS=0

# Color codes
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    echo -e "[$(date -u +"%Y-%m-%d %H:%M:%S UTC")] [$level] $message" | tee -a "$LOG"
}

# Initialize summary JSON
init_summary() {
    cat > "$SUMMARY" <<EOF
{
  "timestamp": "$TIMESTAMP",
  "projects": []
}
EOF
}

# Add project to summary
add_to_summary() {
    local project_json="$1"
    local temp_file=$(mktemp)

    jq ".projects += [$project_json]" "$SUMMARY" > "$temp_file"
    mv "$temp_file" "$SUMMARY"
}

# Sanitize project name for GitHub
sanitize_repo_name() {
    local name="$1"
    # Replace invalid chars with dash, remove leading/trailing dashes
    echo "$name" | sed 's/[^a-zA-Z0-9._-]/-/g' | sed 's/^-//;s/-$//'
}

# Create .gitignore template
create_gitignore() {
    local project_dir="$1"

    if [ -f "$project_dir/.gitignore" ]; then
        log "INFO" "  .gitignore already exists, appending security patterns"
        cat >> "$project_dir/.gitignore" <<'EOF'

# MCP Security Patterns
*.pem
*.key
*.p12
*.jks
*.pfx
id_rsa
id_dsa
.env
.env.*
env.local
credentials
*passwd*
*password*
*.bak
*.backup
node_modules/
__pycache__/
.venv/
venv/
.terraform/
terraform.tfstate*
*.tfvars
*.log
*.sqlite3
*.db
EOF
    else
        cat > "$project_dir/.gitignore" <<'EOF'
# MCP Security Patterns
*.pem
*.key
*.p12
*.jks
*.pfx
id_rsa
id_dsa
.env
.env.*
env.local
credentials
*passwd*
*password*
*.bak
*.backup

# Build artifacts
node_modules/
__pycache__/
.venv/
venv/
dist/
build/
*.egg-info/

# Terraform
.terraform/
terraform.tfstate*
*.tfvars

# Logs and databases
*.log
*.sqlite3
*.db
EOF
    fi
}

# Add secrets to gitignore (don't move files)
ignore_secrets() {
    local project_dir="$1"
    local project_name="$2"
    local secrets_log="$project_dir/.mcp_secrets_detected.log"

    if [ ! -f "$secrets_log" ]; then
        return 0
    fi

    log "WARN" "  Adding secrets to .gitignore: $project_name"

    # Create secrets report (no file movement)
    local report_file="$project_dir/.mcp_secrets_report.txt"
    cat > "$report_file" <<EOF
MCP Secret Detection Report
============================
Project: $project_name
Date: $TIMESTAMP
Files with Secrets: $(cat "$secrets_log" | wc -l)

⚠️  WARNING: The following files contain potential secrets and have been added to .gitignore
They will NOT be committed to GitHub. Please review and migrate secrets to environment variables.

Details:
$(cat "$secrets_log")

Next Steps:
1. Review each file for actual secrets vs false positives
2. For real secrets:
   - Move to secure vault (HashiCorp Vault, AWS Secrets Manager)
   - Update project to reference via environment variables
   - Keep files in .gitignore
3. For false positives:
   - Remove from .gitignore
   - Commit the file
EOF

    # Add each file to gitignore
    while IFS='|' read -r file_path reason details; do
        if [ -f "$file_path" ]; then
            local rel_path=$(realpath --relative-to="$project_dir" "$file_path")

            # Add to gitignore
            echo "$rel_path" >> "$project_dir/.gitignore"

            ((SECRETS_QUARANTINED++))
            log "WARN" "    Added to .gitignore: $rel_path (reason: $reason)"
        fi
    done < "$secrets_log"

    # Add the secrets report to gitignore too (contains sensitive paths)
    echo ".mcp_secrets_report.txt" >> "$project_dir/.gitignore"
    echo ".mcp_secrets_detected.log" >> "$project_dir/.gitignore"

    log "INFO" "  Secrets report: $report_file"
    log "INFO" "  Files remain in place - added to .gitignore only"
}

# Process a single project
process_project() {
    local project_path="$1"
    local project_name=$(basename "$project_path")
    local repo_name=$(sanitize_repo_name "$project_name")

    ((TOTAL_PROJECTS++))

    log "INFO" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log "INFO" "Processing [$TOTAL_PROJECTS/69]: $project_name"
    log "INFO" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    local git_init=false
    local repo_created=false
    local pushed=false
    local secrets_found=false
    local notes=""
    local github_url=""

    # Check if directory exists and is readable
    if [ ! -d "$project_path" ] || [ ! -r "$project_path" ]; then
        log "ERROR" "  Cannot access directory: $project_path"
        ((FAILED_PROJECTS++))
        notes="Directory not accessible"
        add_to_summary "$(jq -n --arg name "$project_name" --arg path "$project_path" --arg notes "$notes" \
            '{name: $name, path: $path, git_init: false, repo_created: false, pushed: false, secrets_found: [], notes: $notes}')"
        return
    fi

    # Skip if directory is too large (>150GB - education/projects are borderline)
    local dir_size=$(du -sm "$project_path" 2>/dev/null | cut -f1)
    if [ "$dir_size" -gt 150000 ]; then
        log "WARN" "  Skipping: Directory too large (${dir_size}MB > 150GB limit)"
        ((SKIPPED_PROJECTS++))
        notes="Too large: ${dir_size}MB"
        add_to_summary "$(jq -n --arg name "$project_name" --arg path "$project_path" --arg notes "$notes" \
            '{name: $name, path: $path, git_init: false, repo_created: false, pushed: false, secrets_found: [], notes: $notes}')"
        return
    fi

    # Step 1: Secret Scanning
    log "INFO" "  [1/5] Scanning for secrets..."
    if bash "$SECRET_SCANNER" "$project_path"; then
        log "INFO" "  ✅ No secrets detected"
    else
        log "WARN" "  ⚠️  Secrets detected - adding to .gitignore..."
        secrets_found=true
        ignore_secrets "$project_path" "$project_name"
    fi

    # Step 2: Git initialization
    log "INFO" "  [2/5] Checking git repository..."
    if [ -d "$project_path/.git" ]; then
        log "INFO" "  Git repository exists"
        cd "$project_path"

        # Check for uncommitted changes
        if ! git diff-index --quiet HEAD -- 2>/dev/null; then
            log "INFO" "  Committing pending changes..."
            git add -A
            git commit -m "mcp: snapshot before GitHub sync - $TIMESTAMP" --allow-empty
        fi
    else
        log "INFO" "  Initializing git repository..."
        cd "$project_path"
        git init -b main
        create_gitignore "$project_path"
        git add -A
        git commit -m "chore: initial commit (MCP automated import - $TIMESTAMP)"
        git_init=true
    fi

    # Step 3: Create GitHub repository via MCP
    log "INFO" "  [3/5] Creating GitHub repository..."

    # Check if repo already exists
    local existing_repo=$(python3 -c "
import sys
try:
    # This would need MCP client integration
    # For now, we'll create a marker file for Python MCP script to process
    print('needs_creation')
except:
    print('error')
" 2>/dev/null || echo "needs_creation")

    # Create marker file for Python MCP processing
    cat > "/tmp/mcp_repo_create_${project_name}.json" <<EOF
{
  "project_name": "$project_name",
  "repo_name": "$repo_name",
  "project_path": "$project_path",
  "owner": "$GITHUB_OWNER",
  "description": "Imported from MCP server on $TIMESTAMP",
  "private": true
}
EOF

    log "INFO" "  📝 Created repo request: /tmp/mcp_repo_create_${project_name}.json"
    log "INFO" "  ⏳ Waiting for Python MCP script to create repository..."

