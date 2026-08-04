"""
AWS Glue Job

Silver Reviews + Silver Metadata → Silver Master

Processes one or more datasets from the Silver layer,
joins the Silver Reviews and Silver Metadata datasets,
validates the Silver Master dataset,
and writes the Silver Master dataset back to Amazon S3.
"""

import logging
import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import DataFrame
from pyspark.sql.functions import col

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

SILVER_METADATA_ROOT = f"{S3_ROOT}/silver/metadata"

SILVER_REVIEWS_ROOT = f"{S3_ROOT}/silver/reviews"

SILVER_MASTER_ROOT = f"{S3_ROOT}/silver/master"


def get_silver_metadata_path(dataset_name: str) -> str:
    return f"{SILVER_METADATA_ROOT}/{dataset_name}"


def get_silver_reviews_path(dataset_name: str) -> str:
    return f"{SILVER_REVIEWS_ROOT}/{dataset_name}"


def get_silver_master_path(dataset_name: str) -> str:
    return f"{SILVER_MASTER_ROOT}/{dataset_name}"


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

    logger.info(f"Writing Silver Master: {output_path}")

    (df.write.mode("overwrite").option("compression", "snappy").parquet(output_path))


# ==========================================================
# Silver Master Transformer
# ==========================================================


class SilverMasterTransformer:
    """
    Creates the Silver Master dataset by joining
    the Silver Reviews and Silver Metadata datasets.
    """

    def __init__(
        self,
        reviews_df: DataFrame,
        metadata_df: DataFrame,
    ):
        self.reviews_df = reviews_df
        self.metadata_df = metadata_df

    def transform(self) -> DataFrame:
        """
        Joins the Silver Reviews and Silver Metadata
        datasets into a single Silver Master dataset.
        """

        return self.reviews_df.join(
            self.metadata_df,
            on="parent_asin",
            how="inner",
        )


# ==========================================================
# Silver Master Validator
# ==========================================================


class SilverMasterValidator:
    """
    Validates the Silver Master dataset before writing.
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
        "user_id",
        "review_rating",
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

            raise ValueError("Silver Master schema validation failed.")

        return self

    def validate_required_columns(self):

        for column_name in self.REQUIRED_COLUMNS:

            null_count = self.df.filter(col(column_name).isNull()).count()

            if null_count > 0:

                raise ValueError(f"{column_name} contains {null_count} NULL values.")

        return self

    def validate_not_empty(self):

        if not self.df.take(1):

            raise ValueError("Silver Master DataFrame is empty.")

        return self

    def run(self):

        return self.validate_not_empty().validate_schema().validate_required_columns()


# ==========================================================
# Pipeline
# ==========================================================


def run_pipeline(dataset_name: str) -> None:

    logger.info(f"Processing Dataset : {dataset_name}")

    reviews_path = get_silver_reviews_path(dataset_name)

    metadata_path = get_silver_metadata_path(dataset_name)

    master_path = get_silver_master_path(dataset_name)

    reviews_df = read_parquet(reviews_path)

    metadata_df = read_parquet(metadata_path)

    master_df = SilverMasterTransformer(
        reviews_df=reviews_df,
        metadata_df=metadata_df,
    ).transform()

    master_df.cache()

    try:

        SilverMasterValidator(master_df).run()

        write_parquet(
            df=master_df,
            output_path=master_path,
        )

    finally:

        master_df.unpersist()

    logger.info(f"Completed Dataset : {dataset_name}")


# ==========================================================
# Main
# ==========================================================


def main():

    logger.info("Starting Silver Master Glue Job")

    try:

        for dataset_name in DATASETS:

            run_pipeline(dataset_name)

        logger.info("Silver Master Glue Job Completed Successfully.")

        job.commit()

    except Exception:

        logger.exception("Silver Master Glue Job Failed.")

        raise


if __name__ == "__main__":
    main()
