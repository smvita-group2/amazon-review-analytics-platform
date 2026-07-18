from pyspark.sql import SparkSession


def create_spark_session(
    app_name: str = "Amazon Review Analytics",
    local: bool = True,
) -> SparkSession:
    """
    Create and return a SparkSession.

    Args:
        app_name: Name of the Spark application.
        local: Run Spark in local mode if True.
               Set to False when running on EMR.

    Returns:
        Configured SparkSession.
    """

    builder = SparkSession.builder.appName(app_name)

    if local:
        builder = builder.master("local[*]")

    spark = (
        builder
        .config("spark.sql.caseSensitive", "true")
        .config("spark.sql.repl.eagerEval.enabled", "true")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")

    return spark