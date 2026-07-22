#!/bin/bash

set -e

PROJECT_ROOT=$(pwd)

PID_DIR="$PROJECT_ROOT/airflow-runtime/pids"

echo "Stopping Airflow..."

if [ -f "$PID_DIR/scheduler.pid" ]; then
    kill $(cat "$PID_DIR/scheduler.pid")
    rm "$PID_DIR/scheduler.pid"
fi

if [ -f "$PID_DIR/webserver.pid" ]; then
    kill $(cat "$PID_DIR/webserver.pid")
    rm "$PID_DIR/webserver.pid"
fi

echo "Airflow stopped."
