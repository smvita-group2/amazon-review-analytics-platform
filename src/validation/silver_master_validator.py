"""
Validation logic for the Silver Master dataset.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col

from config.datasets.schema import SILVER_MASTER_COLUMNS


class SilverMasterValidator:
    """
    Performs validation checks on the Silver Master dataset.
    """

    EXPECTED_COLUMNS = SILVER_MASTER_COLUMNS

    # Only fields that must always exist
    REQUIRED_COLUMNS = [
        "parent_asin",
        "user_id",
        "review_rating",
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

        if missing_columns:
            raise ValueError(f"Missing columns: {missing_columns}")

        if extra_columns:
            raise ValueError(f"Unexpected columns: {extra_columns}")

        return self

    def validate_required_columns(self):
        """
        Validates that required columns do not contain NULL values.
        """

        for column_name in self.REQUIRED_COLUMNS:

            null_count = self.df.filter(col(column_name).isNull()).count()

            if null_count > 0:
                raise ValueError(
                    f"Column '{column_name}' contains {null_count} NULL values."
                )

        return self

    def validate_not_empty(self):
        """
        Validates that the dataframe is not empty.
        """

        if not self.df.take(1):
            raise ValueError("Silver Master DataFrame is empty.")

        return self

    def run(self):
        """
        Executes all Silver Master validation checks.
        """

        return self.validate_not_empty().validate_schema().validate_required_columns()
