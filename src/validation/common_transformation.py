"""
Reusable transformation functions shared across the Bronze to Silver pipeline.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, trim, when
from pyspark.sql.types import StringType


def trim_string_columns(df: DataFrame, columns: list[str]) -> DataFrame:
    """
    Trims leading and trailing whitespace from the specified string columns.
    """

    for column in columns:
        if column in df.columns and isinstance(df.schema[column].dataType, StringType):
            df = df.withColumn(column, trim(col(column)))

    return df


def empty_strings_to_null(df: DataFrame, columns: list[str]) -> DataFrame:
    """
    Replaces empty strings with NULL values for the specified string columns.
    """

    for column in columns:
        if column in df.columns and isinstance(df.schema[column].dataType, StringType):
            df = df.withColumn(
                column, when(trim(col(column)) == "", None).otherwise(col(column))
            )

    return df
