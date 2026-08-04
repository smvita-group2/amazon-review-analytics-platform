"""
AWS Glue Job

Gold Visualization → Gold Aggregates

Processes one or more datasets from the Gold Visualization layer,
creates aggregated datasets for Business Intelligence,
validates each aggregate,
and writes them back to Amazon S3.
"""

import logging
import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import DataFrame
from pyspark.sql.functions import avg, col, count, countDistinct, round, sum, when

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

GOLD_VISUALIZATION_ROOT = f"{S3_ROOT}/gold/visualization"

GOLD_AGGREGATES_ROOT = f"{S3_ROOT}/gold/aggregates"


def get_gold_visualization_path(dataset_name: str) -> str:

    return f"{GOLD_VISUALIZATION_ROOT}/{dataset_name}"


def get_product_summary_path(dataset_name: str) -> str:

    return f"{GOLD_AGGREGATES_ROOT}" f"/product_summary/dataset={dataset_name}"


def get_monthly_summary_path(dataset_name: str) -> str:

    return f"{GOLD_AGGREGATES_ROOT}" f"/monthly_summary/dataset={dataset_name}"


def get_category_summary_path(dataset_name: str) -> str:

    return f"{GOLD_AGGREGATES_ROOT}" f"/category_summary/dataset={dataset_name}"


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
    table_name: str,
) -> None:

    logger.info(f"Writing {table_name}: {output_path}")

    (df.write.mode("overwrite").option("compression", "snappy").parquet(output_path))


# ==========================================================
# Gold Aggregate Transformer
# ==========================================================


class GoldAggregateTransformer:
    """
    Creates aggregated datasets for Business Intelligence.
    """

    def __init__(self, df: DataFrame):
        self.df = df

    def product_summary(self) -> DataFrame:

        return self.df.groupBy(
            "parent_asin",
            "product_title",
            "store",
            "main_category",
            "sub_category",
            "product_average_rating",
            "product_rating_count",
            "product_image_url",
        ).agg(
            round(
                avg("review_rating"),
                2,
            ).alias("average_review_rating"),
            count("*").alias("total_reviews"),
            round(
                avg("helpful_vote"),
                2,
            ).alias("average_helpful_votes"),
            round(
                avg("review_length"),
                2,
            ).alias("average_review_length"),
            round(
                avg(
                    when(
                        col("verified_purchase"),
                        1,
                    ).otherwise(0)
                )
                * 100,
                2,
            ).alias("verified_purchase_percentage"),
            sum(
                when(
                    col("rating_category") == "Positive",
                    1,
                ).otherwise(0)
            ).alias("positive_reviews"),
            sum(
                when(
                    col("rating_category") == "Neutral",
                    1,
                ).otherwise(0)
            ).alias("neutral_reviews"),
            sum(
                when(
                    col("rating_category") == "Negative",
                    1,
                ).otherwise(0)
            ).alias("negative_reviews"),
        )

    def monthly_summary(self) -> DataFrame:

        return (
            self.df.groupBy(
                "review_year",
                "review_month",
                "review_year_month",
            )
            .agg(
                count("*").alias("total_reviews"),
                round(
                    avg("review_rating"),
                    2,
                ).alias("average_rating"),
                round(
                    avg("review_length"),
                    2,
                ).alias("average_review_length"),
                round(
                    avg(
                        when(
                            col("verified_purchase"),
                            1,
                        ).otherwise(0)
                    )
                    * 100,
                    2,
                ).alias("verified_purchase_percentage"),
                sum(
                    when(
                        col("rating_category") == "Positive",
                        1,
                    ).otherwise(0)
                ).alias("positive_reviews"),
                sum(
                    when(
                        col("rating_category") == "Neutral",
                        1,
                    ).otherwise(0)
                ).alias("neutral_reviews"),
                sum(
                    when(
                        col("rating_category") == "Negative",
                        1,
                    ).otherwise(0)
                ).alias("negative_reviews"),
            )
            .orderBy(
                "review_year",
                "review_month",
            )
        )

    def category_summary(self) -> DataFrame:

        return (
            self.df.groupBy(
                "main_category",
                "sub_category",
            )
            .agg(
                countDistinct(
                    "parent_asin",
                ).alias("total_products"),
                count("*").alias("total_reviews"),
                round(
                    avg("review_rating"),
                    2,
                ).alias("average_rating"),
                round(
                    avg("helpful_vote"),
                    2,
                ).alias("average_helpful_votes"),
                round(
                    avg("review_length"),
                    2,
                ).alias("average_review_length"),
                round(
                    avg(
                        when(
                            col("verified_purchase"),
                            1,
                        ).otherwise(0)
                    )
                    * 100,
                    2,
                ).alias("verified_purchase_percentage"),
                sum(
                    when(
                        col("rating_category") == "Positive",
                        1,
                    ).otherwise(0)
                ).alias("positive_reviews"),
                sum(
                    when(
                        col("rating_category") == "Neutral",
                        1,
                    ).otherwise(0)
                ).alias("neutral_reviews"),
                sum(
                    when(
                        col("rating_category") == "Negative",
                        1,
                    ).otherwise(0)
                ).alias("negative_reviews"),
            )
            .orderBy(
                "total_reviews",
                ascending=False,
            )
        )


# ==========================================================
# Aggregate Validator
# ==========================================================


class AggregateValidator:

    def __init__(
        self,
        df: DataFrame,
        table_name: str,
    ):
        self.df = df
        self.table_name = table_name

    def validate_not_empty(self):

        if not self.df.take(1):

            raise ValueError(f"{self.table_name} is empty.")

        return self

    def validate_columns(self):

        if len(self.df.columns) == 0:

            raise ValueError(f"{self.table_name} has no columns.")

        return self

    def run(self):

        return self.validate_not_empty().validate_columns()


# ==========================================================
# Pipeline
# ==========================================================


def run_pipeline(dataset_name: str) -> None:

    logger.info("=" * 80)
    logger.info(f"Processing Dataset : {dataset_name}")
    logger.info("=" * 80)

    visualization_path = get_gold_visualization_path(dataset_name)

    logger.info(f"Input Path : {visualization_path}")

    df = read_parquet(visualization_path)

    transformer = GoldAggregateTransformer(df)

    product_summary_df = transformer.product_summary()

    monthly_summary_df = transformer.monthly_summary()

    category_summary_df = transformer.category_summary()

    datasets = [
        (
            product_summary_df,
            get_product_summary_path(dataset_name),
            "Product Summary",
        ),
        (
            monthly_summary_df,
            get_monthly_summary_path(dataset_name),
            "Monthly Summary",
        ),
        (
            category_summary_df,
            get_category_summary_path(dataset_name),
            "Category Summary",
        ),
    ]

    for aggregate_df, output_path, table_name in datasets:

        aggregate_df = aggregate_df.coalesce(1)

        logger.info(f"Validating {table_name}...")

        logger.info(f"Output Path : {output_path}")

        try:

            (
                AggregateValidator(
                    aggregate_df,
                    table_name,
                ).run()
            )

            write_parquet(
                df=aggregate_df,
                output_path=output_path,
                table_name=table_name,
            )

            logger.info(f"{table_name} written successfully.")

        except Exception:

            logger.exception(f"Failed while processing {table_name}")

            raise

    logger.info(f"{dataset_name} completed successfully.")


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    try:

        logger.info("=" * 80)
        logger.info("Gold Visualization → Gold Aggregates Glue Job Started")
        logger.info("=" * 80)

        for dataset in DATASETS:

            run_pipeline(dataset)

        logger.info("=" * 80)
        logger.info("All datasets processed successfully.")
        logger.info("=" * 80)

        job.commit()

    except Exception:

        logger.exception("Gold Aggregates Glue Job Failed.")

        raise
