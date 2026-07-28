"""
AWS Glue Job

Silver Master → Gold Validated

Processes one or more Silver Master datasets,
validates data quality,
performs cleaning,
generates review statistics,
and writes the Gold Validated dataset back to Amazon S3.
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
    count,
    when,
    trim,
    length,
    split,
    size,
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

DEFAULT_STORE = "Unknown"

DEFAULT_SUB_CATEGORY = "Unknown"

DEFAULT_DESCRIPTION = ""

DEFAULT_FEATURES = ""

DEFAULT_PRICE = 0.0

DEFAULT_IMAGE = (
    "https://dummyimage.com/300x300/e5e7eb/6b7280.png&text=No+Image"
)

# ==========================================================
# S3 Paths
# ==========================================================

S3_ROOT = f"s3://{BUCKET_NAME}"

SILVER_MASTER_ROOT = f"{S3_ROOT}/silver/master"

GOLD_VALIDATED_ROOT = f"{S3_ROOT}/gold/validated"


def get_silver_master_path(dataset_name: str) -> str:
    return f"{SILVER_MASTER_ROOT}/{dataset_name}"


def get_gold_validated_path(dataset_name: str) -> str:
    return f"{GOLD_VALIDATED_ROOT}/{dataset_name}"


# ==========================================================
# Reader
# ==========================================================

def read_parquet(
    path: str,
) -> DataFrame:

    logger.info(f"Reading : {path}")

    return spark.read.parquet(path)

# ==========================================================
# Writer
# ==========================================================

def write_parquet(
    df: DataFrame,
    output_path: str,
) -> None:

    logger.info(
        f"Writing Gold Dataset : {output_path}"
    )

    (
        df.write
        .mode("overwrite")
        .option("compression", "snappy")
        .parquet(output_path)
    )

# ==========================================================
# Gold Validated Transformer
# ==========================================================

class GoldValidatedTransformer:
    """
    Cleans the Silver Master dataset and generates
    additional review statistics for the Gold layer.
    """

    def __init__(
        self,
        df: DataFrame,
    ):
        self.df = df

    def remove_duplicates(self):

        self.df = self.df.dropDuplicates()

        return self

    def fill_missing_values(self):

        self.df = self.df.fillna({

            "store": DEFAULT_STORE,

            "sub_category": DEFAULT_SUB_CATEGORY,

            "description_text": DEFAULT_DESCRIPTION,

            "features_text": DEFAULT_FEATURES,

            "product_price": DEFAULT_PRICE,

        })

        self.df = self.df.withColumn(

            "product_image_url",

            when(

                col("product_image_url").isNull()

                |

                (trim(col("product_image_url")) == ""),

                DEFAULT_IMAGE,

            ).otherwise(
                col("product_image_url")
            ),

        )

        return self

    def add_character_count(self):

        self.df = self.df.withColumn(

            "character_count",

            length(
                col("review_text")
            ),

        )

        return self

    def add_word_count(self):

        self.df = self.df.withColumn(

            "word_count",

            size(

                split(
                    col("review_text"),
                    " ",
                )

            ),

        )

        return self

    def add_sentence_count(self):

        self.df = self.df.withColumn(

            "sentence_count",

            size(

                split(

                    col("review_text"),

                    r"[.!?]+",

                )

            ),

        )

        return self

    def transform(self) -> DataFrame:

        return (

            self.remove_duplicates()

                .fill_missing_values()

                .add_character_count()

                .add_word_count()

                .add_sentence_count()

                .df

        )

# ==========================================================
# Gold Validated Validator
# ==========================================================

class GoldValidatedValidator:
    """
    Validates the dataset before writing.
    """

    SILVER_COLUMNS = [

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

    GOLD_COLUMNS = [

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
        "character_count",
        "word_count",
        "sentence_count",

    ]

    def __init__(
        self,
        df: DataFrame,
        expected_columns,
    ):

        self.df = df
        self.expected_columns = expected_columns

    # ------------------------------------------------------

    def validate_not_empty(self):

        if not self.df.take(1):

            raise ValueError(
                "DataFrame is empty."
            )

        return self

    # ------------------------------------------------------

    def validate_schema(self):

        actual_columns = self.df.columns

        missing_columns = [

            column

            for column in self.expected_columns

            if column not in actual_columns

        ]

        extra_columns = [

            column

            for column in actual_columns

            if column not in self.expected_columns

        ]

        if missing_columns or extra_columns:

            logger.error(
                f"Missing Columns : {missing_columns}"
            )

            logger.error(
                f"Unexpected Columns : {extra_columns}"
            )

            raise ValueError(
                "Schema validation failed."
            )

        logger.info(
            "Schema Validation Passed."
        )

        return self

    # ------------------------------------------------------

    def validate_duplicates(self):

        duplicate_count = (

            self.df.count()

            -

            self.df.dropDuplicates().count()

        )

        logger.info(
            f"Duplicate Records : {duplicate_count}"
        )

        return self

    # ------------------------------------------------------

    def validate_missing_values(self):

        logger.info(
            "Missing Value Analysis"
        )

        (

            self.df.select(

                [

                    count(

                        when(

                            col(column).isNull(),

                            column,

                        )

                    ).alias(column)

                    for column in self.df.columns

                ]

            )

            .show(truncate=False)

        )

        return self

    # ------------------------------------------------------

    def validate_review_rating(self):

        (

            self.df.groupBy(
                "review_rating"
            )

            .count()

            .orderBy(
                "review_rating"
            )

            .show()

        )

        invalid_rating = (

            self.df.filter(

                (col("review_rating") < 1)

                |

                (col("review_rating") > 5)

            )

            .count()

        )

        logger.info(
            f"Invalid Ratings : {invalid_rating}"
        )

        return self

    # ------------------------------------------------------

    def validate_verified_purchase(self):

        (

            self.df.groupBy(
                "verified_purchase"
            )

            .count()

            .show()

        )

        return self

    # ------------------------------------------------------

    def validate_empty_reviews(self):

        empty_reviews = (

            self.df.filter(

                col("review_text").isNull()

                |

                (

                    trim(
                        col("review_text")
                    ) == ""

                )

            )

            .count()

        )

        logger.info(
            f"Empty Reviews : {empty_reviews}"
        )

        return self

    # ------------------------------------------------------

    def run(self):

        return (

            self.validate_not_empty()

                .validate_schema()

                .validate_duplicates()

                .validate_missing_values()

                .validate_review_rating()

                .validate_verified_purchase()

                .validate_empty_reviews()

        )
# ==========================================================
# Pipeline
# ==========================================================

def run_pipeline(
    dataset_name: str,
) -> None:

    logger.info(
        f"Processing Dataset : {dataset_name}"
    )

    silver_master_path = (
        get_silver_master_path(
            dataset_name
        )
    )

    gold_validated_path = (
        get_gold_validated_path(
            dataset_name
        )
    )

    df = read_parquet(
        silver_master_path
    )

    df.cache()

    try:

        # Validate Silver Master Dataset
        GoldValidatedValidator(
            df,
            GoldValidatedValidator.SILVER_COLUMNS,
        ).run()

        # Transform to Gold Dataset
        gold_df = (
            GoldValidatedTransformer(
                df
            )
            .transform()
        )

        gold_df.cache()

        try:

            # Validate Gold Dataset
            GoldValidatedValidator(
                gold_df,
                GoldValidatedValidator.GOLD_COLUMNS,
            ).run()

            # Write Gold Dataset
            write_parquet(
                df=gold_df,
                output_path=gold_validated_path,
            )

        finally:

            gold_df.unpersist()

    finally:

        df.unpersist()

    logger.info(
        f"Completed Dataset : {dataset_name}"
    )
# ==========================================================
# Main
# ==========================================================

def main():

    logger.info(
        "Starting Gold Validation Glue Job"
    )

    try:

        for dataset_name in DATASETS:

            run_pipeline(
                dataset_name
            )

        logger.info(
            "Gold Validation Glue Job Completed Successfully."
        )

        job.commit()

    except Exception:

        logger.exception(
            "Gold Validation Glue Job Failed."
        )

        raise


if __name__ == "__main__":

    main()
