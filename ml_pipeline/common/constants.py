"""
Project Constants

Shared constants used across the ML pipeline.

Only values that are truly constant across the project
should live here.
"""

# ==========================================================
# DataFrame Column Names
# ==========================================================

PARENT_ASIN = "parent_asin"

REVIEW_RATING = "review_rating"
REVIEW_TITLE = "review_title"
REVIEW_TEXT = "review_text"
HELPFUL_VOTE = "helpful_vote"
VERIFIED_PURCHASE = "verified_purchase"
REVIEW_TIMESTAMP = "review_timestamp"

PRODUCT_TITLE = "product_title"
STORE = "store"
MAIN_CATEGORY = "main_category"
SUB_CATEGORY = "sub_category"

PRODUCT_AVERAGE_RATING = "product_average_rating"
PRODUCT_RATING_COUNT = "product_rating_count"

DESCRIPTION_TEXT = "description_text"
FEATURES_TEXT = "features_text"

PRODUCT_IMAGE_URL = "product_image_url"

# ==========================================================
# Generated Columns
# ==========================================================

PRODUCT_DOCUMENT = "product_document"

DOCUMENT_ID = "document_id"

EMBEDDING = "embedding"

# ==========================================================
# Metadata Keys
# ==========================================================

METADATA_PARENT_ASIN = "parent_asin"
METADATA_PRODUCT_TITLE = "product_title"
METADATA_STORE = "store"
METADATA_MAIN_CATEGORY = "main_category"
METADATA_SUB_CATEGORY = "sub_category"
METADATA_PRODUCT_AVERAGE_RATING = "product_average_rating"

# ==========================================================
# File Formats
# ==========================================================

PARQUET = "parquet"

CSV = "csv"

JSON = "json"