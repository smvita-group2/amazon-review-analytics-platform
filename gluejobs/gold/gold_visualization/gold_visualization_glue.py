"""
AWS Glue Job

Silver Master → Gold Visualization

Processes one or more datasets from the Silver Master layer,
creates visualization-ready features,
validates the Gold Visualization dataset,
and writes the Gold Visualization dataset back to Amazon S3.
"""

import sys
import logging

from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job

from pyspark.context import SparkContext
from pyspark.sql import DataFrame

from pyspark.sql.functions import (
    col,
    coalesce,
    concat,
    date_format,
    length,
    lit,
    quarter,
    size,
    split,
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

sc = SparkContext()

glueContext = GlueContext(sc)

spark = glueContext.spark_session

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

DATASETS = [
    dataset.strip()
    for dataset in args["datasets"].split(",")
]

# ==========================================================
# Constants
# ==========================================================

BUCKET_NAME = "amazon-review-analytics-group-2"

START_YEAR = 2014
END_YEAR = 2023

MIN_HELPFUL_VOTES = 2


# ==========================================================
# S3 Paths
# ==========================================================

S3_ROOT = f"s3://{BUCKET_NAME}"

SILVER_MASTER_ROOT = f"{S3_ROOT}/silver/master"

GOLD_VISUALIZATION_ROOT = f"{S3_ROOT}/gold/visualization"


def get_silver_master_path(dataset_name: str) -> str:
    return f"{SILVER_MASTER_ROOT}/{dataset_name}"


def get_gold_visualization_path(dataset_name: str) -> str:
    return f"{GOLD_VISUALIZATION_ROOT}/{dataset_name}"

# ==========================================================
# Reader
# ==========================================================

def read_parquet(path: str) -> DataFrame:

    logger.info(f"Reading: {path}")

    return spark.read.parquet(path)


# ==========================================================
# Writer
# ==========================================================

def write_parquet(
    df: DataFrame,
    output_path: str,
) -> None:

    logger.info(
        f"Writing Gold Visualization: {output_path}"
    )

    (
        df.write
        .mode("overwrite")
        .option("compression", "snappy")
        .parquet(output_path)
    )

# ==========================================================
# Gold Visualization Transformer
# ==========================================================

class GoldVisualizationTransformer:
    """
    Applies feature engineering transformations to create
    the Gold Visualization dataset.
    """

    def __init__(self, df: DataFrame):
        self.df = df

    def apply_year_filter(self):

        self.df = self.df.filter(
            col("review_year").between(
                START_YEAR,
                END_YEAR,
            )
        )

        return self

    def clean_store(self):

        self.df = self.df.withColumn(
            "store",
            coalesce(
                col("store"),
                lit("Unknown"),
            ),
        )

        return self

    def add_time_features(self):

        self.df = (
            self.df
            .withColumn(
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

        review_text = coalesce(
            col("review_text"),
            lit(""),
        )

        self.df = (
            self.df
            .withColumn(
                "review_length",
                length(
                    review_text,
                ),
            )
            .withColumn(
                "review_word_count",
                when(
                    length(review_text) == 0,
                    0,
                ).otherwise(
                    size(
                        split(
                            review_text,
                            r"\s+",
                        )
                    )
                ),
            )
        )

        return self

    def add_rating_features(self):

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

        helpful_votes = coalesce(
            col("helpful_vote"),
            lit(0),
        )

        self.df = (
            self.df
            .withColumn(
                "is_helpful",
                helpful_votes >= MIN_HELPFUL_VOTES,
            )
            .withColumn(
                "helpful_vote_bucket",
                when(
                    helpful_votes == 0,
                    "No Votes",
                )
                .when(
                    helpful_votes <= 10,
                    "Low",
                )
                .when(
                    helpful_votes <= 50,
                    "Medium",
                )
                .otherwise(
                    "High",
                ),
            )
        )

        return self

    def add_product_features(self):

        product_rating_count = coalesce(
            col("product_rating_count"),
            lit(0),
        )

        self.df = (
            self.df
            .withColumn(
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
        )

        return self

    def drop_unused_columns(self):

        self.df = self.df.drop(
            "review_timestamp",
            "product_price",
            "description_text",
            "features_text",
            "review_title",
            "review_text",
        )

        return self

    def reorder_columns(self):

        self.df = self.df.select(
            *GOLD_VISUALIZATION_COLUMNS,
        )

        return self

    def transform(self) -> DataFrame:

        return (
            self.apply_year_filter()
                .clean_store()
                .add_time_features()
                .add_review_features()
                .add_rating_features()
                .add_purchase_features()
                .add_helpfulness_features()
                .add_product_features()
                .drop_unused_columns()
                .reorder_columns()
                .df
        )
# ==========================================================
# Gold Visualization Schema
# ==========================================================

GOLD_VISUALIZATION_COLUMNS = [

    # ===========================
    # Product Information
    # ===========================

    "parent_asin",
    "product_title",
    "store",
    "main_category",
    "sub_category",
    "product_average_rating",
    "product_rating_count",
    "product_image_url",

    # ===========================
    # Review Information
    # ===========================

    "user_id",
    "review_rating",
    "helpful_vote",
    "verified_purchase",

    # ===========================
    # Date Features
    # ===========================

    "review_date",
    "review_year",
    "review_month",
    "review_month_name",
    "review_quarter",
    "review_year_month",
    "review_day_of_week",

    # ===========================
    # Product Description
    # ===========================

    # ===========================
    # Review Features
    # ===========================

    "review_length",
    "review_word_count",

    # ===========================
    # Rating Features
    # ===========================

    "rating_category",

    # ===========================
    # Purchase Features
    # ===========================

    "purchase_type",

    # ===========================
    # Helpfulness Features
    # ===========================

    "is_helpful",
    "helpful_vote_bucket",

    # ===========================
    # Product Features
    # ===========================

   
    "product_review_volume_category",
]

# ==========================================================
# Gold Visualization Validator
# ==========================================================

class GoldVisualizationValidator:
    """
    Validates the Gold Visualization dataset before writing.
    """

    EXPECTED_COLUMNS = GOLD_VISUALIZATION_COLUMNS

    REQUIRED_COLUMNS = [
        "parent_asin",
        "review_rating",
        "review_date",
        "rating_category",
        "purchase_type",
    ]

    def __init__(self, df: DataFrame):
        self.df = df

    def validate_schema(self):

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

            logger.error("Schema validation failed.")

            logger.error(
                f"Missing Columns : {missing_columns}"
            )

            logger.error(
                f"Unexpected Columns : {extra_columns}"
            )

            raise ValueError(
                "Gold Visualization schema validation failed."
            )

        return self

    def validate_required_columns(self):

        for column_name in self.REQUIRED_COLUMNS:

            null_count = (
                self.df
                .filter(
                    col(column_name).isNull()
                )
                .count()
            )

            if null_count > 0:

                raise ValueError(
                    f"{column_name} contains {null_count} NULL values."
                )

        return self

    def validate_not_empty(self):

        if not self.df.take(1):

            raise ValueError(
                "Gold Visualization DataFrame is empty."
            )

        return self

    def run(self):

        return (
            self.validate_not_empty()
                .validate_schema()
                .validate_required_columns()
        )

# ==========================================================
# Pipeline
# ==========================================================

def run_pipeline(dataset_name: str) -> None:

    logger.info("=" * 80)
    logger.info(f"Processing Dataset : {dataset_name}")
    logger.info("=" * 80)

    silver_master_path = get_silver_master_path(dataset_name)
    gold_visualization_path = get_gold_visualization_path(dataset_name)

    df = read_parquet(silver_master_path)

    logger.info("Applying Gold Visualization transformations...")

    df = (
        GoldVisualizationTransformer(df)
        .transform()
    )

    df.cache()

    logger.info("Running validation checks...")

    try:

        (
            GoldVisualizationValidator(df)
            .run()
        )

        write_parquet(
            df=df,
            output_path=gold_visualization_path,
        )

    finally:

        df.unpersist()

    logger.info(
        f"{dataset_name} completed successfully."
    )

# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    try:

        logger.info("=" * 80)
        logger.info("Silver Master → Gold Visualization Glue Job Started")
        logger.info("=" * 80)

        for dataset in DATASETS:

            run_pipeline(dataset)

        logger.info("=" * 80)
        logger.info("All datasets processed successfully.")
        logger.info("=" * 80)

        job.commit()

    except Exception:

        logger.exception(
            "Gold Visualization Glue Job Failed."
        )

        raise

