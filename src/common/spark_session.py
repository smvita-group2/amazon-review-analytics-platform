from pyspark.sql import SparkSession


def create_spark_session(
    app_name: str = "Amazon Review Analytics",
) -> SparkSession:
    """
    Creates and returns a SparkSession for local development.

    Returns:
        SparkSession: Configured Spark session.
    """

    spark = (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .config("spark.sql.repl.eagerEval.enabled", "true")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")

    return spark