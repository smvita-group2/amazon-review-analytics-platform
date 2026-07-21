"""
Centralized S3 paths used by the Bronze to Silver pipeline.
"""

from config.datasets.constants import BUCKET_NAME

# ---------------------------------------------------------------------
# Root Paths
# ---------------------------------------------------------------------

S3_ROOT = f"s3://{BUCKET_NAME}"

BRONZE_ROOT = f"{S3_ROOT}/bronze"
SILVER_ROOT = f"{S3_ROOT}/silver"

# ---------------------------------------------------------------------
# Bronze Layer
# ---------------------------------------------------------------------

BRONZE_METADATA_ROOT = f"{BRONZE_ROOT}/metadata"
BRONZE_REVIEWS_ROOT = f"{BRONZE_ROOT}/reviews"

# ---------------------------------------------------------------------
# Silver Layer
# ---------------------------------------------------------------------

SILVER_METADATA_ROOT = f"{SILVER_ROOT}/metadata"
SILVER_REVIEWS_ROOT = f"{SILVER_ROOT}/reviews"


# ---------------------------------------------------------------------
# Dataset Path Builders
# ---------------------------------------------------------------------

def get_bronze_metadata_path(dataset_name: str) -> str:
    """
    Returns the Bronze metadata path for the given dataset.
    """
    return f"{BRONZE_METADATA_ROOT}/meta_{dataset_name}"


def get_bronze_reviews_path(dataset_name: str) -> str:
    """
    Returns the Bronze reviews path for the given dataset.
    """
    return f"{BRONZE_REVIEWS_ROOT}/{dataset_name}"


def get_silver_metadata_path(dataset_name: str) -> str:
    """
    Returns the Silver metadata output path.
    """
    return f"{SILVER_METADATA_ROOT}/{dataset_name}"


def get_silver_reviews_path(dataset_name: str) -> str:
    """
    Returns the Silver reviews output path.
    """
    return f"{SILVER_REVIEWS_ROOT}/{dataset_name}"