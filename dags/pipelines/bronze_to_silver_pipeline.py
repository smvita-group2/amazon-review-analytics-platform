from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

from dags.config.default_args import default_args


PROJECT_ROOT = "/home/hadoop/amazon-review-analytics-platform"
JAVA_HOME = "/usr/lib/jvm/java-17-amazon-corretto.x86_64"

DEFAULT_DATASET = "Appliances"


with DAG(
    dag_id="bronze_to_silver_pipeline",
    description="Bronze to Silver ETL Pipeline",
    default_args=default_args,
    start_date=datetime(2026, 7, 1),
    schedule=None,
    catchup=False,
    tags=["amazon", "spark", "etl"],
) as dag:

    start = EmptyOperator(
        task_id="start"
    )

    #
    # TEMPORARILY DISABLED
    # We'll add the S3 validation back after verifying
    # dataset parameterization works correctly.
    #
    check_bronze = EmptyOperator(
        task_id="check_bronze_data"
    )

    bronze_to_silver_metadata = BashOperator(
        task_id="bronze_to_silver_metadata",
        bash_command=f"""
        cd {PROJECT_ROOT}

        export JAVA_HOME={JAVA_HOME}
        export PATH=$JAVA_HOME/bin:$PATH
        export PYTHONPATH={PROJECT_ROOT}

        DATASET="{{{{ dag_run.conf.get('dataset', '{DEFAULT_DATASET}') if dag_run else '{DEFAULT_DATASET}' }}}}"

        echo "========== DATASET =========="
        echo $DATASET

        echo "========== JAVA VERSION =========="
        java -version

        echo "========== PYTHON VERSION =========="
        python --version

        echo "========== SPARK VERSION =========="
        /usr/lib/spark/bin/spark-submit --version

        /usr/lib/spark/bin/spark-submit \
        --conf spark.yarn.appMasterEnv.PYTHONPATH=$PYTHONPATH \
        --conf spark.executorEnv.PYTHONPATH=$PYTHONPATH \
        src/pipelines/bronze_to_silver_metadata.py \
        --dataset "$DATASET"
        """,
    )

    bronze_to_silver_reviews = BashOperator(
        task_id="bronze_to_silver_reviews",
        bash_command=f"""
        cd {PROJECT_ROOT}

        export JAVA_HOME={JAVA_HOME}
        export PATH=$JAVA_HOME/bin:$PATH
        export PYTHONPATH={PROJECT_ROOT}

        DATASET="{{{{ dag_run.conf.get('dataset', '{DEFAULT_DATASET}') if dag_run else '{DEFAULT_DATASET}' }}}}"

        echo "========== DATASET =========="
        echo $DATASET

        echo "========== JAVA VERSION =========="
        java -version

        echo "========== PYTHON VERSION =========="
        python --version

        echo "========== SPARK VERSION =========="
        /usr/lib/spark/bin/spark-submit --version

        /usr/lib/spark/bin/spark-submit \
        --conf spark.yarn.appMaster
