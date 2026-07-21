"""
Dataset schemas used throughout the ingestion pipeline.
"""

from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    IntegerType,
    BooleanType,
    TimestampType,
    DateType
)

# ---------------------------------------------------------------------
# Bronze Columns
# ---------------------------------------------------------------------

REVIEWS_COLUMNS = [
    "rating",
    "title",
    "text",
    "images",
    "asin",
    "parent_asin",
    "user_id",
    "timestamp",
    "helpful_vote",
    "verified_purchase",
]

METADATA_COLUMNS = [
    "parent_asin",
    "title",
    "main_category",
    "average_rating",
    "rating_number",
    "store",
    "categories",
]

# ---------------------------------------------------------------------
# Silver Metadata Schema
# ---------------------------------------------------------------------

SILVER_METADATA_SCHEMA = StructType([
    StructField("parent_asin", StringType(), False),
    StructField("product_title", StringType(), True),
    StructField("store", StringType(), True),
    StructField("main_category", StringType(), True),
    StructField("sub_category", StringType(), True),
    StructField("product_price", DoubleType(), True),
    StructField("product_average_rating", DoubleType(), True),
    StructField("product_rating_count", IntegerType(), True),
    StructField("description_text", StringType(), True),
    StructField("features_text", StringType(), True),
    StructField("product_image_url", StringType(), True),
])

# ---------------------------------------------------------------------
# Silver Reviews Schema
# ---------------------------------------------------------------------

SILVER_REVIEWS_SCHEMA = StructType([
    StructField("parent_asin", StringType(), False),
    StructField("user_id", StringType(), False),
    StructField("review_rating", DoubleType(), False),
    StructField("review_title", StringType(), True),
    StructField("review_text", StringType(), True),
    StructField("helpful_vote", IntegerType(), True),
    StructField("verified_purchase", BooleanType(), True),
    StructField("review_timestamp", TimestampType(), False),
    StructField("review_date", DateType(), True),
    StructField("review_year", IntegerType(), True),
    StructField("review_month", IntegerType(), True),
])