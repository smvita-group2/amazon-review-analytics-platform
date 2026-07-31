"""
Amazon S3 DataFrame I/O Utilities

Provides helper functions for reading and writing
Pandas DataFrames directly from Amazon S3.
"""

import pandas as pd

from common.config import get_setting
from common.logger import get_logger

logger = get_logger(__name__)

# ==========================================================
# AWS Configuration
# ==========================================================

_BUCKET = get_setting(
    "aws",
    "bucket_name",
)

# ==========================================================
# Helpers
# ==========================================================


def _build_s3_path(
    s3_key: str,
) -> str:
    """
    Build a full S3 URI from an object key.
    """

    return f"s3://{_BUCKET}/{s3_key}"


# ==========================================================
# Read Parquet
# ==========================================================


def read_parquet_from_s3(
    s3_key: str,
) -> pd.DataFrame:
    """
    Read a parquet dataset from Amazon S3.
    """

    path = _build_s3_path(s3_key)

    logger.info(f"Reading parquet from {path}")

    return pd.read_parquet(path)


# ==========================================================
# Write Parquet
# ==========================================================


def write_parquet_to_s3(
    dataframe: pd.DataFrame,
    s3_key: str,
) -> None:
    """
    Write a dataframe as parquet to Amazon S3.
    """

    path = _build_s3_path(s3_key)

    logger.info(f"Writing parquet to {path}")

    dataframe.to_parquet(
        path,
        index=False,
    )


# ==========================================================
# Read CSV
# ==========================================================


def read_csv_from_s3(
    s3_key: str,
) -> pd.DataFrame:
    """
    Read a CSV dataset from Amazon S3.
    """

    path = _build_s3_path(s3_key)

    logger.info(f"Reading CSV from {path}")

    return pd.read_csv(path)


# ==========================================================
# Write CSV
# ==========================================================


def write_csv_to_s3(
    dataframe: pd.DataFrame,
    s3_key: str,
) -> None:
    """
    Write a dataframe as CSV to Amazon S3.
    """

    path = _build_s3_path(s3_key)

    logger.info(f"Writing CSV to {path}")

    dataframe.to_csv(
        path,
        index=False,
    )
