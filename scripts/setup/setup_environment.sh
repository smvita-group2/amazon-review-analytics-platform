#!/bin/bash

set -e

echo "Creating virtual environment..."

python3 -m venv airflow-venv

source airflow-venv/bin/activate

pip install --upgrade pip

echo "Environment created."
