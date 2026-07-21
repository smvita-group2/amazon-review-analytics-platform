"""
Validation logic for the Silver reviews dataset.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col


class ReviewsValidator:
    """
    Validates the Silver reviews dataset before writing.
    """

    EXPECTED_COLUMNS = [
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
    ]

    REQUIRED_COLUMNS = [
        "parent_asin",
        "user_id",
        "review_rating",
        "review_timestamp",
    ]

    def __init__(self, df: DataFrame):
        self.df = df

    def validate_schema(self):
        """
        Validates that the dataframe contains the expected columns.
        """

        actual_columns = self.df.columns

        missing_columns = [
            column
            for column in self.EXPECTED_COLUMNS
            if column not in actual_columns
        ]

        extra_columns = [
            column
            for column in actual_columns
            if column not in self.EXPECTED_COLUMNS
        ]

        if missing_columns or extra_columns:

            print("\n========== SCHEMA VALIDATION ==========")
            print(f"Expected Columns ({len(self.EXPECTED_COLUMNS)}):")
            print(self.EXPECTED_COLUMNS)

            print(f"\nActual Columns ({len(actual_columns)}):")
            print(actual_columns)

            if missing_columns:
                print(f"\nMissing Columns: {missing_columns}")

            if extra_columns:
                print(f"\nUnexpected Columns: {extra_columns}")

            raise ValueError(
                "Reviews schema validation failed."
            )

        return self

    def validate_required_columns(self):
        """
        Validates that required columns do not contain NULL values.
        """

        for column_name in self.REQUIRED_COLUMNS:

            null_count = (
                self.df
                .filter(col(column_name).isNull())
                .count()
            )

            if null_count > 0:
                raise ValueError(
                    f"Column '{column_name}' contains {null_count} NULL values."
                )

        return self

    def validate_rating_range(self):
        """
        Validates that review ratings are between 1 and 5.
        """

        invalid_count = (
            self.df
            .filter(
                col("review_rating").isNotNull() &
                (
                    (col("review_rating") < 1) |
                    (col("review_rating") > 5)
                )
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
            .filter(
                col("helpful_vote").isNotNull() &
                (col("helpful_vote") < 0)
            )
            .count()
        )

        if invalid_count > 0:
            raise ValueError(
                f"Found {invalid_count} review(s) with negative helpful votes."
            )

        return self

    def validate_timestamp(self):
        """
        Validates that review timestamps are not NULL.
        """

        null_count = (
            self.df
            .filter(col("review_timestamp").isNull())
            .count()
        )

        if null_count > 0:
            raise ValueError(
                f"Found {null_count} review(s) with NULL timestamps."
            )

        return self

    def run(self):
        """
        Executes all validation checks.
        """

        return (
            self.validate_schema()
                .validate_required_columns()
                .validate_rating_range()
                .validate_helpful_vote()
                .validate_timestamp()
        )