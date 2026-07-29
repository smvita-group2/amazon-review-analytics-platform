"""
Dataset schemas and expected column definitions used throughout the project.
"""

from pyspark.sql.types import (BooleanType, DateType, DoubleType, IntegerType,
                               LongType, StringType, StructField, StructType,
                               TimestampType)

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

SILVER_METADATA_SCHEMA = StructType(
    [
        StructField("parent_asin", StringType(), False),
        StructField("product_title", StringType(), True),
        StructField("store", StringType(), True),
        StructField("main_category", StringType(), True),
        StructField("sub_category", StringType(), True),
        StructField("product_price", DoubleType(), True),
        StructField("product_average_rating", DoubleType(), True),
        StructField("product_rating_count", LongType(), True),
        StructField("description_text", StringType(), True),
        StructField("features_text", StringType(), True),
        StructField("product_image_url", StringType(), True),
    ]
)

# ---------------------------------------------------------------------
# Silver Reviews Schema
# ---------------------------------------------------------------------

SILVER_REVIEWS_SCHEMA = StructType(
    [
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
    ]
)

# ---------------------------------------------------------------------
# Silver Master Columns
# ---------------------------------------------------------------------

SILVER_MASTER_COLUMNS = [
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

# ---------------------------------------------------------------------
# Gold Visualization Columns
# ---------------------------------------------------------------------

GOLD_VISUALIZATION_COLUMNS = [
    # =====================================================
    # Product Information
    # =====================================================
    "parent_asin",
    "product_title",
    "store",
    "main_category",
    "sub_category",
    "product_average_rating",
    "product_rating_count",
    "product_review_volume_category",
    "review_count_threshold_met",
    # =====================================================
    # Review Information
    # =====================================================
    "review_rating",
    "rating_category",
    "review_length",
    "review_word_count",
    # =====================================================
    # Helpfulness
    # =====================================================
    "helpful_vote",
    "helpful_vote_bucket",
    "is_helpful",
    # =====================================================
    # Purchase Information
    # =====================================================
    "verified_purchase",
    "purchase_type",
    # =====================================================
    # Time Information
    # =====================================================
    "review_date",
    "review_year",
    "review_quarter",
    "review_month",
    "review_month_name",
    "review_year_month",
    "review_day_of_week",
]
