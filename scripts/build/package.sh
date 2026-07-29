#!/usr/bin/env bash

set -euo pipefail

ARTIFACT_NAME="amazon-review-analytics-platform.zip"
BUILD_DIR="build"

echo "=================================="
echo " Amazon Review Analytics Platform "
echo " Packaging Deployment Artifact"
echo "=================================="

echo
echo "Cleaning previous build..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

echo
echo "Generating build metadata..."

cat > "$BUILD_DIR/build-info.txt" <<EOF
====================================
Amazon Review Analytics Platform
====================================

Build Time (UTC): $(date -u)
Git Commit      : $(git rev-parse --short HEAD)
Git Branch      : $(git rev-parse --abbrev-ref HEAD)

EOF

echo
echo "Copying project files..."

cp -R src "$BUILD_DIR/"
cp -R config "$BUILD_DIR/"

cp requirements.txt "$BUILD_DIR/"

# Copy README only if it exists
if [ -f README.md ]; then
    cp README.md "$BUILD_DIR/"
fi

echo
echo "Removing unnecessary files..."

find "$BUILD_DIR" -name "__pycache__" -type d -exec rm -rf {} +
find "$BUILD_DIR" -name "*.pyc" -delete
find "$BUILD_DIR" -name ".DS_Store" -delete

echo
echo "Creating deployment artifact..."

(
    cd "$BUILD_DIR"

    rm -f "$ARTIFACT_NAME"

    zip -rq "$ARTIFACT_NAME" .
)

echo
echo "=================================="
echo " Deployment Artifact Created"
echo "=================================="

echo
echo "Artifact Location:"
echo "$BUILD_DIR/$ARTIFACT_NAME"

echo
echo "Build Directory Contents:"
ls -lh "$BUILD_DIR"

echo
echo "Package Complete"