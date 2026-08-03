"""
Unit tests for Bronze to Silver PySpark transformers.
"""

from pyspark.sql.types import (
    ArrayType,
    DoubleType,
    IntegerType,
    LongType,
    StringType,
    StructField,
    StructType,
)

from src.bronze_to_silver.metadata_transformer import MetadataTransformer
from src.bronze_to_silver.reviews_transformer import ReviewsTransformer


def test_reviews_transformer(spark):
    """
    Test ReviewsTransformer schema transformation, column renaming,
    and helpful vote cleaning.
    """
    schema = StructType([
        StructField("parent_asin", StringType(), True),
        StructField("user_id", StringType(), True),
        StructField("rating", DoubleType(), True),
        StructField("title", StringType(), True),
        StructField("text", StringType(), True),
        StructField("helpful_vote", IntegerType(), True),
        StructField("verified_purchase", StringType(), True),
        StructField("timestamp", LongType(), True),
    ])

    data = [
        (
            "B0001",
            "U101",
            4.5,
            "  Great Product  ",
            " Works well ",
            -1,
            "True",
            1600000000000,
        ),
        (
            "B0002",
            "U102",
            5.0,
            "Awesome",
            "Super fast",
            5,
            "True",
            1650000000000,
        ),
    ]

    df = spark.createDataFrame(data, schema)
    transformer = ReviewsTransformer(df)
    transformed_df = transformer.transform()

    result = transformed_df.collect()
    assert len(result) == 2

    # Check column names
    expected_cols = [
        "parent_asin",
        "user_id",
        "review_rating",
        "review_title",
        "review_text",
        "helpful_vote",
        "verified_purchase",
        "review_timestamp",
        "review_date",
        "review_year",
        "review_month",
    ]
    assert transformed_df.columns == expected_cols

    # Check whitespace trimming
    assert result[0]["review_title"] == "Great Product"
    assert result[0]["review_text"] == "Works well"

    # Check negative helpful vote sanitized to 0
    assert result[0]["helpful_vote"] == 0
    assert result[1]["helpful_vote"] == 5


def test_metadata_transformer(spark):
    """
    Test MetadataTransformer category parsing, store trimming,
    and price extraction.
    """
    image_struct = StructType([
        StructField("hi_res", StringType(), True),
        StructField("large", StringType(), True),
    ])

    schema = StructType([
        StructField("parent_asin", StringType(), True),
        StructField("title", StringType(), True),
        StructField("store", StringType(), True),
        StructField("categories", ArrayType(StringType()), True),
        StructField("price", StringType(), True),
        StructField("average_rating", DoubleType(), True),
        StructField("rating_number", IntegerType(), True),
        StructField("description", ArrayType(StringType()), True),
        StructField("features", ArrayType(StringType()), True),
        StructField("images", ArrayType(image_struct), True),
        StructField("main_category", StringType(), True),
    ])

    data = [
        (
            "B0001",
            "  Smart Watch  ",
            " TechStore ",
            ["Electronics", "Wearables", "Smartwatches"],
            "$99.99",
            4.2,
            120,
            ["High resolution display", "Long battery life"],
            ["Bluetooth 5.0", "Waterproof"],
            [{"hi_res": "http://img.hi", "large": "http://img.lg"}],
            "Electronics",
        )
    ]

    df = spark.createDataFrame(data, schema)
    transformer = MetadataTransformer(df)
    transformed_df = transformer.transform()

    result = transformed_df.collect()
    assert len(result) == 1
    row = result[0]

    assert row["product_title"] == "Smart Watch"
    assert row["store"] == "TechStore"
    assert row["main_category"] == "Electronics"
    assert row["sub_category"] == "Wearables | Smartwatches"
    assert row["product_image_url"] == "http://img.hi"
    assert row["description_text"] == "High resolution display Long battery life"
