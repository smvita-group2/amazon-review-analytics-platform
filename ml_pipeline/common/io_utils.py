"""
Input / Output Utilities

Provides reusable helper functions for reading
and writing datasets used throughout the ML pipeline.
"""

from pathlib import Path

import pandas as pd

from common.logger import get_logger

logger = get_logger(__name__)


# ==========================================================
# Read Parquet
# ==========================================================

def read_parquet(path: str | Path) -> pd.DataFrame:
    """
    Read a parquet dataset.
    """

    logger.info(f"Reading parquet: {path}")

    return pd.read_parquet(path)


# ==========================================================
# Write Parquet
# ==========================================================

def write_parquet(
    dataframe: pd.DataFrame,
    path: str | Path,
) -> None:
    """
    Write dataframe as parquet.
    """

    logger.info(f"Writing parquet: {path}")

    Path(path).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_parquet(
        path,
        index=False,
    )


# ==========================================================
# Read CSV
# ==========================================================

def read_csv(path: str | Path) -> pd.DataFrame:
    """
    Read a CSV file.
    """

    logger.info(f"Reading CSV: {path}")

    return pd.read_csv(path)


# ==========================================================
# Write CSV
# ==========================================================

def write_csv(
    dataframe: pd.DataFrame,
    path: str | Path,
) -> None:
    """
    Write dataframe as CSV.
    """

    logger.info(f"Writing CSV: {path}")

    Path(path).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_csv(
        path,
        index=False,
    )