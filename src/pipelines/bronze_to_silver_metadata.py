"""
Pipeline for transforming Bronze metadata into the Silver layer.
"""

from config.datasets.paths import (
    get_bronze_metadata_path,
    get_silver_metadata_path,
)

from src.common.spark_session import create_spark_session
from src.common.logger import get_logger

from src.ingestion.reader import read_json
from src.ingestion.writer import write_parquet

from src.bronze_to_silver.metadata_transformer import MetadataTransformer
from src.validation.metadata_validator import MetadataValidator


logger = get_logger(__name__)


def run() -> None:
    """
    Executes the Bronze to Silver metadata pipeline.
    """

    spark = create_spark_session(
        app_name="Bronze to Silver Metadata Pipeline"
    )


if __name__ == "__main__":
    run()