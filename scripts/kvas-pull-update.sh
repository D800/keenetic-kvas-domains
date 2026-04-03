#!/bin/sh
# Script for Keenetic (Entware/BusyBox) — pull aggregated domain list from GitHub and import into KVAS
# Only imports when the list has actually changed (compares SHA256 hash).
#
# Install: copy to /opt/etc/cron.daily/ or add to crontab
# Usage: ./kvas-pull-update.sh [--dry-run] [--force]
#
# Requires: curl (opkg install curl)

set -e

# CHANGE THIS to your GitHub username/org and repo name
REPO="YOUR_USER/keenetic-kvas-domains"
BRANCH="main"
FILE="domains/kvas-aggregated.txt"

URL="https://raw.githubusercontent.com/${REPO}/${BRANCH}/${FILE}"
TMP_FILE="/opt/tmp/kvas-aggregated.txt"
HASH_FILE="/opt/tmp/kvas-aggregated.sha256"
LOG_TAG="kvas-pull-update"

DRY_RUN=0
FORCE=0
for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=1 ;;
        --force)   FORCE=1 ;;
    esac
done

log() {
    logger -t "$LOG_TAG" "$1"
    echo "$1"
}

log "Downloading domain list from $URL"
if ! curl -sL "$URL" -o "$TMP_FILE"; then
    log "ERROR: Failed to download domain list"
    exit 1
fi

COUNT=$(grep -c . "$TMP_FILE" || true)
log "Downloaded $COUNT domains"

if [ "$COUNT" -lt 10 ]; then
    log "ERROR: Downloaded list too small ($COUNT domains), skipping import"
    rm -f "$TMP_FILE"
    exit 1
fi

# Compare hash with previous download
NEW_HASH=$(sha256sum "$TMP_FILE" | cut -d' ' -f1)
OLD_HASH=""
[ -f "$HASH_FILE" ] && OLD_HASH=$(cat "$HASH_FILE")

if [ "$FORCE" = "0" ] && [ "$NEW_HASH" = "$OLD_HASH" ]; then
    log "No changes detected (hash match), skipping import"
    rm -f "$TMP_FILE"
    exit 0
fi

log "Changes detected (old=${OLD_HASH:-none} new=${NEW_HASH})"

if [ "$DRY_RUN" = "1" ]; then
    log "DRY RUN: would import $COUNT domains into KVAS"
    rm -f "$TMP_FILE"
    exit 0
fi

# Clear current list and import new one
log "Clearing KVAS list and importing..."
kvas clear force
kvas import "$TMP_FILE"

# Save hash only after successful import
echo "$NEW_HASH" > "$HASH_FILE"

rm -f "$TMP_FILE"
log "KVAS update complete: $COUNT domains imported"
