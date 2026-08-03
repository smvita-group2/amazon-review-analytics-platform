"""
Validation logic for the Silver reviews dataset.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count, when


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
            column for column in self.EXPECTED_COLUMNS if column not in actual_columns
        ]

        extra_columns = [
            column for column in actual_columns if column not in self.EXPECTED_COLUMNS
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

            raise ValueError("Reviews schema validation failed.")

        return self

    def run(self):
        """
        Executes all validation checks in a single PySpark aggregation pass.
        """

        self.validate_schema()

        # Build single-pass aggregation expressions
        agg_exprs = []

        for req_col in self.REQUIRED_COLUMNS:
            agg_exprs.append(
                count(when(col(req_col).isNull(), 1)).alias(f"null_{req_col}")
            )

        agg_exprs.append(
            count(
                when(
                    col("review_rating").isNotNull()
                    & ((col("review_rating") < 1) | (col("review_rating") > 5)),
                    1,
                )
            ).alias("invalid_ratings")
        )

        agg_exprs.append(
            count(
                when(
                    col("helpful_vote").isNotNull() & (col("helpful_vote") < 0),
                    1,
                )
            ).alias("invalid_helpful_votes")
        )

        metrics = self.df.select(*agg_exprs).collect()[0]

        for req_col in self.REQUIRED_COLUMNS:
            null_count = metrics[f"null_{req_col}"]
            if null_count > 0:
                raise ValueError(
                    f"Column '{req_col}' contains {null_count} NULL values."
                )

        if metrics["invalid_ratings"] > 0:
            raise ValueError(
                f"Found {metrics['invalid_ratings']} review(s) with invalid ratings."
            )

        if metrics["invalid_helpful_votes"] > 0:
            raise ValueError(
                f"Found {metrics['invalid_helpful_votes']} review(s) with negative helpful votes."
            )

        return self
