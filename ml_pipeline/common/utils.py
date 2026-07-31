"""
Common Utility Functions

Contains reusable helper functions shared across
the ML pipeline.
"""

from pathlib import Path
from typing import Iterable

from ml_pipeline.common.logger import get_logger

logger = get_logger(__name__)


# ==========================================================
# Ensure Directory Exists
# ==========================================================


def ensure_directory(path: str | Path) -> Path:
    """
    Create a directory if it does not already exist.
    """

    directory = Path(path)

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return directory


# ==========================================================
# Chunk Iterable
# ==========================================================


def chunk_iterable(
    iterable: Iterable,
    chunk_size: int,
):
    """
    Yield successive chunks from an iterable.
    """

    iterable = list(iterable)

    for index in range(
        0,
        len(iterable),
        chunk_size,
    ):

        yield iterable[index : index + chunk_size]


# ==========================================================
# Safe String
# ==========================================================


def safe_string(value) -> str:
    """
    Convert a value to a clean string.
    """

    if value is None:

        return ""

    return str(value).strip()


# ==========================================================
# Format Rating
# ==========================================================


def format_rating(value) -> str:
    """
    Format product rating.
    """

    if value is None:

        return "N/A"

    return f"{float(value):.1f}"


# ==========================================================
# Format Integer
# ==========================================================


def format_number(value) -> str:
    """
    Format integer with thousands separator.
    """

    if value is None:

        return "0"

    return f"{int(value):,}"
