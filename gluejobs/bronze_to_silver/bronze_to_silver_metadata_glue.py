"""
AWS Glue Job

Bronze Metadata → Silver Metadata

Processes one or more datasets from the Bronze layer,
applies metadata transformations and validations,
and writes the Silver metadata dataset back to Amazon S3.
"""

import sys
import logging

from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job

from pyspark.context import SparkContext

from pyspark.sql import DataFrame

from pyspark.sql.functions import (
    array_join,
    col,
    coalesce,
    regexp_replace,
    size,
    slice,
    trim,
    when,
    lit,
)

from pyspark.sql.types import DecimalType


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

DATASETS = [
    dataset.strip()
    for dataset in args["datasets"].split(",")
]


# ==========================================================
# Constants
# ==========================================================

BUCKET_NAME = "amazon-review-analytics-group-2"

CATEGORY_SEPARATOR = " | "

PRICE_PRECISION = 10
PRICE_SCALE = 2


# ==========================================================
# S3 Paths
# ==========================================================

S3_ROOT = f"s3://{BUCKET_NAME}"

BRONZE_METADATA_ROOT = f"{S3_ROOT}/bronze/metadata"

SILVER_METADATA_ROOT = f"{S3_ROOT}/silver/metadata"


def get_bronze_metadata_path(dataset_name: str) -> str:
    return f"{BRONZE_METADATA_ROOT}/meta_{dataset_name}"


def get_silver_metadata_path(dataset_name: str) -> str:
    return f"{SILVER_METADATA_ROOT}/{dataset_name}"


# ==========================================================
# Reader
# ==========================================================

def read_parquet(path: str) -> DataFrame:

    logger.info(f"Reading Bronze Metadata: {path}")

    return spark.read.parquet(path)


# ==========================================================
# Writer
# ==========================================================

def write_parquet(
    df: DataFrame,
    output_path: str,
) -> None:

    logger.info(f"Writing Silver Metadata: {output_path}")

    (
        df.write
        .mode("overwrite")
        .option("compression", "snappy")
        .parquet(output_path)
    )

# ==========================================================
# Metadata Transformer
# ==========================================================

class MetadataTransformer:
    """
    Applies all transformations required to convert Bronze metadata
    into the standardized Silver schema.
    """

    def __init__(
        self,
        df: DataFrame,
        dataset_name: str,
    ):
        self.df = df
        self.dataset_name = dataset_name

    def rename_columns(self):

        self.df = (
            self.df
            .withColumnRenamed("title", "product_title")
            .withColumnRenamed("average_rating", "product_average_rating")
            .withColumnRenamed("rating_number", "product_rating_count")
            .withColumnRenamed("description", "description_text")
            .withColumnRenamed("features", "features_text")
            .withColumnRenamed("price", "product_price")
        )

        return self

    def drop_unused_columns(self):

        self.df = self.df.drop(
            "author",
            "bought_together",
            "subtitle",
            "videos",
            "details",
        )

        return self

    def clean_price(self):

        self.df = self.df.withColumn(
            "product_price",
            regexp_replace(
                col("product_price"),
                r"[^0-9.]",
                "",
            ).cast(
                DecimalType(
                    PRICE_PRECISION,
                    PRICE_SCALE,
                )
            ),
        )

        return self

    def extract_primary_image(self):

        self.df = (
            self.df
            .withColumn(
                "product_image_url",
                coalesce(
                    col("images").getItem(0).getField("hi_res"),
                    col("images").getItem(0).getField("large"),
                ),
            )
            .drop("images")
        )

        return self

    def flatten_description(self):

        self.df = self.df.withColumn(
            "description_text",
            when(
                col("description_text").isNull()
                | (size(col("description_text")) == 0),
                None,
            ).otherwise(
                array_join(
                    col("description_text"),
                    " ",
                )
            ),
        )

        return self

    def flatten_features(self):

        self.df = self.df.withColumn(
            "features_text",
            when(
                col("features_text").isNull()
                | (size(col("features_text")) == 0),
                None,
            ).otherwise(
                array_join(
                    col("features_text"),
                    CATEGORY_SEPARATOR,
                )
            ),
        )

        return self

    def standardize_categories(self):

        self.df = (
            self.df
            .drop("main_category")
            .withColumn(
                "main_category",
                lit(self.dataset_name),
            )
            .withColumn(
                "sub_category",
                when(
                    col("categories").isNull()
                    | (size(col("categories")) <= 1),
                    None,
                ).otherwise(
                    array_join(
                        slice(
                            col("categories"),
                            2,
                            size(col("categories")) - 1,
                        ),
                        CATEGORY_SEPARATOR,
                    )
                ),
            )
            .drop("categories")
        )

        return self

    def standardize_store(self):

        self.df = self.df.withColumn(
            "store",
            when(
                trim(col("store")) == "",
                None,
            ).otherwise(
                trim(col("store"))
            ),
        )

        return self

    def clean_product_title(self):

        self.df = self.df.withColumn(
            "product_title",
            when(
                trim(col("product_title")) == "",
                None,
            ).otherwise(
                trim(col("product_title"))
            ),
        )

        return self

    def reorder_columns(self):

        self.df = self.df.select(
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
        )

        return self

    def transform(self) -> DataFrame:

        return (
            self.rename_columns()
                .drop_unused_columns()
                .clean_price()
                .extract_primary_image()
                .flatten_description()
                .flatten_features()
                .standardize_categories()
                .standardize_store()
                .clean_product_title()
                .reorder_columns()
                .df
        )

# ==========================================================
# Metadata Validator
# ==========================================================

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

        duplicate_count = (
            self.df
            .groupBy("parent_asin")
            .count()
            .filter(col("count") > 1)
            .count()
        )

        if duplicate_count > 0:
            raise ValueError(
                f"Found {duplicate_count} duplicate parent_asin values."
            )

        return self

    def validate_required_columns(self):

        for column_name in self.REQUIRED_COLUMNS:

            null_count = (
                self.df
                .filter(col(column_name).isNull())
                .count()
            )

            if null_count > 0:
                raise ValueError(
                    f"{column_name} contains {null_count} NULL values."
                )

        return self

    def validate_rating_range(self):

        invalid_count = (
            self.df
            .filter(
                col("product_average_rating").isNotNull()
                &
                (
                    (col("product_average_rating") < 0)
                    |
                    (col("product_average_rating") > 5)
                )
            )
            .count()
        )

        if invalid_count > 0:
            raise ValueError(
                f"Found {invalid_count} invalid ratings."
            )

        return self

    def validate_rating_count(self):

        invalid_count = (
            self.df
            .filter(
                col("product_rating_count").isNotNull()
                &
                (col("product_rating_count") < 0)
            )
            .count()
        )

        if invalid_count > 0:
            raise ValueError(
                f"Found {invalid_count} negative rating counts."
            )

        return self

    def validate_price(self):

        invalid_count = (
            self.df
            .filter(
                col("product_price").isNotNull()
                &
                (col("product_price") < 0)
            )
            .count()
        )

        if invalid_count > 0:
            raise ValueError(
                f"Found {invalid_count} negative prices."
            )

        return self

    def run(self):

        (
            self.validate_schema()
                .validate_duplicate_parent_asin()
                .validate_required_columns()
                .validate_rating_range()
                .validate_rating_count()
                .validate_price()
        )

# ==========================================================
# Pipeline
# ==========================================================

def run_pipeline(dataset_name: str) -> None:

    logger.info("=" * 80)
    logger.info(f"Processing Dataset : {dataset_name}")
    logger.info("=" * 80)

    bronze_path = get_bronze_metadata_path(dataset_name)
    silver_path = get_silver_metadata_path(dataset_name)

    df = read_parquet(bronze_path)

    logger.info("Applying metadata transformations...")

    df = (
        MetadataTransformer(df,dataset_name,)
        .transform()
    )
 
    df.cache()
       
    logger.info("Running validation checks...")

    (
        MetadataValidator(df)
        .run()
    )

    write_parquet(
        df=df,
        output_path=silver_path,
    )

    df.unpersist()
    
    logger.info(
        f"{dataset_name} completed successfully."
    )# ==========================================================
# Pipeline
# ==========================================================

def run_pipeline(dataset_name: str) -> None:

    logger.info("=" * 80)
    logger.info(f"Processing Dataset : {dataset_name}")
    logger.info("=" * 80)

    bronze_path = get_bronze_metadata_path(dataset_name)
    silver_path = get_silver_metadata_path(dataset_name)

    df = read_parquet(bronze_path)

    logger.info("Applying metadata transformations...")

    df = (
        MetadataTransformer(
            df,
            dataset_name,
        )
        .transform()
    )

    df.cache()

    logger.info("Running validation checks...")

    try:

        (
            MetadataValidator(df)
            .run()
        )

        write_parquet(
            df=df,
            output_path=silver_path,
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
        logger.info("Bronze → Silver Metadata Glue Job Started")
        logger.info("=" * 80)

        for dataset in DATASETS:

            run_pipeline(dataset)

        logger.info("=" * 80)
        logger.info("All datasets processed successfully.")
        logger.info("=" * 80)

        job.commit()

    except Exception:

        logger.exception("Glue Job Failed")

        raise 
