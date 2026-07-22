#!/bin/bash

set -e

PROJECT_ROOT=$(pwd)

source airflow-venv/bin/activate

export AIRFLOW_HOME=$HOME/airflow
export AIRFLOW__CORE__DAGS_FOLDER=$PROJECT_ROOT/dags
export PYTHONPATH=$PROJECT_ROOT

LOG_DIR="$PROJECT_ROOT/airflow-runtime/logs"
PID_DIR="$PROJECT_ROOT/airflow-runtime/pids"

mkdir -p "$LOG_DIR"
mkdir -p "$PID_DIR"

echo "Starting Airflow Scheduler..."

nohup airflow scheduler > "$LOG_DIR/scheduler.log" 2>&1 &
echo $! > "$PID_DIR/scheduler.pid"

sleep 8

echo "Starting Airflow Webserver..."

nohup airflow webserver --port 8080 > "$LOG_DIR/webserver.log" 2>&1 &
echo $! > "$PID_DIR/webserver.pid"

sleep 8

echo
echo "=================================="
echo "Airflow Started Successfully"
echo "=================================="
echo
echo "Scheduler PID : $(cat $PID_DIR/scheduler.pid)"
echo "Webserver PID : $(cat $PID_DIR/webserver.pid)"
