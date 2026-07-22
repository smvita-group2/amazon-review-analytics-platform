#!/bin/bash

set -e

source airflow-venv/bin/activate

export AIRFLOW_HOME=$HOME/airflow

echo "Create Airflow Admin User"

read -p "Username: " USERNAME
read -p "First Name: " FIRSTNAME
read -p "Last Name: " LASTNAME
read -p "Email: " EMAIL
read -s -p "Password: " PASSWORD
echo

airflow users create \
    --username "$USERNAME" \
    --firstname "$FIRSTNAME" \
    --lastname "$LASTNAME" \
    --role Admin \
    --email "$EMAIL" \
    --password "$PASSWORD"

echo "Admin user created successfully."
