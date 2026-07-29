import boto3

from airflow.exceptions import AirflowException

from config.datasets.paths import (
    get_bronze_metadata_path,
    get_bronze_reviews_path,
)


def _check_prefix_exists(s3_uri: str) -> bool:
    """
    Returns True if the S3 prefix contains at least one object.
    """

    s3 = boto3.client("s3")

    bucket, prefix = s3_uri.replace("s3://", "").split("/", 1)

    print(f"Checking S3 path: {s3_uri}")

    response = s3.list_objects_v2(
        Bucket=bucket,
        Prefix=prefix,
        MaxKeys=1,
    )

    return "Contents" in response


def check_bronze_data(dataset_name):
    """
    Verify Bronze Metadata and Bronze Reviews exist.
    """

    print(f"Checking dataset: {dataset_name}")

    metadata_path = get_bronze_metadata_path(dataset_name)
    reviews_path = get_bronze_reviews_path(dataset_name)

    if not _check_prefix_exists(metadata_path):
        raise AirflowException(f"Bronze metadata not found: {metadata_path}")

    if not _check_prefix_exists(reviews_path):
        raise AirflowException(f"Bronze reviews not found: {reviews_path}")

    print("Bronze dataset verified successfully.")
