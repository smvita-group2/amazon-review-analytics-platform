"""
Centralized S3 paths used across the Medallion Architecture.

Bronze
    ├── metadata
    └── reviews

Silver
    ├── metadata
    ├── reviews
    └── master

Gold
    ├── visualization
    └── ml
"""

from config.datasets.constants import BUCKET_NAME

# ============================================================================
# Root Paths
# ============================================================================

S3_ROOT = f"s3://{BUCKET_NAME}"

BRONZE_ROOT = f"{S3_ROOT}/bronze"
SILVER_ROOT = f"{S3_ROOT}/silver"
GOLD_ROOT = f"{S3_ROOT}/gold"

# ============================================================================
# Bronze Layer
# ============================================================================

BRONZE_METADATA_ROOT = f"{BRONZE_ROOT}/metadata"
BRONZE_REVIEWS_ROOT = f"{BRONZE_ROOT}/reviews"

# ============================================================================
# Silver Layer
# ============================================================================

SILVER_METADATA_ROOT = f"{SILVER_ROOT}/metadata"
SILVER_REVIEWS_ROOT = f"{SILVER_ROOT}/reviews"
SILVER_MASTER_ROOT = f"{SILVER_ROOT}/master"

# ============================================================================
# Gold Layer
# ============================================================================

GOLD_VISUALIZATION_ROOT = f"{GOLD_ROOT}/visualization"
GOLD_ML_ROOT = f"{GOLD_ROOT}/ml"

# ============================================================================
# Bronze Path Builders
# ============================================================================

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


# ============================================================================
# Silver Path Builders
# ============================================================================

def get_silver_metadata_path(dataset_name: str) -> str:
    """
    Returns the Silver metadata path for the given dataset.
    """
    return f"{SILVER_METADATA_ROOT}/{dataset_name}"


def get_silver_reviews_path(dataset_name: str) -> str:
    """
    Returns the Silver reviews path for the given dataset.
    """
    return f"{SILVER_REVIEWS_ROOT}/{dataset_name}"


def get_silver_master_path(dataset_name: str) -> str:
    """
    Returns the Silver Master dataset path.
    """
    return f"{SILVER_MASTER_ROOT}/{dataset_name}"


# ============================================================================
# Gold Path Builders
# ============================================================================

def get_gold_visualization_path(dataset_name: str) -> str:
    """
    Returns the Gold Visualization dataset path.
    """
    return f"{GOLD_VISUALIZATION_ROOT}/{dataset_name}"


def get_gold_ml_path(dataset_name: str) -> str:
    """
    Returns the Gold ML dataset path.
    """
    return f"{GOLD_ML_ROOT}/{dataset_name}"