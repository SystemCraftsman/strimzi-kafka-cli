#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLUSTER_NAME="${KIND_CLUSTER_NAME:-strimzi-cli-test}"

log() { echo "==> $*"; }

check_prerequisites() {
    for cmd in kind kubectl; do
        if ! command -v "$cmd" &>/dev/null; then
            echo "Error: '$cmd' is required but not installed."
            exit 1
        fi
    done
}

create_kind_cluster() {
    if kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
        log "kind cluster '${CLUSTER_NAME}' already exists, skipping creation"
        return
    fi
    log "Creating kind cluster '${CLUSTER_NAME}'..."
    kind create cluster --name "$CLUSTER_NAME" --config "$SCRIPT_DIR/kind-config.yaml" --wait 120s
}

main() {
    check_prerequisites
    create_kind_cluster
    log "Kind cluster is ready!"
    log "Run 'make test-integration' to execute integration tests."
}

main "$@"
