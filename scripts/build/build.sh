#!/usr/bin/env bash

set -euo pipefail

echo "=================================="
echo " Amazon Review Analytics Platform "
echo " Build Validation Started"
echo "=================================="

# Detect Python
if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    echo "ERROR: Python is not installed."
    exit 1
fi

echo "Using Python: $PYTHON"
$PYTHON --version

echo "Checking Pip..."
$PYTHON -m pip --version

echo
echo "Checking Project Structure..."

required_dirs=(
    "src"
    "config"
    "tests"
)

for dir in "${required_dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "ERROR: Missing directory -> $dir"
        exit 1
    fi
done

if [ ! -f "requirements.txt" ]; then
    echo "ERROR: requirements.txt missing"
    exit 1
fi

echo "Project Structure Verified"

mkdir -p build

echo
echo "Build Validation Complete"