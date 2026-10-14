#!/usr/bin/env bash
# Installs the bolig-notifier as a per-user systemd timer on Linux.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
UV_BIN="$(command -v uv || true)"
UNIT_DIR="$HOME/.config/systemd/user"

if [[ -z "$UV_BIN" ]]; then
  echo "error: 'uv' not found on PATH. Install it first: https://docs.astral.sh/uv/" >&2
  exit 1
fi

if [[ ! -f "$PROJECT_DIR/.env" ]]; then
  echo "warning: $PROJECT_DIR/.env not found — copy .env.example to .env and set DISCORD_WEBHOOK_URL first." >&2
fi

mkdir -p "$UNIT_DIR" "$PROJECT_DIR/data"

sed \
  -e "s|{{PROJECT_DIR}}|$PROJECT_DIR|g" \
  -e "s|{{UV_BIN}}|$UV_BIN|g" \
  "$SCRIPT_DIR/bolig-notifier.service.template" > "$UNIT_DIR/bolig-notifier.service"

cp "$SCRIPT_DIR/bolig-notifier.timer" "$UNIT_DIR/bolig-notifier.timer"

systemctl --user daemon-reload
systemctl --user enable --now bolig-notifier.timer

echo "Installed and started bolig-notifier.timer"
echo "Status:  systemctl --user status bolig-notifier.timer"
echo "Logs:    journalctl --user -u bolig-notifier.service -f"
echo "Stop:    systemctl --user disable --now bolig-notifier.timer"
echo
echo "On a headless server, also run this once so the timer keeps running"
echo "without an active login session (survives reboot too):"
echo "  sudo loginctl enable-linger \$USER"
