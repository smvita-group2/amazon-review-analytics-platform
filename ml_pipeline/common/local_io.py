"""
Local DataFrame I/O Utilities

Provides helper functions for reading and writing
Pandas DataFrames directly from the local filesystem.
"""

from pathlib import Path

import pandas as pd

from common.config import get_setting
from common.logger import get_logger

logger = get_logger(__name__)

# ==========================================================
# Helpers
# ==========================================================


def _build_local_path(
    base_path: str,
    category: str,
) -> Path:
    """
    Build a local directory path.
    """

    return Path(base_path) / category


# ==========================================================
# Read Parquet
# ==========================================================


def read_parquet_local(
    base_path: str,
    category: str,
) -> pd.DataFrame:
    """
    Read a parquet dataset from the local filesystem.
    """

    directory = _build_local_path(
        base_path,
        category,
    )

    logger.info("Reading parquet from %s", directory)

    dataframe = pd.read_parquet(directory)

    return dataframe


# ==========================================================
# Write Parquet
# ==========================================================


def write_parquet_local(
    dataframe: pd.DataFrame,
    base_path: str,
    category: str,
    filename: str,
) -> None:
    """
    Write a dataframe as parquet to the local filesystem.
    """

    directory = _build_local_path(
        base_path,
        category,
    )

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = directory / filename

    logger.info(
        "Writing parquet to %s",
        output_file,
    )

    dataframe.to_parquet(
        output_file,
        index=False,
    )


# ==========================================================
# Read CSV
# ==========================================================


def read_csv_local(
    base_path: str,
    category: str,
) -> pd.DataFrame:
    """
    Read a CSV dataset from the local filesystem.
    """

    directory = _build_local_path(
        base_path,
        category,
    )

    logger.info(
        "Reading CSV from %s",
        directory,
    )

    return pd.read_csv(directory)


# ==========================================================
# Write CSV
# ==========================================================


def write_csv_local(
    dataframe: pd.DataFrame,
    base_path: str,
    category: str,
    filename: str,
) -> None:
    """
    Write a dataframe as CSV to the local filesystem.
    """

    directory = _build_local_path(
        base_path,
        category,
    )

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = directory / filename

    logger.info(
        "Writing CSV to %s",
        output_file,
    )

    dataframe.to_csv(
        output_file,
        index=False,
    )
