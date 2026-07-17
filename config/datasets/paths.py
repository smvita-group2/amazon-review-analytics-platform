"""
Dataset path configuration.

This module centralizes all dataset locations used across
local development and AWS EMR execution.
"""

# ============================================================
# SOURCE BUCKET (Read Only)
# ============================================================

SOURCE_BUCKET = "amazon-raw-data-group2"

RAW_REVIEWS_PATH = (
    f"s3://{SOURCE_BUCKET}/Sports_and_Outdoors.jsonl"
)

RAW_METADATA_PATH = (
    f"s3://{SOURCE_BUCKET}/meta_Sports_and_Outdoors.jsonl"
)


# ============================================================
# DESTINATION BUCKET (Your Data Lake)
# ============================================================

DESTINATION_BUCKET = "amazon-parquet-data-group2-shreyash"


# ---------------- Bronze ----------------

BRONZE_REVIEWS_PATH = (
    f"s3://{DESTINATION_BUCKET}/bronze/reviews/"
)

BRONZE_METADATA_PATH = (
    f"s3://{DESTINATION_BUCKET}/bronze/metadata/")


# ---------------- Sample ----------------

SAMPLE_REVIEWS_PATH = (
    f"s3://{DESTINATION_BUCKET}/sample/reviews/"
)

SAMPLE_METADATA_PATH = (
    f"s3://{DESTINATION_BUCKET}/sample/metadata/"
)


# ---------------- Silver ----------------

SILVER_REVIEWS_PATH = (
    f"s3://{DESTINATION_BUCKET}/silver/reviews/"
)

SILVER_METADATA_PATH = (
    f"s3://{DESTINATION_BUCKET}/silver/metadata/"
)


# ---------------- Gold ----------------

GOLD_ANALYTICS_PATH = (
    f"s3://{DESTINATION_BUCKET}/gold/analytics/"
)

GOLD_DASHBOARD_PATH = (
    f"s3://{DESTINATION_BUCKET}/gold/dashboard/"
)

GOLD_ML_PATH = (
    f"s3://{DESTINATION_BUCKET}/gold/ml/"
)


# ---------------- Reports ----------------

REPORTS_PATH = (
    f"s3://{DESTINATION_BUCKET}/reports/"
)