#!/usr/bin/env bash

set -euo pipefail

BUCKET="${S3_BUCKET:?S3_BUCKET is not set}"
PREFIX="${S3_ARTIFACT_PREFIX:?S3_ARTIFACT_PREFIX is not set}"

ARTIFACT="build/amazon-review-analytics-platform.zip"

echo "=================================="
echo " Amazon Review Analytics Platform "
echo " Development Deployment"
echo "=================================="

echo

if ! command -v aws >/dev/null 2>&1; then
    echo "ERROR: AWS CLI not installed."
    exit 1
fi

if [ ! -f "$ARTIFACT" ]; then
    echo "ERROR: Deployment artifact not found."
    echo "Run ./scripts/build/package.sh first."
    exit 1
fi

echo "Uploading artifact..."

aws s3 cp \
    "$ARTIFACT" \
    "s3://$BUCKET/$PREFIX/"

echo
echo "Verifying upload..."

aws s3 ls \
    "s3://$BUCKET/$PREFIX/"

echo
echo "Deployment Successful"