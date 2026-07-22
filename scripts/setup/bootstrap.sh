#!/bin/bash

set -e

echo "======================================="
echo " Amazon Review Analytics Bootstrap"
echo "======================================="

if [ ! -d "airflow-venv" ]; then
    bash scripts/setup/setup_environment.sh
else
    echo "Virtual environment already exists."
fi

bash scripts/setup/install_dependencies.sh

bash scripts/setup/install_airflow.sh

bash scripts/setup/create_admin.sh

echo
echo "======================================="
echo " Bootstrap completed successfully!"
echo "======================================="
echo
echo "Next step:"
echo "bash scripts/setup/start_airflow.sh"
