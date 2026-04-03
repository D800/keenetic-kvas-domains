#!/bin/bash
set -euo pipefail

# Deploy KVAS domain lists to both Keenetic routers
# Requires SSH access to routers (key-based auth)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOMAINS_DIR="$SCRIPT_DIR/../domains"

# Keenetic router IPs — adjust as needed
# Set your Keenetic router IPs here
ROUTERS=("192.168.1.1" "192.168.2.1")
REMOTE_USER="root"
KVAS_LIST_DIR="/opt/etc/kvas/domains"

for ROUTER in "${ROUTERS[@]}"; do
    echo "=== Deploying to $ROUTER ==="

    # Copy domain lists
    scp "$DOMAINS_DIR/proxy.txt" "$REMOTE_USER@$ROUTER:$KVAS_LIST_DIR/proxy.txt"
    scp "$DOMAINS_DIR/direct.txt" "$REMOTE_USER@$ROUTER:$KVAS_LIST_DIR/direct.txt"

    # Apply changes
    ssh "$REMOTE_USER@$ROUTER" "kvas update"

    echo "=== Done: $ROUTER ==="
done

echo "All routers updated."
