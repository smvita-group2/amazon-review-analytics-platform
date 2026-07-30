"""
Amazon S3 Utilities

Provides helper functions for interacting with
Amazon S3.
"""

from pathlib import Path

import boto3

from common.config import get_setting
from common.logger import get_logger

logger = get_logger(__name__)

# ==========================================================
# AWS Configuration
# ==========================================================

_REGION = get_setting(
    "aws",
    "region",
)

_BUCKET = get_setting(
    "aws",
    "bucket_name",
)

s3_client = boto3.client(
    "s3",
    region_name=_REGION,
)

# ==========================================================
# Upload File
# ==========================================================


def upload_file(
    local_file: str | Path,
    s3_key: str,
) -> None:
    """
    Upload a local file to Amazon S3.
    """

    local_file = Path(local_file)

    logger.info(
        f"Uploading {local_file} -> s3://{_BUCKET}/{s3_key}"
    )

    s3_client.upload_file(
        str(local_file),
        _BUCKET,
        s3_key,
    )


# ==========================================================
# Download File
# ==========================================================


def download_file(
    s3_key: str,
    local_file: str | Path,
) -> None:
    """
    Download a file from Amazon S3.
    """

    local_file = Path(local_file)

    local_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger.info(
        f"Downloading s3://{_BUCKET}/{s3_key}"
    )

    s3_client.download_file(
        _BUCKET,
        s3_key,
        str(local_file),
    )


# ==========================================================
# Check Object Exists
# ==========================================================


def object_exists(
    s3_key: str,
) -> bool:
    """
    Check whether an object exists in Amazon S3.
    """

    try:

        s3_client.head_object(
            Bucket=_BUCKET,
            Key=s3_key,
        )

        return True

    except Exception:

        return False


# ==========================================================
# List Objects
# ==========================================================


def list_objects(
    prefix: str,
) -> list[str]:
    """
    List all object keys under a prefix.
    """

    response = s3_client.list_objects_v2(
        Bucket=_BUCKET,
        Prefix=prefix,
    )

    contents = response.get(
        "Contents",
        [],
    )

    return [
        obj["Key"]
        for obj in contents
    ]