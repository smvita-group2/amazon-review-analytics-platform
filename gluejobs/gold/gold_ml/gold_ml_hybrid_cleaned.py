"""
AWS Glue Job

Silver Master → Gold ML Hybrid Cleaned

Processes one or more datasets from the Silver Master layer,
cleans and validates the dataset for the Hybrid RAG pipeline,
and writes the cleaned dataset to Amazon S3.
"""

import logging
import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import DataFrame
from pyspark.sql.column import Column
from pyspark.sql.functions import (
    col,
    regexp_replace,
    trim,
    when,
)

# ==========================================================
# Glue Initialization
# ==========================================================

# ==========================================================
# Glue Initialization & Argument Parsing
# ==========================================================

# Parse JOB_NAME safely
args = getResolvedOptions(
    sys.argv,
    [
        "JOB_NAME",
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
# Datasets & Category Filter
# ==========================================================

category_param = None
if "--category" in sys.argv:
    idx = sys.argv.index("--category")
    if idx + 1 < len(sys.argv) and not sys.argv[idx + 1].startswith("--"):
        val = sys.argv[idx + 1].strip()
        if val:
            category_param = val

datasets_param = None
if "--datasets" in sys.argv:
    idx = sys.argv.index("--datasets")
    if idx + 1 < len(sys.argv) and not sys.argv[idx + 1].startswith("--"):
        val = sys.argv[idx + 1].strip()
        if val:
            datasets_param = val

if category_param:
    DATASETS = [category_param]
elif datasets_param:
    DATASETS = [d.strip() for d in datasets_param.split(",") if d.strip()]
else:
    DATASETS = ["Appliances", "Video_Games", "Musical_Instruments"]

logger.info(f"Datasets to process: {DATASETS}")


# ==========================================================
# Constants
# ==========================================================

BUCKET_NAME = "amazon-review-analytics-group-2"


# ==========================================================
# S3 Paths
# ==========================================================

S3_ROOT = f"s3://{BUCKET_NAME}"

SILVER_MASTER_ROOT = f"{S3_ROOT}/silver/master"

GOLD_ML_HYBRID_ROOT = f"{S3_ROOT}/gold/ml-hybrid-rag/cleaned"


def get_silver_master_path(dataset_name: str) -> str:
    return f"{SILVER_MASTER_ROOT}/{dataset_name}"


def get_gold_ml_hybrid_path(dataset_name: str) -> str:
    return f"{GOLD_ML_HYBRID_ROOT}/{dataset_name}"


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

    logger.info(f"Writing Gold ML Hybrid Cleaned Dataset: {output_path}")

    (df.write.mode("overwrite").option("compression", "snappy").parquet(output_path))


# ==========================================================
# Gold ML Hybrid Transformer
# ==========================================================


class GoldMLHybridTransformer:
    """
    Cleans the Silver Master dataset and prepares it
    for the Hybrid RAG pipeline.
    """

    SELECTED_COLUMNS = [
        "parent_asin",
        "user_id",
        "review_rating",
        "review_title",
        "review_text",
        "helpful_vote",
        "verified_purchase",
        "review_timestamp",
        "product_title",
        "store",
        "main_category",
        "sub_category",
        "product_average_rating",
        "product_rating_count",
        "description_text",
        "features_text",
        "product_image_url",
    ]

    TEXT_COLUMNS = [
        "review_title",
        "review_text",
        "product_title",
        "description_text",
        "features_text",
    ]

    def __init__(self, df: DataFrame):

        self.df = df

    def select_columns(self):

        self.df = self.df.select(*self.SELECTED_COLUMNS)

        return self

    def remove_duplicates(self):

        self.df = self.df.dropDuplicates(
            [
                "parent_asin",
                "user_id",
                "review_timestamp",
            ]
        )

        return self

    def clean_text_column(self, column_name: str) -> Column:
        """
        Cleans a text column by:
        - Replacing NULL values
        - Removing HTML tags
        - Decoding common HTML entities
        - Removing tabs, newlines and carriage returns
        - Removing non-printable characters
        - Collapsing multiple spaces
        - Trimming whitespace
        """

        cleaned = when(
            col(column_name).isNull(),
            "",
        ).otherwise(col(column_name))

        # Remove HTML tags
        cleaned = regexp_replace(cleaned, r"<[^>]+>", "")

        # Decode common HTML entities
        cleaned = regexp_replace(cleaned, "&amp;", "&")
        cleaned = regexp_replace(cleaned, r"&nbsp;|&#160;", " ")
        cleaned = regexp_replace(cleaned, "&quot;", '"')
        cleaned = regexp_replace(cleaned, "&apos;", "'")
        cleaned = regexp_replace(cleaned, "&lt;", "<")
        cleaned = regexp_replace(cleaned, "&gt;", ">")

        # Remove tabs, carriage returns and newlines
        cleaned = regexp_replace(cleaned, r"[\r\n\t]", " ")

        # Remove non-printable ASCII characters
        cleaned = regexp_replace(cleaned, r"[\x00-\x1F\x7F]", "")

        # Collapse multiple whitespace
        cleaned = regexp_replace(cleaned, r"\s+", " ")

        # Trim leading/trailing whitespace
        cleaned = trim(cleaned)

        return cleaned

    def clean_text_columns(self):

        for column_name in self.TEXT_COLUMNS:

            self.df = self.df.withColumn(
                column_name,
                self.clean_text_column(column_name),
            )

        return self

    def handle_null_values(self):

        self.df = self.df.fillna(
            {
                "review_title": "",
                "description_text": "",
                "features_text": "",
                "store": "Unknown",
                "sub_category": "Unknown",
                "product_image_url": "",
            }
        )

        return self

    def drop_invalid_rows(self):

        self.df = self.df.filter(
            (col("review_text") != "") & (col("product_title") != "")
        )

        return self

    def drop_unused_columns(self):

        self.df = self.df.drop(
            "user_id",
        )

        return self

    def transform(self) -> DataFrame:

        return (
            self.select_columns()
            .remove_duplicates()
            .clean_text_columns()
            .handle_null_values()
            .drop_invalid_rows()
            .drop_unused_columns()
            .df
        )


# ==========================================================
# Gold ML Hybrid Validator
# ==========================================================


class GoldMLHybridValidator:
    """
    Validates the Gold ML Hybrid dataset before writing.
    """

    EXPECTED_COLUMNS = [
        "parent_asin",
        "review_rating",
        "review_title",
        "review_text",
        "helpful_vote",
        "verified_purchase",
        "review_timestamp",
        "product_title",
        "store",
        "main_category",
        "sub_category",
        "product_average_rating",
        "product_rating_count",
        "description_text",
        "features_text",
        "product_image_url",
    ]

    REQUIRED_COLUMNS = [
        "parent_asin",
        "review_text",
        "product_title",
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

            raise ValueError("Gold ML Hybrid schema validation failed.")

        return self

    def validate_required_columns(self):

        for column_name in self.REQUIRED_COLUMNS:

            null_count = self.df.filter(col(column_name).isNull()).count()

            if null_count > 0:

                raise ValueError(f"{column_name} contains {null_count} NULL values.")

        return self

    def validate_not_empty(self):

        if not self.df.take(1):

            raise ValueError("Gold ML Hybrid DataFrame is empty.")

        return self

    def run(self):

        return self.validate_not_empty().validate_schema().validate_required_columns()


# ==========================================================
# Pipeline
# ==========================================================


def run_pipeline(dataset_name: str) -> None:

    logger.info(f"Processing Dataset : {dataset_name}")

    input_path = get_silver_master_path(dataset_name)

    output_path = get_gold_ml_hybrid_path(dataset_name)

    master_df = read_parquet(input_path)

    cleaned_df = GoldMLHybridTransformer(
        master_df,
    ).transform()

    # Cache cleaned DataFrame for validation and writing
    cleaned_df.cache()

    # Materialize cache
    cleaned_df.count()

    try:

        GoldMLHybridValidator(
            cleaned_df,
        ).run()

        write_parquet(
            df=cleaned_df,
            output_path=output_path,
        )

    finally:

        cleaned_df.unpersist()

    logger.info(f"Completed Dataset : {dataset_name}")


# ==========================================================
# Main
# ==========================================================


def main():

    logger.info("Starting Gold ML Hybrid Glue Job")

    try:

        for dataset_name in DATASETS:

            run_pipeline(dataset_name)

        logger.info("Gold ML Hybrid Glue Job Completed Successfully.")

        job.commit()

    except Exception:

        logger.exception("Gold ML Hybrid Glue Job Failed.")

        raise


if __name__ == "__main__":
    main()
