"""
AWS Glue Job
Gold ML Layer

Silver Master (Glue Catalog)
    -> Remove HTML tags from review_text
    -> Write to Gold ML (S3)

Author: Team Project
"""

import sys
import logging

from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job

from pyspark.context import SparkContext
from pyspark.sql import DataFrame
from pyspark.sql.functions import regexp_replace, col

# ==========================================================
# Glue Initialization
# ==========================================================

args = getResolvedOptions(sys.argv, ["JOB_NAME"])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# ==========================================================
# Logging
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# ==========================================================
# Configuration
# ==========================================================

DATABASE_NAME = "amazon_review_analytics"
TABLE_NAME = "master"

BUCKET_NAME = "amazon-review-analytics-group-2"
OUTPUT_ROOT = f"s3://{BUCKET_NAME}/gold/ml"

PARTITION_COLUMN = "partition_0"

# ==========================================================
# Reader
# ==========================================================

class Reader:

    @staticmethod
    def read_master() -> DataFrame:
        logger.info("Reading master table from Glue Catalog")
        return (
            glueContext.create_dynamic_frame.from_catalog(
                database=DATABASE_NAME,
                table_name=TABLE_NAME,
            ).toDF()
        )

# ==========================================================
# Transformer
# ==========================================================

class GoldMLTransformer:

    HTML_REGEX = r"<[^>]+>"

    def __init__(self, df: DataFrame):
        self.df = df

    def remove_html(self):
        logger.info("Removing HTML tags")
        self.df = self.df.withColumn(
            "review_text",
            regexp_replace(col("review_text"), self.HTML_REGEX, "")
        )
        return self

    def transform(self):
        return self.remove_html().df

# ==========================================================
# Validator
# ==========================================================

class Validator:

    REQUIRED_COLUMNS = [
        "parent_asin",
        "user_id",
        "review_text",
    ]

    @staticmethod
    def validate(df: DataFrame):

        if df.rdd.isEmpty():
            raise Exception("DataFrame is empty")

        for c in Validator.REQUIRED_COLUMNS:
            if c not in df.columns:
                raise Exception(f"Missing column : {c}")

# ==========================================================
# Writer
# ==========================================================

class Writer:

    @staticmethod
    def write(df: DataFrame, dataset_name: str):

        output_path = f"{OUTPUT_ROOT}/{dataset_name}"

        logger.info(f"Writing -> {output_path}")

        (
            df.write
            .mode("overwrite")
            .option("compression", "snappy")
            .parquet(output_path)
        )

# ==========================================================
# Pipeline
# ==========================================================

def get_datasets(df: DataFrame):

    return [
        row[PARTITION_COLUMN]
        for row in (
            df.select(PARTITION_COLUMN)
              .distinct()
              .collect()
        )
    ]


def process_dataset(master_df: DataFrame, dataset_name: str):

    logger.info(f"Processing {dataset_name}")

    dataset_df = master_df.filter(
        col(PARTITION_COLUMN) == dataset_name
    )

    transformed_df = (
        GoldMLTransformer(dataset_df)
        .transform()
    )

    Validator.validate(transformed_df)

    Writer.write(
        transformed_df,
        dataset_name
    )


def main():

    logger.info("Starting Gold ML Job")

    master_df = Reader.read_master()

    datasets = get_datasets(master_df)

    logger.info(f"Datasets Found : {datasets}")

    for dataset in datasets:
        process_dataset(master_df, dataset)

    logger.info("Gold ML Job Completed")

    job.commit()


if __name__ == "__main__":
    main()
