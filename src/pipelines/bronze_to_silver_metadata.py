"""
Pipeline for transforming Bronze metadata into the Silver layer.
"""

from config.datasets.paths import (
    get_bronze_metadata_path,
    get_silver_metadata_path,
)

from src.common.logger import get_logger
from src.common.spark_session import create_spark_session

from src.ingestion.reader import read_json
from src.ingestion.writer import write_parquet

from src.bronze_to_silver.metadata_transformer import MetadataTransformer
from src.validation.metadata_validator import MetadataValidator


logger = get_logger(__name__)


def run(dataset_name: str) -> None:
    """
    Executes the Bronze to Silver metadata pipeline.

    Args:
        dataset_name: Dataset to process.
    """

    spark = create_spark_session(
        app_name="Bronze to Silver Metadata Pipeline",
        local=False,
    )

    try:
        logger.info(
            "Starting Bronze to Silver Metadata Pipeline"
        )

        bronze_path = get_bronze_metadata_path(dataset_name)
        silver_path = get_silver_metadata_path(dataset_name)

        logger.info(
            f"Reading Bronze metadata from: {bronze_path}"
        )

        df = read_json(
            spark=spark,
            path=bronze_path,
        )

        logger.info("Transforming metadata...")

        df = (
            MetadataTransformer(df)
            .transform()
        )

        logger.info("Validating metadata...")

        (
            MetadataValidator(df)
            .run()
        )

        logger.info(
            f"Writing Silver metadata to: {silver_path}"
        )

        write_parquet(
            df=df,
            output_path=silver_path,
        )

        logger.info(
            "Bronze to Silver Metadata Pipeline completed successfully."
        )

    finally:
        spark.stop()


if __name__ == "__main__":
    run("Sports_and_Outdoors")