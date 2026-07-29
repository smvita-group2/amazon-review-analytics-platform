"""
Transformer for creating the Gold Visualization dataset.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    coalesce,
    col,
    concat,
    date_format,
    length,
    lit,
    quarter,
    size,
    split,
    when,
)

from config.datasets.constants import (
    END_YEAR,
    MIN_HELPFUL_VOTES,
    MIN_PRODUCT_REVIEW_THRESHOLD,
    START_YEAR,
)

from config.datasets.schema import (
    GOLD_VISUALIZATION_COLUMNS,
)


class GoldVisualizationTransformer:
    """
    Applies feature engineering transformations to the
    Silver Master dataset to create the Gold Visualization dataset.
    """

    def __init__(self, df: DataFrame):
        """
        Initializes the Gold Visualization transformer.

        Args:
            df:
                Silver Master DataFrame.
        """

        self.df = df

    def apply_year_filter(self):
        """
        Filters records within the configured year range.
        """

        self.df = self.df.filter(
            col("review_year").between(
                START_YEAR,
                END_YEAR,
            )
        )

        return self

    def drop_unused_columns(self):
        """
        Drops columns that are not required for visualization.
        """

        self.df = self.df.drop(
            "review_timestamp",
        )

        return self

    def add_time_features(self):
        """
        Adds derived time-based features.
        """

        self.df = (
            self.df.withColumn(
                "review_month_name",
                date_format(
                    col("review_date"),
                    "MMMM",
                ),
            )
            .withColumn(
                "review_quarter",
                concat(
                    lit("Q"),
                    quarter(
                        col("review_date"),
                    ),
                ),
            )
            .withColumn(
                "review_year_month",
                date_format(
                    col("review_date"),
                    "yyyy-MM",
                ),
            )
            .withColumn(
                "review_day_of_week",
                date_format(
                    col("review_date"),
                    "EEEE",
                ),
            )
        )

        return self

    def add_review_features(self):
        """
        Adds review-related features.
        """

        review_text = coalesce(
            col("review_text"),
            lit(""),
        )

        self.df = self.df.withColumn(
            "review_length",
            length(
                review_text,
            ),
        ).withColumn(
            "review_word_count",
            size(
                split(
                    review_text,
                    r"\s+",
                )
            ),
        )

        return self

    def add_rating_features(self):
        """
        Adds rating-related features.
        """

        self.df = self.df.withColumn(
            "rating_category",
            when(
                col("review_rating").isin(
                    1,
                    2,
                ),
                "Negative",
            )
            .when(
                col("review_rating") == 3,
                "Neutral",
            )
            .otherwise(
                "Positive",
            ),
        )

        return self

    def add_purchase_features(self):
        """
        Adds purchase-related features.
        """

        self.df = self.df.withColumn(
            "purchase_type",
            when(
                col("verified_purchase"),
                "Verified Purchase",
            ).otherwise(
                "Non-Verified Purchase",
            ),
        )

        return self

    def add_helpfulness_features(self):
        """
        Adds helpfulness-related features.
        """

        helpful_votes = coalesce(
            col("helpful_vote"),
            lit(0),
        )

        self.df = self.df.withColumn(
            "is_helpful",
            helpful_votes >= MIN_HELPFUL_VOTES,
        ).withColumn(
            "helpful_vote_bucket",
            when(
                helpful_votes == 0,
                "No Votes",
            )
            .when(
                helpful_votes <= 5,
                "Low",
            )
            .when(
                helpful_votes <= 20,
                "Medium",
            )
            .otherwise(
                "High",
            ),
        )

        return self

    def add_product_features(self):
        """
        Adds product-related features.
        """

        product_rating_count = coalesce(
            col("product_rating_count"),
            lit(0),
        )

        self.df = self.df.withColumn(
            "review_count_threshold_met",
            product_rating_count >= MIN_PRODUCT_REVIEW_THRESHOLD,
        ).withColumn(
            "product_review_volume_category",
            when(
                product_rating_count < 100,
                "Low Volume",
            )
            .when(
                product_rating_count < 1000,
                "Medium Volume",
            )
            .otherwise(
                "High Volume",
            ),
        )

        return self

    def reorder_columns(self):
        """
        Reorders columns according to the Gold Visualization schema.
        """

        self.df = self.df.select(
            *GOLD_VISUALIZATION_COLUMNS,
        )

        return self

    def transform(self) -> DataFrame:
        """
        Executes the complete Gold Visualization transformation pipeline.

        Returns:
            Gold Visualization DataFrame.
        """

        return (
            self.apply_year_filter()
            .drop_unused_columns()
            .add_time_features()
            .add_review_features()
            .add_rating_features()
            .add_purchase_features()
            .add_helpfulness_features()
            .add_product_features()
            .reorder_columns()
            .df
        )
