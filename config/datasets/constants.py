"""
Project-wide constants used across the Amazon Review Analytics Platform.

Only store reusable constants and business rules here.
Do not define S3 paths in this file.
"""

# ============================================================================
# S3 Configuration
# ============================================================================

BUCKET_NAME = "amazon-review-analytics-group-2"

# ============================================================================
# Metadata Processing
# ============================================================================

CATEGORY_SEPARATOR = " | "

# ============================================================================
# Numeric Configuration
# ============================================================================

PRICE_PRECISION = 10
PRICE_SCALE = 2

# ============================================================================
# Gold Visualization Business Rules
# ============================================================================

# Review year filter
START_YEAR = 2014
END_YEAR = 2023

# Minimum number of product reviews to be considered reliable
MIN_PRODUCT_REVIEW_THRESHOLD = 100

# ============================================================================
# Rating Categories
# ============================================================================

RATING_CATEGORY_MAPPING = {
    1: "Very Poor",
    2: "Poor",
    3: "Average",
    4: "Good",
    5: "Excellent",
}

# ============================================================================
# Helpfulness Buckets
# ============================================================================

HELPFULNESS_BUCKETS = {
    "NO_ENGAGEMENT": 0,
    "LOW_ENGAGEMENT": 1,
    "MODERATE_MIN": 2,
    "MODERATE_MAX": 5,
    "HIGH_MIN": 6,
    "HIGH_MAX": 20,
}

# Minimum helpful votes to consider a review helpful
MIN_HELPFUL_VOTES = 2

# ============================================================================
# Product Review Volume Buckets
# ============================================================================

PRODUCT_REVIEW_VOLUME_BUCKETS = {
    "VERY_LOW_MAX": 99,
    "LOW_MAX": 499,
    "MEDIUM_MAX": 2499,
    "HIGH_MAX": 9999,
}