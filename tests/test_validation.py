"""
Unit tests for PySpark data validators.
"""

import pytest
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

from src.validation.metadata_validator import MetadataValidator
from src.validation.reviews_validator import ReviewsValidator


def test_reviews_validator_pass(spark):
    """
    Test ReviewsValidator with valid Silver reviews dataset.
    """
    schema = StructType(
        [
            StructField("parent_asin", StringType(), True),
            StructField("user_id", StringType(), True),
            StructField("review_rating", DoubleType(), True),
            StructField("review_title", StringType(), True),
            StructField("review_text", StringType(), True),
            StructField("helpful_vote", IntegerType(), True),
            StructField("verified_purchase", StringType(), True),
            StructField("review_timestamp", StringType(), True),
            StructField("review_date", StringType(), True),
            StructField("review_year", IntegerType(), True),
            StructField("review_month", IntegerType(), True),
        ]
    )

    data = [
        (
            "B001",
            "U001",
            4.0,
            "Good",
            "Nice item",
            2,
            "True",
            "2023-01-01 00:00:00",
            "2023-01-01",
            2023,
            1,
        )
    ]
    df = spark.createDataFrame(data, schema)
    validator = ReviewsValidator(df)
    # Should not raise exception
    validator.run()


def test_reviews_validator_invalid_rating(spark):
    """
    Test ReviewsValidator raises error on invalid rating (>5).
    """
    schema = StructType(
        [
            StructField("parent_asin", StringType(), True),
            StructField("user_id", StringType(), True),
            StructField("review_rating", DoubleType(), True),
            StructField("review_title", StringType(), True),
            StructField("review_text", StringType(), True),
            StructField("helpful_vote", IntegerType(), True),
            StructField("verified_purchase", StringType(), True),
            StructField("review_timestamp", StringType(), True),
            StructField("review_date", StringType(), True),
            StructField("review_year", IntegerType(), True),
            StructField("review_month", IntegerType(), True),
        ]
    )

    data = [
        (
            "B001",
            "U001",
            6.0,
            "Overrated",
            "Rating 6 is invalid",
            0,
            "True",
            "2023-01-01 00:00:00",
            "2023-01-01",
            2023,
            1,
        )
    ]
    df = spark.createDataFrame(data, schema)
    validator = ReviewsValidator(df)
    with pytest.raises(ValueError, match="invalid ratings"):
        validator.run()


def test_metadata_validator_pass(spark):
    """
    Test MetadataValidator with valid Silver metadata dataset.
    """
    schema = StructType(
        [
            StructField("parent_asin", StringType(), True),
            StructField("product_title", StringType(), True),
            StructField("store", StringType(), True),
            StructField("main_category", StringType(), True),
            StructField("sub_category", StringType(), True),
            StructField("product_price", DoubleType(), True),
            StructField("product_average_rating", DoubleType(), True),
            StructField("product_rating_count", IntegerType(), True),
            StructField("description_text", StringType(), True),
            StructField("features_text", StringType(), True),
            StructField("product_image_url", StringType(), True),
        ]
    )

    data = [
        (
            "B001",
            "Headphones",
            "Sony",
            "Electronics",
            "Audio",
            99.99,
            4.5,
            250,
            "Wireless noise cancelling",
            "Bluetooth 5.2",
            "http://image.url",
        )
    ]
    df = spark.createDataFrame(data, schema)
    validator = MetadataValidator(df)
    validator.run()
