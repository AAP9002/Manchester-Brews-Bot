#!/bin/bash

CIRCUITPY="/Volumes/CIRCUITPY"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
POLL_INTERVAL=1

latest_mtime() {
  find "$SCRIPT_DIR/code.py" \
       "$SCRIPT_DIR/components" \
       "$SCRIPT_DIR/screens" \
       "$SCRIPT_DIR/utils" \
       -type f 2>/dev/null \
  | xargs stat -f %m 2>/dev/null \
  | sort -n \
  | tail -1
}

deploy() {
  if [ ! -d "$CIRCUITPY" ]; then
    echo "[$(date +%H:%M:%S)] CIRCUITPY not mounted — skipping"
    return
  fi
  echo -n "[$(date +%H:%M:%S)] Deploying... "
  rsync -a --exclude='__pycache__/' \
    "$SCRIPT_DIR/code.py" \
    "$SCRIPT_DIR/components" \
    "$SCRIPT_DIR/screens" \
    "$SCRIPT_DIR/utils" \
    "$SCRIPT_DIR/images" \
    "$SCRIPT_DIR/lib" \
    "$CIRCUITPY/"
  echo "done"
}

echo "Watching code.py, components/, screens/, utils/ (polling every ${POLL_INTERVAL}s)"
echo "Ctrl+C to stop"
echo ""

deploy
last_mtime=$(latest_mtime)

while true; do
  sleep "$POLL_INTERVAL"
  current_mtime=$(latest_mtime)
  if [ "$current_mtime" != "$last_mtime" ]; then
    last_mtime=$current_mtime
    deploy
  fi
done
