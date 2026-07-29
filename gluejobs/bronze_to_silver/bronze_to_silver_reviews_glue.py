"""
AWS Glue Job

Bronze Reviews → Silver Reviews

Processes one or more datasets from the Bronze layer,
applies review transformations and validations,
and writes the Silver reviews dataset back to Amazon S3.
"""

import logging
import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import DataFrame
from pyspark.sql.functions import (col, from_unixtime, lit, month, to_date,
                                   trim, when, year)

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

sc = SparkContext()

glueContext = GlueContext(sc)

spark = glueContext.spark_session

# Required because Amazon Reviews contains nested fields
# that differ only by case.
spark.conf.set("spark.sql.caseSensitive", "true")

job = Job(glueContext)

job.init(args["JOB_NAME"], args)

# ==========================================================
# Logger
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

# ==========================================================
# Datasets
# ==========================================================

DATASETS = [dataset.strip() for dataset in args["datasets"].split(",")]

# ==========================================================
# Constants
# ==========================================================

BUCKET_NAME = "amazon-review-analytics-group-2"


# ==========================================================
# S3 Paths
# ==========================================================

S3_ROOT = f"s3://{BUCKET_NAME}"

BRONZE_REVIEWS_ROOT = f"{S3_ROOT}/bronze/reviews"

SILVER_REVIEWS_ROOT = f"{S3_ROOT}/silver/reviews"


def get_bronze_reviews_path(dataset_name: str) -> str:
    return f"{BRONZE_REVIEWS_ROOT}/{dataset_name}"


def get_silver_reviews_path(dataset_name: str) -> str:
    return f"{SILVER_REVIEWS_ROOT}/{dataset_name}"


# ==========================================================
# Reader
# ==========================================================


def read_parquet(path: str) -> DataFrame:

    logger.info(f"Reading Bronze Reviews: {path}")

    return spark.read.parquet(path)


# ==========================================================
# Writer
# ==========================================================


def write_parquet(
    df: DataFrame,
    output_path: str,
) -> None:

    logger.info(f"Writing Silver Reviews: {output_path}")

    (df.write.mode("overwrite").option("compression", "snappy").parquet(output_path))


# ==========================================================
# Reviews Transformer
# ==========================================================


class ReviewsTransformer:
    """
    Applies all transformations required to convert Bronze reviews
    into the standardized Silver schema.
    """

    def __init__(self, df: DataFrame):
        self.df = df

    def rename_columns(self):

        self.df = (
            self.df.withColumnRenamed("rating", "review_rating")
            .withColumnRenamed("title", "review_title")
            .withColumnRenamed("text", "review_text")
            .withColumnRenamed("timestamp", "review_timestamp")
        )

        return self

    def clean_review_title(self):

        self.df = self.df.withColumn("review_title", trim(col("review_title")))

        return self

    def clean_review_text(self):

        self.df = self.df.withColumn("review_text", trim(col("review_text")))

        return self

    def clean_helpful_vote(self):

        self.df = self.df.withColumn(
            "helpful_vote",
            when(
                col("helpful_vote").isNull(),
                lit(0),
            )
            .when(
                col("helpful_vote") < 0,
                lit(0),
            )
            .otherwise(col("helpful_vote"))
            .cast("int"),
        )

        return self

    def convert_timestamp(self):

        self.df = self.df.withColumn(
            "review_timestamp",
            from_unixtime(col("review_timestamp") / 1000).cast("timestamp"),
        )

        return self

    def extract_date_parts(self):

        self.df = (
            self.df.withColumn("review_date", to_date(col("review_timestamp")))
            .withColumn("review_year", year(col("review_timestamp")))
            .withColumn("review_month", month(col("review_timestamp")))
        )

        return self

    def remove_duplicates(self):
        """
        Removes duplicate review records.
        """

        self.df = self.df.dropDuplicates()

        return self

    def reorder_columns(self):

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

        return (
            self.rename_columns()
            .clean_review_title()
            .clean_review_text()
            .clean_helpful_vote()
            .convert_timestamp()
            .extract_date_parts()
            .remove_duplicates()
            .reorder_columns()
            .df
        )


# ==========================================================
# Reviews Validator
# ==========================================================


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

        actual_columns = self.df.columns

        missing_columns = [
            column for column in self.EXPECTED_COLUMNS if column not in actual_columns
        ]

        extra_columns = [
            column for column in actual_columns if column not in self.EXPECTED_COLUMNS
        ]

        if missing_columns or extra_columns:

            logger.error("Schema validation failed.")

            logger.error(f"Missing Columns : {missing_columns}")

            logger.error(f"Unexpected Columns : {extra_columns}")

            raise ValueError("Reviews schema validation failed.")

        return self

    def validate_required_columns(self):

        for column_name in self.REQUIRED_COLUMNS:

            null_count = self.df.filter(col(column_name).isNull()).count()

            if null_count > 0:

                raise ValueError(f"{column_name} contains {null_count} NULL values.")

        return self

    def validate_rating_range(self):

        invalid_count = self.df.filter(
            col("review_rating").isNotNull()
            & ((col("review_rating") < 1) | (col("review_rating") > 5))
        ).count()

        if invalid_count > 0:

            raise ValueError(f"Found {invalid_count} invalid ratings.")

        return self

    def validate_helpful_vote(self):

        invalid_count = self.df.filter(col("helpful_vote") < 0).count()

        if invalid_count > 0:

            raise ValueError(f"Found {invalid_count} negative helpful votes.")

        return self

    def validate_timestamp(self):

        null_count = self.df.filter(col("review_timestamp").isNull()).count()

        if null_count > 0:

            raise ValueError(f"Found {null_count} NULL timestamps.")

        return self

    def run(self):

        return (
            self.validate_schema()
            .validate_required_columns()
            .validate_rating_range()
            .validate_helpful_vote()
            .validate_timestamp()
        )


# ==========================================================
# Pipeline
# ==========================================================


def run_pipeline(dataset_name: str) -> None:

    logger.info(f"Processing Dataset : {dataset_name}")

    bronze_path = get_bronze_reviews_path(dataset_name)

    silver_path = get_silver_reviews_path(dataset_name)

    df = read_parquet(bronze_path)

    df = ReviewsTransformer(df).transform()

    df.cache()

    try:

        ReviewsValidator(df).run()

        write_parquet(
            df=df,
            output_path=silver_path,
        )

    finally:

        df.unpersist()

    logger.info(f"Completed Dataset : {dataset_name}")


# ==========================================================
# Main
# ==========================================================


def main():

    logger.info("Starting Bronze → Silver Reviews Glue Job")

    try:

        for dataset_name in DATASETS:

            run_pipeline(dataset_name)

        logger.info("Bronze → Silver Reviews Glue Job Completed Successfully.")

        job.commit()

    except Exception:

        logger.exception("Bronze → Silver Reviews Glue Job Failed.")

        raise


if __name__ == "__main__":
    main()
