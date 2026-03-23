#!/bin/bash
# CEO Dashboard — start script
# Sources env vars from ~/.zshenv and launches the Node server

set -e

# Source environment variables (API keys, passwords)
if [ -f "$HOME/.zshenv" ]; then
  set -a
  source "$HOME/.zshenv"
  set +a
fi

# Defaults
export PORT="${PORT:-4200}"
export DASHBOARD_PASSWORD="${DASHBOARD_PASSWORD:-collectiveshift}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Starting CEO Dashboard on port $PORT..."
echo "   Dashboard dir: $SCRIPT_DIR"
echo "   Data dir:      $SCRIPT_DIR/../dashboard-data"

cd "$SCRIPT_DIR"
node server.js
