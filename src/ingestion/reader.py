from pyspark.sql import DataFrame, SparkSession


def read_json(
    spark: SparkSession,
    path: str,
) -> DataFrame:
    """
    Read a JSON Lines dataset from the specified path.

    Args:
        spark: Active SparkSession.
        path: S3 or local path to the JSONL dataset.

    Returns:
        A Spark DataFrame containing the loaded dataset.
    """

    return spark.read.json(path)