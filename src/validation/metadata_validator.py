"""
Validation logic for the Silver metadata dataset.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count


class MetadataValidator:
    """
    Performs validation checks on the Silver metadata dataset.
    """

    EXPECTED_COLUMNS = [
        "parent_asin",
        "product_title",
        "store",
        "main_category",
        "sub_category",
        "product_price",
        "product_average_rating",
        "product_rating_count",
        "description_text",
        "features_text",
        "product_image_url",
    ]

    REQUIRED_COLUMNS = [
        "parent_asin",
        "product_title",
    ]

    def _init_(self, df: DataFrame):
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

        if missing_columns:
            raise ValueError(
                f"Missing columns: {missing_columns}"
            )

        if extra_columns:
            raise ValueError(
                f"Unexpected columns: {extra_columns}"
            )

        return self

    def validate_duplicate_parent_asin(self):
        """
        Validates that parent_asin is unique.
        """

        duplicate_count = (
            self.df
            .groupBy("parent_asin")
            .agg(count("*").alias("record_count"))
            .filter(col("record_count") > 1)
            .count()
        )

        if duplicate_count > 0:
            raise ValueError(
                f"Found {duplicate_count} duplicate parent_asin values."
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
        Validates that product ratings are between 0 and 5.
        """

        invalid_count = (
            self.df
            .filter(
                col("product_average_rating").isNotNull() &
                (
                    (col("product_average_rating") < 0) |
                    (col("product_average_rating") > 5)
                )
            )
            .count()
        )

        if invalid_count > 0:
            raise ValueError(
                f"Found {invalid_count} records with invalid product_average_rating."
            )

        return self

    def validate_rating_count(self):
        """
        Validates that product_rating_count is not negative.
        """

        invalid_count = (
            self.df
            .filter(
                col("product_rating_count").isNotNull() &
                (col("product_rating_count") < 0)
            )
            .count()
        )

        if invalid_count > 0:
            raise ValueError(
                f"Found {invalid_count} records with negative product_rating_count."
            )

        return self

    def validate_price(self):
        """
        Validates that product_price is not negative.
        """

        invalid_count = (
            self.df
            .filter(
                col("product_price").isNotNull() &
                (col("product_price") < 0)
            )
            .count()
        )

        if invalid_count > 0:
            raise ValueError(
                f"Found {invalid_count} records with negative product_price."
            )

        return self

    def run(self):
        """
        Executes all metadata validation checks.
        """

        return (
            self.validate_schema()
                .validate_duplicate_parent_asin()
                .validate_required_columns()
                .validate_rating_range()
                .validate_rating_count()
                .validate_price()
        )