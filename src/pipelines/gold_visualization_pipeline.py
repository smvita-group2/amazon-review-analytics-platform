"""
Pipeline for transforming Silver Master into the Gold Visualization layer.
"""

import argparse

from config.datasets.paths import (
    get_gold_visualization_path,
    get_silver_master_path,
)

from src.common.logger import get_logger
from src.common.spark_session import create_spark_session

from src.ingestion.reader import read_parquet
from src.ingestion.writer import write_parquet

from src.silver_to_gold.gold_visualization_transformer import (
    GoldVisualizationTransformer,
)

from src.validation.gold_visualization_validator import (
    GoldVisualizationValidator,
)


logger = get_logger(__name__)


def run(dataset_name: str) -> None:
    """
    Executes the Silver Master to Gold Visualization pipeline.

    Args:
        dataset_name: Dataset to process.
    """

    spark = create_spark_session(
        app_name="Silver to Gold Visualization Pipeline",
        local=False,
    )

    try:
        logger.info(
            "Starting Silver to Gold Visualization Pipeline"
        )

        silver_master_path = get_silver_master_path(dataset_name)
        gold_visualization_path = get_gold_visualization_path(dataset_name)

        logger.info(
            f"Reading Silver Master from: {silver_master_path}"
        )

        df = read_parquet(
            spark=spark,
            path=silver_master_path,
        )

        logger.info(
            "Transforming Gold Visualization dataset..."
        )

        df = (
            GoldVisualizationTransformer(df)
            .transform()
        )

        logger.info(
            "Validating Gold Visualization dataset..."
        )

        (
            GoldVisualizationValidator(df)
            .run()
        )

        logger.info(
            f"Writing Gold Visualization to: {gold_visualization_path}"
        )

        write_parquet(
            df=df,
            output_path=gold_visualization_path,
        )

        logger.info(
            "Silver to Gold Visualization Pipeline completed successfully."
        )

    finally:
        spark.stop()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Silver to Gold Visualization Pipeline"
    )

    parser.add_argument(
        "--dataset",
        required=True,
        help="Dataset name to process",
    )

    args = parser.parse_args()

    run(args.dataset)