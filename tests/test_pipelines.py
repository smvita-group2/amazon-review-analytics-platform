"""
Unit tests for data processing pipelines.
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
from src.silver_to_gold.gold_visualization_transformer import (
    GoldVisualizationTransformer,
)
from src.silver_to_gold.silver_master_transformer import SilverMasterTransformer
from src.validation.metadata_validator import MetadataValidator
from src.validation.reviews_validator import ReviewsValidator


def test_bronze_to_silver_reviews_pipeline_flow(spark):
    """
    Test end-to-end transformation and validation flow for Bronze to Silver Reviews.
    """
    schema = StructType(
        [
            StructField("parent_asin", StringType(), True),
            StructField("user_id", StringType(), True),
            StructField("rating", DoubleType(), True),
            StructField("title", StringType(), True),
            StructField("text", StringType(), True),
            StructField("helpful_vote", IntegerType(), True),
            StructField("verified_purchase", StringType(), True),
            StructField("timestamp", LongType(), True),
        ]
    )

    data = [
        (
            "B0001",
            "U101",
            5.0,
            "  Awesome Speaker  ",
            " Loud and clear ",
            3,
            "True",
            1670000000000,
        )
    ]

    df = spark.createDataFrame(data, schema)
    transformed_df = ReviewsTransformer(df).transform()

    # Verify validation passes on transformed df
    ReviewsValidator(transformed_df).run()
    assert transformed_df.count() == 1


def test_bronze_to_silver_metadata_pipeline_flow(spark):
    """
    Test end-to-end transformation and validation flow for Bronze to Silver Metadata.
    """
    image_struct = StructType(
        [
            StructField("hi_res", StringType(), True),
            StructField("large", StringType(), True),
        ]
    )

    schema = StructType(
        [
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
        ]
    )

    data = [
        (
            "B0001",
            "  Smart Watch  ",
            " TechStore ",
            ["Electronics", "Wearables"],
            "$149.99",
            4.6,
            300,
            ["AMOLED Display"],
            ["Heart Rate Monitor"],
            [{"hi_res": "http://hi.url", "large": "http://lg.url"}],
            "Electronics",
        )
    ]

    df = spark.createDataFrame(data, schema)
    transformed_df = MetadataTransformer(df).transform()

    # Verify validation passes on transformed df
    MetadataValidator(transformed_df).run()
    assert transformed_df.count() == 1


def test_silver_master_and_gold_pipeline_flow(spark):
    """
    Test Silver Master join and Gold Visualization dataset creation pipeline.
    """
    reviews_schema = StructType(
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
    reviews_data = [
        (
            "B001",
            "U100",
            5.0,
            "Great",
            "Love it",
            1,
            "True",
            "2023-01-01 00:00:00",
            "2023-01-01",
            2023,
            1,
        )
    ]
    reviews_df = spark.createDataFrame(reviews_data, reviews_schema)

    metadata_schema = StructType(
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
    metadata_data = [
        (
            "B001",
            "Camera",
            "Canon",
            "Electronics",
            "Cameras",
            499.99,
            4.8,
            1000,
            "4K DSLR",
            "WiFi enabled",
            "http://img.url",
        )
    ]
    metadata_df = spark.createDataFrame(metadata_data, metadata_schema)

    # Join in Silver Master
    silver_master_df = SilverMasterTransformer(
        reviews_df=reviews_df,
        metadata_df=metadata_df,
    ).transform()
    assert silver_master_df.count() == 1

    # Transform to Gold
    gold_df = GoldVisualizationTransformer(silver_master_df).transform()
    assert gold_df.count() == 1
