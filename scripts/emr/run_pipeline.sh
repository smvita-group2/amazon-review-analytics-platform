#!/bin/bash
set -Eeuo pipefail

#############################################
# Amazon Review Analytics Platform
# EMR Deployment Pipeline
#############################################

readonly BUCKET="amazon-review-analytics-group-2"
readonly ARTIFACT_PREFIX="artifacts/develop"
readonly WORKDIR="/home/hadoop/app"
readonly MARKER_FILE=".deps_installed"

readonly DATASETS=(
    "Musical_Instruments"
    "Video_Games"
    "Sports_and_Outdoors"
    "Appliances"
)

#############################################
# Logging
#############################################

log() {
    echo "[$(date '+%F %T')] $1"
}

#############################################
# Download latest artifact
#############################################

prepare_environment() {

    mkdir -p "$WORKDIR"
    cd "$WORKDIR"

    log "Finding latest artifact..."

    LATEST_ARTIFACT=$(
        aws s3 ls s3://$BUCKET/$ARTIFACT_PREFIX/ \
        | awk '{print $4}' \
        | grep '\.zip$' \
        | sort \
        | tail -1
    )

    if [[ -z "$LATEST_ARTIFACT" ]]; then
        echo "No deployment artifact found."
        exit 1
    fi

    log "Downloading $LATEST_ARTIFACT"

    aws s3 cp \
        "s3://$BUCKET/$ARTIFACT_PREFIX/$LATEST_ARTIFACT" \
        .

    log "Extracting artifact..."

    unzip -oq "$LATEST_ARTIFACT"
}

#############################################
# Install dependencies once
#############################################

install_dependencies() {

    if [[ -f "$MARKER_FILE" ]]; then
        log "Dependencies already installed."
        return
    fi

    log "Installing Python dependencies..."

    python3 -m pip install --upgrade pip

    pip3 install \
        --no-cache-dir \
        -r requirements.txt

    touch "$MARKER_FILE"

    log "Dependencies installed."
}

#############################################
# Run one dataset
#############################################

run_dataset() {

    DATASET="$1"

    log "======================================"
    log "Processing Dataset : $DATASET"
    log "======================================"

    spark-submit \
        src/pipelines/bronze_to_silver_metadata.py \
        --dataset "$DATASET"

    spark-submit \
        src/pipelines/bronze_to_silver_reviews.py \
        --dataset "$DATASET"

    spark-submit \
        src/pipelines/silver_master_pipeline.py \
        --dataset "$DATASET"

    spark-submit \
        src/pipelines/gold_visualization_pipeline.py \
        --dataset "$DATASET"

    log "Finished Dataset : $DATASET"
}

#############################################
# Main
#############################################

main() {

    prepare_environment

    install_dependencies

    if [[ $# -eq 0 || "$1" == "all" ]]; then

        log "Running ALL datasets..."

        for dataset in "${DATASETS[@]}"
        do
            run_dataset "$dataset"
        done

    else

        run_dataset "$1"

    fi

    log "======================================"
    log "Pipeline Completed Successfully"
    log "======================================"
}

main "$@"