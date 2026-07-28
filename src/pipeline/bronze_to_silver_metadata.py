from config.datasets.paths import (
    BRONZE_METADATA_PATH,
    SILVER_METADATA_PATH,
)

from src.common.spark_session import create_spark_session
from src.ingestion.reader import read_parquet
from src.ingestion.writer import write_parquet
from src.transformation.metadata_transformer import MetadataTransformer


def main():
    """
    Bronze Metadata → Silver Metadata Pipeline
    """

    spark = create_spark_session()

    try:
        print("Reading Bronze Metadata...")

        metadata_df = read_parquet(
            spark,
            BRONZE_METADATA_PATH,
        )

        print("Applying Metadata Transformations...")

        transformer = MetadataTransformer()

        silver_metadata_df = transformer.transform(metadata_df)

        print("Writing Silver Metadata...")

        write_parquet(
            silver_metadata_df,
            SILVER_METADATA_PATH,
        )

        print("Silver Metadata Successfully Created.")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()