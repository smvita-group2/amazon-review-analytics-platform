"""
AWS Glue Job

Gold ML Cleaned -> Review Analytics

Generates product-level review analytics used by the
Hybrid RAG retrieval pipeline.
"""

# ==========================================================
# Standard Library
# ==========================================================

import logging
import sys

# ==========================================================
# Third Party
# ==========================================================

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

from pyspark.context import SparkContext

from pyspark.sql import DataFrame

from pyspark.sql.functions import (
    avg,
    col,
    count,
    first,
    round,
    sum,
    when,
)

# ==========================================================
# Glue Initialization
# ==========================================================

args = getResolvedOptions(
    sys.argv,
    [
        "JOB_NAME",
        "datasets",
    ],
)

spark_context = SparkContext()

glue_context = GlueContext(
    spark_context,
)

spark = glue_context.spark_session

job = Job(
    glue_context,
)

job.init(
    args["JOB_NAME"],
    args,
)

# ==========================================================
# Logger
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

# ==========================================================
# Dataset List
# ==========================================================

DATASETS = [
    dataset.strip()
    for dataset in args["datasets"].split(",")
]

# ==========================================================
# Constants
# ==========================================================

BUCKET_NAME = "amazon-review-analytics-group-2"

POSITIVE_RATING = 4
NEUTRAL_RATING = 3

VERY_LOW_CONFIDENCE_THRESHOLD = 3
LOW_CONFIDENCE_THRESHOLD = 8
MEDIUM_CONFIDENCE_THRESHOLD = 20

HIGHLY_POSITIVE_SCORE = 90.0
POSITIVE_SCORE = 80.0
NEUTRAL_SCORE = 65.0
NEGATIVE_SCORE = 50.0

# ==========================================================
# S3 Paths
# ==========================================================

S3_ROOT = (
    f"s3://{BUCKET_NAME}"
)

GOLD_ML_CLEANED_PATH = (
    f"{S3_ROOT}/gold/ml-hybrid-rag/cleaned"
)

REVIEW_ANALYTICS_PATH = (
    f"{S3_ROOT}/gold/ml-hybrid-rag/review_analytics"
)


def get_input_path(
    dataset: str,
) -> str:
    """
    Return Gold ML Cleaned dataset path.
    """

    return (
        f"{GOLD_ML_CLEANED_PATH}/{dataset}"
    )


def get_output_path(
    dataset: str,
) -> str:
    """
    Return Review Analytics dataset path.
    """

    return (
        f"{REVIEW_ANALYTICS_PATH}/{dataset}"
    )


# ==========================================================
# Reader
# ==========================================================


def read_parquet(
    path: str,
) -> DataFrame:
    """
    Read a Parquet dataset from Amazon S3.
    """

    logger.info(
        "Reading dataset from '%s'.",
        path,
    )

    return spark.read.parquet(
        path,
    )


# ==========================================================
# Writer
# ==========================================================


def write_parquet(
    df: DataFrame,
    output_path: str,
) -> None:
    """
    Write the Review Analytics dataset to Amazon S3.
    """

    logger.info(
        "Writing Review Analytics dataset to '%s'.",
        output_path,
    )

    (
        df.write.mode(
            "overwrite",
        )
        .option(
            "compression",
            "snappy",
        )
        .parquet(
            output_path,
        )
    )
# ==========================================================
# Review Analytics Transformer
# ==========================================================


class ReviewAnalyticsTransformer:
    """
    Generates product-level review analytics for the
    Hybrid RAG retrieval pipeline.
    """

    def __init__(
        self,
        df: DataFrame,
    ):
        self.df = df

    def aggregate_reviews(
        self,
    ):
        """
        Aggregate review statistics for each product.
        """

        self.df = (
            self.df.groupBy(
                "parent_asin",
            ).agg(
                first(
                    "product_average_rating",
                ).alias(
                    "product_average_rating",
                ),
                count(
                    "*",
                ).alias(
                    "review_count",
                ),
                sum(
                    when(
                        col("review_rating") >= POSITIVE_RATING,
                        1,
                    ).otherwise(
                        0,
                    )
                ).alias(
                    "positive_review_count",
                ),
                sum(
                    when(
                        col("review_rating") == NEUTRAL_RATING,
                        1,
                    ).otherwise(
                        0,
                    )
                ).alias(
                    "neutral_review_count",
                ),
                sum(
                    when(
                        col("review_rating") < NEUTRAL_RATING,
                        1,
                    ).otherwise(
                        0,
                    )
                ).alias(
                    "negative_review_count",
                ),
                round(
                    avg(
                        "helpful_vote",
                    ),
                    2,
                ).alias(
                    "average_helpful_vote",
                ),
                round(
                    avg(
                        when(
                            col("verified_purchase"),
                            1,
                        ).otherwise(
                            0,
                        )
                    )
                    * 100,
                    2,
                ).alias(
                    "verified_purchase_percentage",
                ),
            )
        )

        return self

    def calculate_percentages(
        self,
    ):
        """
        Calculate review sentiment percentages.
        """

        self.df = (
            self.df.withColumn(
                "positive_percentage",
                round(
                    (
                        col("positive_review_count")
                        / col("review_count")
                    )
                    * 100,
                    2,
                ),
            )
            .withColumn(
                "neutral_percentage",
                round(
                    (
                        col("neutral_review_count")
                        / col("review_count")
                    )
                    * 100,
                    2,
                ),
            )
            .withColumn(
                "negative_percentage",
                round(
                    (
                        col("negative_review_count")
                        / col("review_count")
                    )
                    * 100,
                    2,
                ),
            )
        )

        return self

    def derive_confidence_level(
        self,
    ):
        """
        Derive recommendation confidence level
        based on the number of reviews.
        """

        self.df = self.df.withColumn(
            "confidence_level",
            when(
                col("review_count")
                >= MEDIUM_CONFIDENCE_THRESHOLD,
                "High",
            )
            .when(
                col("review_count")
                >= LOW_CONFIDENCE_THRESHOLD,
                "Medium",
            )
            .when(
                col("review_count")
                >= VERY_LOW_CONFIDENCE_THRESHOLD,
                "Low",
            )
            .otherwise(
                "Very Low",
            ),
        )

        return self

    def calculate_sentiment_score(
        self,
    ):
        """
        Calculate a weighted sentiment score
        using rating and positive review percentage.
        """

        self.df = self.df.withColumn(
            "sentiment_score",
            round(
                (
                    (
                        col("product_average_rating")
                        / 5
                    )
                    * 100
                    * 0.6
                )
                + (
                    col("positive_percentage")
                    * 0.4
                ),
                2,
            ),
        )

        return self

    def derive_overall_sentiment(
        self,
    ):
        """
        Derive the overall customer sentiment
        using the weighted sentiment score.
        """

        self.df = self.df.withColumn(
            "overall_sentiment",
            when(
                col("sentiment_score")
                >= HIGHLY_POSITIVE_SCORE,
                "Highly Positive",
            )
            .when(
                col("sentiment_score")
                >= POSITIVE_SCORE,
                "Positive",
            )
            .when(
                col("sentiment_score")
                >= NEUTRAL_SCORE,
                "Neutral",
            )
            .when(
                col("sentiment_score")
                >= NEGATIVE_SCORE,
                "Negative",
            )
            .otherwise(
                "Highly Negative",
            ),
        )

        return self

    def reorder_columns(
        self,
    ):
        """
        Reorder output columns.
        """

        self.df = self.df.select(
            "parent_asin",
            "product_average_rating",
            "review_count",
            "positive_review_count",
            "neutral_review_count",
            "negative_review_count",
            "positive_percentage",
            "neutral_percentage",
            "negative_percentage",
            "average_helpful_vote",
            "verified_purchase_percentage",
            "confidence_level",
            "sentiment_score",
            "overall_sentiment",
        )

        return self

    def transform(
        self,
    ) -> DataFrame:
        """
        Execute the complete transformation
        pipeline.
        """

        return (
            self.aggregate_reviews()
            .calculate_percentages()
            .derive_confidence_level()
            .calculate_sentiment_score()
            .derive_overall_sentiment()
            .reorder_columns()
            .df
        )

# ==========================================================
# Review Analytics Validator
# ==========================================================


class ReviewAnalyticsValidator:
    """
    Validates the Review Analytics dataset before writing.
    """

    EXPECTED_COLUMNS = [
        "parent_asin",
        "product_average_rating",
        "review_count",
        "positive_review_count",
        "neutral_review_count",
        "negative_review_count",
        "positive_percentage",
        "neutral_percentage",
        "negative_percentage",
        "average_helpful_vote",
        "verified_purchase_percentage",
        "confidence_level",
        "sentiment_score",
        "overall_sentiment",
    ]

    REQUIRED_COLUMNS = [
        "parent_asin",
        "product_average_rating",
        "review_count",
    ]

    def __init__(
        self,
        df: DataFrame,
    ):
        self.df = df

    def validate_not_empty(
        self,
    ):
        """
        Validate that the DataFrame is not empty.
        """

        if not self.df.take(1):

            raise ValueError(
                "Review Analytics DataFrame is empty."
            )

        return self

    def validate_schema(
        self,
    ):
        """
        Validate the output schema.
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

            logger.error(
                "Schema validation failed."
            )

            logger.error(
                "Missing Columns: %s",
                missing_columns,
            )

            logger.error(
                "Unexpected Columns: %s",
                extra_columns,
            )

            raise ValueError(
                "Review Analytics schema validation failed."
            )

        return self

    def validate_required_columns(
        self,
    ):
        """
        Validate required columns contain no NULL values.
        """

        for column_name in self.REQUIRED_COLUMNS:

            null_count = self.df.filter(
                col(
                    column_name,
                ).isNull()
            ).count()

            if null_count > 0:

                raise ValueError(
                    f"{column_name} contains "
                    f"{null_count} NULL values."
                )

        return self

    def run(
        self,
    ):
        """
        Execute all validations.
        """

        return (
            self.validate_not_empty()
            .validate_schema()
            .validate_required_columns()
        )


# ==========================================================
# Pipeline
# ==========================================================


def process_dataset(
    dataset: str,
) -> None:
    """
    Process a single dataset.
    """

    logger.info(
        "Processing dataset '%s'.",
        dataset,
    )

    input_path = get_input_path(
        dataset,
    )

    output_path = get_output_path(
        dataset,
    )

    dataframe = read_parquet(
        input_path,
    )

    analytics_df = (
        ReviewAnalyticsTransformer(
            dataframe,
        )
        .transform()
    )

    ReviewAnalyticsValidator(
        analytics_df,
    ).run()

    write_parquet(
        analytics_df,
        output_path,
    )

    logger.info(
        "Successfully processed dataset '%s'.",
        dataset,
    )


# ==========================================================
# Main
# ==========================================================


def main() -> None:
    """
    Execute the Review Analytics Glue job.
    """

    logger.info(
        "=" * 80,
    )

    logger.info(
        "Starting Review Analytics Glue Job.",
    )

    logger.info(
        "=" * 80,
    )

    for dataset in DATASETS:

        process_dataset(
            dataset,
        )

    logger.info(
        "=" * 80,
    )

    logger.info(
        "Review Analytics Glue Job completed successfully.",
    )

    logger.info(
        "=" * 80,
    )

    job.commit()


if __name__ == "__main__":

    main()
