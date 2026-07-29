#!/usr/bin/env bash

set -euo pipefail

BUCKET="${S3_BUCKET:?S3_BUCKET is not set}"
PREFIX="${S3_ARTIFACT_PREFIX:?S3_ARTIFACT_PREFIX is not set}"

SHORT_SHA=$(git rev-parse --short HEAD)
ARTIFACT_NAME="amazon-review-analytics-platform-${SHORT_SHA}.zip"
ARTIFACT="build/${ARTIFACT_NAME}"

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
    exit 1
fi

echo "Uploading artifact..."
echo "Artifact : ${ARTIFACT_NAME}"
echo "Bucket   : ${BUCKET}"
echo "Prefix   : ${PREFIX}"

aws s3 cp \
    "$ARTIFACT" \
    "s3://${BUCKET}/${PREFIX}/${ARTIFACT_NAME}"

echo
echo "Upload completed."

echo
echo "Artifacts currently in S3:"
aws s3 ls "s3://${BUCKET}/${PREFIX}/"

echo
echo "Deployment Successful"