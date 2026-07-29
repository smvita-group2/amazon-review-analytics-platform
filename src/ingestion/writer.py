from pyspark.sql import DataFrame


def write_parquet(
    df: DataFrame,
    output_path: str,
    mode: str = "overwrite",
) -> None:
    """
    Write a DataFrame as Parquet.

    Args:
        df: Spark DataFrame to write.
        output_path: Destination S3 or local path.
        mode: Spark write mode. Default is 'overwrite'.
    """

    (df.write.mode(mode).parquet(output_path))
