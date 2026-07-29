"""
Pipeline for transforming Bronze reviews into the Silver layer.
"""

import argparse

from config.datasets.paths import (get_bronze_reviews_path,
                                   get_silver_reviews_path)
from src.bronze_to_silver.reviews_transformer import ReviewsTransformer
from src.common.logger import get_logger
from src.common.spark_session import create_spark_session
from src.ingestion.reader import read_parquet
from src.ingestion.writer import write_parquet
from src.validation.reviews_validator import ReviewsValidator

logger = get_logger(__name__)


def run(dataset_name: str) -> None:
    """
    Executes the Bronze to Silver reviews pipeline.

    Args:
        dataset_name: Dataset to process.
    """

    spark = create_spark_session(
        app_name="Bronze to Silver Reviews Pipeline",
        local=False,
    )

    try:
        logger.info("Starting Bronze to Silver Reviews Pipeline")

        bronze_path = get_bronze_reviews_path(dataset_name)
        silver_path = get_silver_reviews_path(dataset_name)

        logger.info(f"Reading Bronze reviews from: {bronze_path}")

        reviews_df = read_parquet(
            spark=spark,
            path=bronze_path,
        )

        logger.info("Transforming Bronze reviews")

        silver_reviews_df = ReviewsTransformer(reviews_df).transform()

        logger.info("Validating Silver reviews")

        ReviewsValidator(silver_reviews_df).run()

        logger.info(f"Writing Silver reviews to: {silver_path}")

        write_parquet(
            df=silver_reviews_df,
            output_path=silver_path,
        )

        logger.info("Bronze to Silver Reviews Pipeline completed successfully.")

    finally:
        spark.stop()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Bronze to Silver Reviews Pipeline")

    parser.add_argument("--dataset", required=True, help="Dataset name to process")

    args = parser.parse_args()

    run(args.dataset)
