"""
Project-wide constants used across the Bronze to Silver pipeline.

Only store reusable values here.
Do not define S3 paths in this file.
"""

# ---------------------------------------------------------------------
# S3 Configuration
# ---------------------------------------------------------------------

BUCKET_NAME = "amazon-review-analytics-group-2"

# ---------------------------------------------------------------------
# Metadata Processing
# ---------------------------------------------------------------------

CATEGORY_SEPARATOR = " | "

# ---------------------------------------------------------------------
# Numeric Configuration
# ---------------------------------------------------------------------

PRICE_PRECISION = 10
PRICE_SCALE = 2