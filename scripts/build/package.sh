#!/usr/bin/env bash

set -euo pipefail

BUILD_DIR="build"
SHORT_SHA=$(git rev-parse --short HEAD)
ARTIFACT_NAME="amazon-review-analytics-platform-${SHORT_SHA}.zip"

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
Git Commit      : $(git rev-parse HEAD)
Git Short SHA   : ${SHORT_SHA}
Git Branch      : $(git rev-parse --abbrev-ref HEAD)

EOF

echo
echo "Copying project files..."

cp -R src "$BUILD_DIR/"
cp -R config "$BUILD_DIR/"
cp requirements.txt "$BUILD_DIR/"

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

    rm -f *.zip

    zip -rq "$ARTIFACT_NAME" .
)

echo
echo "=================================="
echo " Deployment Artifact Created"
echo "=================================="

echo
echo "Artifact:"
echo "$BUILD_DIR/$ARTIFACT_NAME"

echo
ls -lh "$BUILD_DIR"

echo
echo "Package Complete"