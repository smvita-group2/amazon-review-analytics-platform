"""
Amazon S3 Utilities

Provides helper functions for interacting with
Amazon S3.
"""

from pathlib import Path

import boto3

from ml_pipeline.common.config import get_setting
from ml_pipeline.common.logger import get_logger

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
        "Uploading '%s' to s3://%s/%s",
        local_file,
        _BUCKET,
        s3_key,
    )

    s3_client.upload_file(
        str(local_file),
        _BUCKET,
        s3_key,
    )


# ==========================================================
# Upload Bytes
# ==========================================================


def upload_bytes(
    data: bytes,
    s3_key: str,
) -> None:
    """
    Upload bytes directly to Amazon S3.
    """

    logger.info(
        "Uploading object to s3://%s/%s",
        _BUCKET,
        s3_key,
    )

    s3_client.put_object(
        Bucket=_BUCKET,
        Key=s3_key,
        Body=data,
    )


# ==========================================================
# Upload Directory
# ==========================================================


def upload_directory(
    local_directory: str | Path,
    s3_prefix: str,
) -> None:
    """
    Upload an entire directory to Amazon S3.
    """

    local_directory = Path(local_directory)

    if not local_directory.exists():

        raise FileNotFoundError(f"Directory not found: {local_directory}")

    logger.info(
        "Uploading directory '%s' to s3://%s/%s",
        local_directory,
        _BUCKET,
        s3_prefix,
    )

    for file_path in local_directory.rglob("*"):

        if not file_path.is_file():

            continue

        relative_path = file_path.relative_to(
            local_directory,
        )

        s3_key = f"{s3_prefix}/{relative_path.as_posix()}"

        s3_client.upload_file(
            str(file_path),
            _BUCKET,
            s3_key,
        )

    logger.info("Directory upload completed.")


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
        "Downloading s3://%s/%s",
        _BUCKET,
        s3_key,
    )

    s3_client.download_file(
        _BUCKET,
        s3_key,
        str(local_file),
    )


# ==========================================================
# Download Directory
# ==========================================================


def download_directory(
    s3_prefix: str,
    local_directory: str | Path,
) -> None:
    """
    Download an entire directory from Amazon S3.
    """

    local_directory = Path(local_directory)

    local_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger.info(
        "Downloading directory s3://%s/%s",
        _BUCKET,
        s3_prefix,
    )

    response = s3_client.list_objects_v2(
        Bucket=_BUCKET,
        Prefix=s3_prefix,
    )

    for obj in response.get(
        "Contents",
        [],
    ):

        key = obj["Key"]

        relative_path = Path(key.removeprefix(f"{s3_prefix}/"))

        destination = local_directory / relative_path

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        s3_client.download_file(
            _BUCKET,
            key,
            str(destination),
        )

    logger.info("Directory download completed.")


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

    return [obj["Key"] for obj in contents]
