#!/bin/bash

set -e

source airflow-venv/bin/activate

export AIRFLOW_HOME=$HOME/airflow

PYTHON_VERSION=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-${PYTHON_VERSION}.txt"

pip install "apache-airflow==2.10.5" \
    --constraint "${CONSTRAINT_URL}"

airflow db migrate

echo "Airflow installed successfully."
