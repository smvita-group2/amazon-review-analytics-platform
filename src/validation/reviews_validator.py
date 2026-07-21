"""
Validation logic for the Silver reviews dataset.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col
from config.datasets.schema import SILVER_REVIEWS_SCHEMA


class ReviewsValidator:
    """
    Validates the Silver reviews dataset before writing.
    """

    def __init__(self, df: DataFrame):
        self.df = df

    def validate_schema(self):
        """
        Validates the Silver reviews schema.
        """

        actual_schema = self.df.schema
        expected_schema = SILVER_REVIEWS_SCHEMA

        if actual_schema != expected_schema:
            raise ValueError(
                "Silver reviews schema validation failed."
            )

        return self

    def validate_required_columns(self):
        """
        Validates that required columns do not contain null values.
        """

        required_columns = [
            "parent_asin",
            "user_id",
            "review_rating",
            "review_timestamp",
        ]

        for column in required_columns:
            null_count = (
                self.df
                .filter(col(column).isNull())
                .count()
            )

            if null_count > 0:
                raise ValueError(
                    f"Required column '{column}' contains {null_count} null values."
                )

        return self

    def validate_rating_range(self):
        """
        Validates that review ratings are between 1 and 5.
        """

        invalid_count = (
            self.df
            .filter(
                (col("review_rating") < 1) |
                (col("review_rating") > 5)
            )
            .count()
        )

        if invalid_count > 0:
            raise ValueError(
                f"Found {invalid_count} review(s) with invalid ratings."
            )

        return self

    def validate_helpful_vote(self):
        """
        Validates that helpful votes are non-negative.
        """

        invalid_count = (
            self.df
            .filter(col("helpful_vote") < 0)
            .count()
        )

        if invalid_count > 0:
            raise ValueError(
                f"Found {invalid_count} review(s) with negative helpful votes."
            )

        return self

    def validate_timestamp(self):
        """
        Validates that review timestamps are not null.
        """

        null_count = (
            self.df
            .filter(col("review_timestamp").isNull())
            .count()
        )

        if null_count > 0:
            raise ValueError(
                f"Found {null_count} review(s) with null timestamps."
            )

        return self

    def run(self):
        """
        Executes all validations.
        """

        return (
            self.validate_schema()
                .validate_required_columns()
                .validate_rating_range()
                .validate_helpful_vote()
                .validate_timestamp()
        )