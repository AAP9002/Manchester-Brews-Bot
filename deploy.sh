#!/bin/bash

CIRCUITPY="/Volumes/CIRCUITPY"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

PATHS=(
  "$SCRIPT_DIR/code.py"
  "$SCRIPT_DIR/settings.toml"
  "$SCRIPT_DIR/components"
  "$SCRIPT_DIR/screens"
  "$SCRIPT_DIR/utils"
  "$SCRIPT_DIR/images"
  "$SCRIPT_DIR/lib"
)

if [ ! -d "$CIRCUITPY" ]; then
  echo "[$(date +%H:%M:%S)] CIRCUITPY not mounted — aborting"
  exit 1
fi

echo -n "[$(date +%H:%M:%S)] Deploying... "
rsync -a --delete --exclude='__pycache__/' \
  "${PATHS[@]}" \
  "$CIRCUITPY/"
echo "done"
