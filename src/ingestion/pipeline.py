from config.datasets.paths import (
    RAW_REVIEWS_PATH,
    RAW_METADATA_PATH,
    BRONZE_REVIEWS_PATH,
    BRONZE_METADATA_PATH,
    SAMPLE_REVIEWS_PATH,
    SAMPLE_METADATA_PATH,
)

from src.common.spark_session import create_spark_session

from src.ingestion.reader import read_json
from src.ingestion.writer import write_parquet
from src.ingestion.sampler import create_sample
from pyspark.sql import functions as F
from config.datasets.schema import (
    REVIEWS_COLUMNS,
    METADATA_COLUMNS,
)


def main():

    print("=" * 60)
    print("Amazon Review Analytics - Ingestion Pipeline")
    print("=" * 60)

    spark = create_spark_session()

    # ----------------------------------------
    # Read Raw Data
    # ----------------------------------------

    print("\nReading Reviews Dataset...")

    reviews_df = read_json(spark, RAW_REVIEWS_PATH).select(*REVIEWS_COLUMNS)

    # testing
    # print(f"Reviews Rows : {reviews_df.count():,}")
    print("Reviews Dataset Loaded.")

    print("\nReading Metadata Dataset...")

    metadata_df = read_json(spark, RAW_METADATA_PATH).select(
        *METADATA_COLUMNS,
        F.regexp_replace(F.col("price"), "—", "").cast("double").alias("price")
    )

    # testing
    # print(f"Metadata Rows : {metadata_df.count():,}")
    print("Metadata Dataset Loaded.")

    # ----------------------------------------
    # Bronze Layer
    # ----------------------------------------

    print("\nWriting Bronze Reviews...")

    write_parquet(
        reviews_df,
        BRONZE_REVIEWS_PATH,
    )

    print("Bronze Reviews Written.")

    print("\nWriting Bronze Metadata...")

    write_parquet(
        metadata_df,
        BRONZE_METADATA_PATH,
    )

    print("Bronze Metadata Written.")

    # ----------------------------------------
    # Sample Layer
    # ----------------------------------------

    print("\nCreating Review Sample...")

    reviews_sample = create_sample(
        reviews_df,
        fraction=0.01,
    )

    print("Creating Metadata Sample...")

    metadata_sample = create_sample(
        metadata_df,
        fraction=0.01,
    )

    print("\nWriting Review Sample...")

    write_parquet(
        reviews_sample,
        SAMPLE_REVIEWS_PATH,
    )

    print("Review Sample Written.")

    print("\nWriting Metadata Sample...")

    write_parquet(
        metadata_sample,
        SAMPLE_METADATA_PATH,
    )

    print("Metadata Sample Written.")

    print("\nPipeline Completed Successfully!")

    spark.stop()


if __name__ == "__main__":
    main()
