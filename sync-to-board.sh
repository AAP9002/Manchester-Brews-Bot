#!/bin/bash

# Sync CircuitPython project to CIRCUITPY volume
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
CIRCUITPY_DIR="/Volumes/CIRCUITPY"

echo "Building/Validating Python files..."

# Check syntax of all Python files
find "$PROJECT_DIR" -name "*.py" -not -path "*/\.*" -not -path "*/.git/*" | while read -r file; do
    python3 -m py_compile "$file" 2>&1
    if [ $? -ne 0 ]; then
        echo "Syntax error in $file"
        exit 1
    fi
done

echo "Build successful!"
echo "Syncing to CIRCUITPY volume..."

# Check if CIRCUITPY is mounted
if [ ! -d "$CIRCUITPY_DIR" ]; then
    echo "Error: CIRCUITPY volume not found. Make sure the board is connected."
    exit 1
fi

# Sync main files
rsync -av --progress \
    --exclude='.git' \
    --exclude='.gitignore' \
    --exclude='boot_out.txt' \
    --exclude='bruno' \
    --exclude='sync-to-board.sh' \
    --exclude='.*' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.DS_Store' \
    "$PROJECT_DIR/" "$CIRCUITPY_DIR/"

echo "Sync complete!"
