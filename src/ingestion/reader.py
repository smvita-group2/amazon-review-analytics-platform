from pyspark.sql import DataFrame, SparkSession


def read_parquet(
    spark: SparkSession,
    path: str,
) -> DataFrame:
    """
    Read a Parquet dataset from the specified path.

    Args:
        spark: Active SparkSession.
        path: S3 or local path to the Parquet dataset.

    Returns:
        A Spark DataFrame.
    """

    return spark.read.parquet(path)
