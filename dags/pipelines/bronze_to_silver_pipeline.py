from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

from dags.config.default_args import default_args
from dags.utils.s3_checks import check_bronze_data

DATASET_NAME = "Appliances"

with DAG(
    dag_id="bronze_to_silver_pipeline",
    description="Bronze to Silver ETL Pipeline",
    default_args=default_args,
    start_date=datetime(2026, 7, 1),
    schedule=None,
    catchup=False,
    tags=["amazon", "spark", "etl"],
) as dag:

    start = EmptyOperator(task_id="start")

    check_bronze = PythonOperator(
        task_id="check_bronze_data",
        python_callable=check_bronze_data,
        op_kwargs={
            "dataset_name": DATASET_NAME,
        },
    )

    bronze_to_silver_metadata = EmptyOperator(
        task_id="bronze_to_silver_metadata"
    )

    bronze_to_silver_reviews = EmptyOperator(
        task_id="bronze_to_silver_reviews"
    )

    validate_silver = EmptyOperator(
        task_id="validate_silver"
    )

    end = EmptyOperator(task_id="end")

    (
        start
        >> check_bronze
        >> bronze_to_silver_metadata
        >> bronze_to_silver_reviews
        >> validate_silver
        >> end
    )
