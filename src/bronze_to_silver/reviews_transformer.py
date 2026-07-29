"""
Transformation logic for converting Bronze reviews into the Silver layer.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col,
    trim,
    lit,
    when,
    from_unixtime,
    to_date,
    year,
    month,
)


class ReviewsTransformer:
    """
    Applies all transformations required to convert Bronze reviews
    into the standardized Silver schema.
    """

    def __init__(self, df: DataFrame):
        self.df = df

    def rename_columns(self):
        """
        Renames Bronze review columns to the standardized Silver schema.
        """

        self.df = (
            self.df.withColumnRenamed("rating", "review_rating")
            .withColumnRenamed("title", "review_title")
            .withColumnRenamed("text", "review_text")
            .withColumnRenamed("timestamp", "review_timestamp")
        )

        return self

    def clean_review_title(self):
        """
        Removes leading and trailing whitespace from review titles.
        """

        self.df = self.df.withColumn("review_title", trim(col("review_title")))

        return self

    def clean_review_text(self):
        """
        Removes leading and trailing whitespace from review text.
        """

        self.df = self.df.withColumn("review_text", trim(col("review_text")))

        return self

    def clean_helpful_vote(self):
        """
        Replaces null and negative helpful votes with 0.
        """

        self.df = self.df.withColumn(
            "helpful_vote",
            when(col("helpful_vote").isNull(), lit(0))
            .when(col("helpful_vote") < 0, lit(0))
            .otherwise(col("helpful_vote"))
            .cast("int"),
        )

        return self

    def convert_timestamp(self):
        """
        Converts Unix epoch milliseconds into a Spark timestamp.
        """

        self.df = self.df.withColumn(
            "review_timestamp",
            from_unixtime(col("review_timestamp") / 1000).cast("timestamp"),
        )

        return self

    def extract_date_parts(self):
        """
        Extracts review date, year and month from the review timestamp.
        """

        self.df = (
            self.df.withColumn("review_date", to_date(col("review_timestamp")))
            .withColumn("review_year", year(col("review_timestamp")))
            .withColumn("review_month", month(col("review_timestamp")))
        )

        return self

    def reorder_columns(self):
        """
        Reorders columns to match the Silver reviews schema.
        """

        self.df = self.df.select(
            "parent_asin",
            "user_id",
            "review_rating",
            "review_title",
            "review_text",
            "helpful_vote",
            "verified_purchase",
            "review_timestamp",
            "review_date",
            "review_year",
            "review_month",
        )

        return self

    def transform(self) -> DataFrame:
        """
        Executes all review transformations.
        """

        return (
            self.rename_columns()
            .clean_review_title()
            .clean_review_text()
            .clean_helpful_vote()
            .convert_timestamp()
            .extract_date_parts()
            .reorder_columns()
            .df
        )
