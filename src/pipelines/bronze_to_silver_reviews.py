"""
Pipeline for transforming Bronze reviews into the Silver layer.
"""

from src.common.logger import get_logger
from src.common.spark_session import create_spark_session
from src.ingestion.reader import read_parquet
from src.ingestion.writer import write_parquet
from src.bronze_to_silver.reviews_transformer import ReviewsTransformer
from src.validation.reviews_validator import ReviewsValidator
from config.datasets.paths import (
    get_bronze_reviews_path,
    get_silver_reviews_path,
)


logger = get_logger(__name__)


def run(dataset_name: str):
    """
    Executes the Bronze to Silver reviews pipeline.
    """

    spark = create_spark_session("Bronze To Silver Reviews")

    try:
        logger.info("Starting Bronze to Silver Reviews Pipeline")

        bronze_path = get_bronze_reviews_path(dataset_name)
        silver_path = get_silver_reviews_path(dataset_name)

        logger.info(f"Reading Bronze reviews from: {bronze_path}")

        reviews_df = read_json(spark, bronze_path)

        logger.info("Transforming Bronze reviews")

        silver_reviews_df = (
            ReviewsTransformer(reviews_df)
            .transform()
        )

        logger.info("Validating Silver reviews")

        ReviewsValidator(silver_reviews_df).run()

        logger.info(f"Writing Silver reviews to: {silver_path}")

        write_parquet(
            silver_reviews_df,
            silver_path
        )

        logger.info("Bronze to Silver Reviews Pipeline completed successfully.")

    finally:
        spark.stop()


if __name__ == "__main__":
    run("Sports_and_Outdoors")