#!/bin/bash

set -e

source airflow-venv/bin/activate

export AIRFLOW_HOME=$HOME/airflow

pip install apache-airflow==2.10.5

airflow db migrate

echo "Airflow installed."
