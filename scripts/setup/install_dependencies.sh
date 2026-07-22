#!/bin/bash

set -e

source airflow-venv/bin/activate

echo "Installing project dependencies..."

pip install -r requirements.txt

echo "Project dependencies installed."
