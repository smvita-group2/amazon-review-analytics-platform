"""
Pipeline for creating the Silver Master dataset.
"""

import argparse

from config.datasets.paths import (
    get_silver_metadata_path,
    get_silver_reviews_path,
    get_silver_master_path,
)

from src.common.logger import get_logger
from src.common.spark_session import create_spark_session

from src.ingestion.reader import read_parquet
from src.ingestion.writer import write_parquet

from src.silver_to_gold.silver_master_transformer import (
    SilverMasterTransformer,
)

from src.validation.silver_master_validator import (
    SilverMasterValidator,
)


logger = get_logger(__name__)


def run(dataset_name: str) -> None:
    """
    Executes the Silver Master pipeline.

    Args:
        dataset_name: Dataset to process.
    """

    spark = create_spark_session(
        app_name="Silver Master Pipeline",
        local=False,
    )

    try:
        logger.info(
            "Starting Silver Master Pipeline"
        )

        reviews_path = get_silver_reviews_path(dataset_name)
        metadata_path = get_silver_metadata_path(dataset_name)
        master_path = get_silver_master_path(dataset_name)

        logger.info(
            f"Reading Silver reviews from: {reviews_path}"
        )

        reviews_df = read_parquet(
            spark=spark,
            path=reviews_path,
        )

        logger.info(
            f"Reading Silver metadata from: {metadata_path}"
        )

        metadata_df = read_parquet(
            spark=spark,
            path=metadata_path,
        )

        logger.info(
            "Creating Silver Master dataset..."
        )

        master_df = (
            SilverMasterTransformer(
                reviews_df=reviews_df,
                metadata_df=metadata_df,
            )
            .transform()
        )

        logger.info(
            "Validating Silver Master dataset..."
        )

        (
            SilverMasterValidator(master_df)
            .run()
        )

        logger.info(
            f"Writing Silver Master to: {master_path}"
        )

        write_parquet(
            df=master_df,
            output_path=master_path,
        )

        logger.info(
            "Silver Master Pipeline completed successfully."
        )

    finally:
        spark.stop()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Silver Master Pipeline"
    )

    parser.add_argument(
        "--dataset",
        required=True,
        help="Dataset name to process"
    )

    args = parser.parse_args()

    run(args.dataset)