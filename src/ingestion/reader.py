from pyspark.sql import DataFrame, SparkSession


def read_parquet(
    spark: SparkSession,
    path: str,
) -> DataFrame:
    """
    Read a Parquet file from S3 or local path.
    """

    return spark.read.parquet(path)