#!/usr/bin/env bash
# Installs the bolig-notifier as a per-user launchd agent on macOS.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
UV_BIN="$(command -v uv || true)"
PLIST_NAME="com.blg.bolig-notifier.plist"
DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

if [[ -z "$UV_BIN" ]]; then
  echo "error: 'uv' not found on PATH. Install it first: https://docs.astral.sh/uv/" >&2
  exit 1
fi

if [[ ! -f "$PROJECT_DIR/.env" ]]; then
  echo "warning: $PROJECT_DIR/.env not found — copy .env.example to .env and set DISCORD_WEBHOOK_URL first." >&2
fi

mkdir -p "$HOME/Library/LaunchAgents" "$PROJECT_DIR/data"

sed \
  -e "s|{{PROJECT_DIR}}|$PROJECT_DIR|g" \
  -e "s|{{UV_BIN}}|$UV_BIN|g" \
  "$SCRIPT_DIR/bolig-notifier.plist.template" > "$DEST"

launchctl unload "$DEST" 2>/dev/null || true
launchctl load "$DEST"

echo "Installed and started: $DEST"
echo "Logs: $PROJECT_DIR/data/notifier.log"
echo "Stop with: launchctl unload $DEST && rm $DEST"
