#!/bin/bash

# Kubernetes Deployment Script for MCP Servers
# Software House & Real Estate LLC - Production Deployment

set -euo pipefail

# Configuration
NAMESPACE="mcp-servers"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."

    if ! command -v kubectl &> /dev/null; then
        error "kubectl is not installed"
        exit 1
    fi

    if ! kubectl cluster-info &> /dev/null; then
        error "No Kubernetes cluster connection"
        exit 1
    fi

    log "Prerequisites check passed"
}

# Deploy namespace and basic resources
deploy_namespace() {
    log "Deploying namespace and basic resources..."

    kubectl apply -f "$SCRIPT_DIR/namespace.yaml"

    # Wait for namespace to be ready
    kubectl wait --for=condition=Active namespace/$NAMESPACE --timeout=60s

    log "Namespace deployed successfully"
}

# Deploy secrets (with warning about credential update)
deploy_secrets() {
    log "Deploying secrets..."

    warn "IMPORTANT: Update the secrets.yaml file with your actual API credentials before deploying to production!"
    warn "Current secrets contain placeholder values and must be replaced."

    kubectl apply -f "$SCRIPT_DIR/secrets.yaml"

    log "Secrets deployed (remember to update with real credentials)"
}

# Deploy persistent volumes
deploy_storage() {
    log "Deploying persistent volumes..."

    # Create directories on nodes (this is for local testing - use proper storage classes in production)
    if kubectl get nodes -o name | grep -q "kind-"; then
        info "Detected kind cluster - creating local directories"
        docker exec kind-control-plane mkdir -p /mnt/data/mcp-postgres /mnt/data/mcp-redis /mnt/data/mcp-logs /mnt/data/mcp-monitoring
    fi

    kubectl apply -f "$SCRIPT_DIR/persistent-volumes.yaml"

    # Wait for PVCs to be bound
    kubectl wait --for=condition=Bound pvc --all -n $NAMESPACE --timeout=120s

    log "Storage deployed successfully"
}

# Deploy configmaps
deploy_config() {
    log "Deploying configuration..."

    kubectl apply -f "$SCRIPT_DIR/configmap.yaml"

    log "Configuration deployed successfully"
}

# Deploy infrastructure (databases, monitoring)
deploy_infrastructure() {
    log "Deploying infrastructure services..."

    kubectl apply -f "$SCRIPT_DIR/deployments/infrastructure.yaml"

    # Wait for infrastructure to be ready
    log "Waiting for infrastructure services to be ready..."
    kubectl wait --for=condition=available deployment/postgres -n $NAMESPACE --timeout=300s
    kubectl wait --for=condition=available deployment/redis -n $NAMESPACE --timeout=300s
    kubectl wait --for=condition=available deployment/prometheus -n $NAMESPACE --timeout=300s
    kubectl wait --for=condition=available deployment/grafana -n $NAMESPACE --timeout=300s

    log "Infrastructure deployed successfully"
}

# Deploy MCP servers
deploy_mcp_servers() {
    log "Deploying MCP servers..."

    # Deploy development category servers
    kubectl apply -f "$SCRIPT_DIR/deployments/github-mcp.yaml"

    # Wait for deployments to be ready
    log "Waiting for MCP servers to be ready..."
    kubectl wait --for=condition=available deployment/github-mcp -n $NAMESPACE --timeout=300s

    log "MCP servers deployed successfully"
}

# Create service account and RBAC
deploy_rbac() {
    log "Deploying RBAC configuration..."

    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  name: mcp-servers-sa
  namespace: $NAMESPACE
  labels:
    app: mcp-servers

---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: $NAMESPACE
  name: mcp-servers-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps", "secrets"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "watch"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: mcp-servers-rolebinding
  namespace: $NAMESPACE
subjects:
- kind: ServiceAccount
  name: mcp-servers-sa
  namespace: $NAMESPACE
roleRef:
  kind: Role
  name: mcp-servers-role
  apiGroup: rbac.authorization.k8s.io
EOF

    log "RBAC configuration deployed"
}

# Show deployment status
show_status() {
    log "Checking deployment status..."
    echo ""

    info "Namespace status:"
    kubectl get ns $NAMESPACE

    echo ""
    info "Pods status:"
    kubectl get pods -n $NAMESPACE -o wide

    echo ""
    info "Services status:"
    kubectl get svc -n $NAMESPACE

    echo ""
    info "Persistent Volume Claims:"
    kubectl get pvc -n $NAMESPACE

    echo ""
    info "Ingress status:"
    kubectl get ingress -n $NAMESPACE

    echo ""
    info "HPA status:"
    kubectl get hpa -n $NAMESPACE

    echo ""
}

# Show access information
show_access_info() {
    log "Access Information:"
    echo "=================="

    # Get node IPs
    NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}')
    if [[ -z "$NODE_IP" ]]; then
        NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
    fi

    echo "Cluster Node IP: $NODE_IP"
    echo ""

    # Service URLs
    echo "Service Access:"
    echo "  - Grafana: http://$NODE_IP:$(kubectl get svc grafana -n $NAMESPACE -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null || echo '30000')"
    echo "  - Prometheus: http://$NODE_IP:$(kubectl get svc prometheus -n $NAMESPACE -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null || echo '30001')"
    echo ""

    # Port forwarding commands
    echo "Port Forward Commands:"
    echo "  kubectl port-forward -n $NAMESPACE svc/grafana 3000:3000"
    echo "  kubectl port-forward -n $NAMESPACE svc/prometheus 9090:9090"
    echo "  kubectl port-forward -n $NAMESPACE svc/github-mcp 3001:3001"
    echo ""

    # Logs commands
    echo "Logs Commands:"
    echo "  kubectl logs -n $NAMESPACE deployment/github-mcp -f"
    echo "  kubectl logs -n $NAMESPACE deployment/postgres -f"
    echo ""
}

# Cleanup function
cleanup() {
    log "Cleaning up MCP servers deployment..."

    kubectl delete namespace $NAMESPACE --ignore-not-found=true

    # Clean up persistent volumes (be careful in production!)
    if [[ "${1:-}" == "--purge-data" ]]; then
        warn "Purging persistent volume data..."
        kubectl delete pv mcp-postgres-pv mcp-redis-pv mcp-logs-pv mcp-monitoring-pv --ignore-not-found=true
    fi

    log "Cleanup completed"
}

# Main deployment function
deploy_all() {
    log "Starting comprehensive MCP servers deployment..."
    log "=============================================="

    check_prerequisites
    deploy_rbac
    deploy_namespace
    deploy_storage
    deploy_config
    deploy_secrets
    deploy_infrastructure
    deploy_mcp_servers

    log "Deployment completed successfully!"
    echo ""

    show_status
    show_access_info

    echo ""
    warn "Next steps:"
    echo "1. Update secrets with real API credentials: kubectl edit secret mcp-servers-secrets -n $NAMESPACE"
    echo "2. Configure domain name and TLS certificates for production"
    echo "3. Scale deployments based on your needs"
    echo "4. Set up monitoring alerts and dashboards"
    echo ""
}

# Command handling
case "${1:-deploy}" in
    deploy)
        deploy_all
        ;;
    status)
        show_status
        show_access_info
        ;;
    cleanup)
        cleanup "${2:-}"
        ;;
    namespace)
        deploy_namespace
        ;;
    storage)
        deploy_storage
        ;;
    config)
        deploy_config
        ;;
    secrets)
        deploy_secrets
        ;;
    infrastructure)
        deploy_infrastructure
        ;;
    mcp-servers)
        deploy_mcp_servers
        ;;
    *)
        cat << EOF
