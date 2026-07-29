"""
Transformation logic for converting Bronze metadata into the Silver layer.
"""

from typing import cast

from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    array_join,
    coalesce,
    col,
    regexp_replace,
    size,
    slice,
    trim,
    when,
)
from pyspark.sql.types import DecimalType

from config.datasets.constants import CATEGORY_SEPARATOR, PRICE_PRECISION, PRICE_SCALE


class MetadataTransformer:
    """
    Applies all transformations required to convert Bronze metadata
    into the standardized Silver schema.
    """

    def __init__(self, df: DataFrame):
        self.df = df

    def rename_columns(self):
        """
        Renames Bronze metadata columns to the standardized Silver schema.
        """

        self.df = (
            self.df.withColumnRenamed("title", "product_title")
            .withColumnRenamed("average_rating", "product_average_rating")
            .withColumnRenamed("rating_number", "product_rating_count")
            .withColumnRenamed("description", "description_text")
            .withColumnRenamed("features", "features_text")
            .withColumnRenamed("price", "product_price")
        )

        return self

    def drop_unused_columns(self):
        """
        Removes metadata columns that are not required in the Silver layer.
        """

        self.df = self.df.drop(
            "author", "bought_together", "subtitle", "videos", "details"
        )

        return self

    def clean_price(self):
        """
        Cleans the product price and converts it to DecimalType.
        """

        self.df = self.df.withColumn(
            "product_price",
            regexp_replace(col("product_price"), r"[^0-9.]", "").cast(
                DecimalType(PRICE_PRECISION, PRICE_SCALE)
            ),
        )

        return self

    def extract_primary_image(self):
        """
        Extracts the primary product image URL.
        """

        self.df = self.df.withColumn(
            "product_image_url",
            coalesce(
                col("images").getItem(0).getField("hi_res"),
                col("images").getItem(0).getField("large"),
            ),
        ).drop("images")

        return self

    def flatten_description(self):
        """
        Flattens the description array into a single text field.
        Empty arrays are converted to NULL.
        """

        self.df = self.df.withColumn(
            "description_text",
            when(
                col("description_text").isNull() | (size(col("description_text")) == 0),
                None,
            ).otherwise(array_join(col("description_text"), " ")),
        )

        return self

    def flatten_features(self):
        """
        Flattens the features array into a single text field.
        Empty arrays are converted to NULL.
        """

        self.df = self.df.withColumn(
            "features_text",
            when(
                col("features_text").isNull() | (size(col("features_text")) == 0), None
            ).otherwise(array_join(col("features_text"), CATEGORY_SEPARATOR)),
        )

        return self

    def standardize_categories(self):
        """
        Creates standardized main and sub categories from the category hierarchy.
        """

        self.df = (
            self.df.drop("main_category")
            .withColumn("main_category", trim(col("categories").getItem(0)))
            .withColumn(
                "sub_category",
                when(
                    col("categories").isNull() | (size(col("categories")) <= 1), None
                ).otherwise(
                    array_join(
                        slice(col("categories"), 2, size(col("categories")) - 1),
                        CATEGORY_SEPARATOR,
                    )
                ),
            )
            .drop("categories")
        )

        return self

    def standardize_store(self):
        """
        Cleans the store name by trimming whitespace.
        Empty strings are converted to NULL.
        """

        self.df = self.df.withColumn(
            "store", when(trim(col("store")) == "", None).otherwise(trim(col("store")))
        )

        return self

    def clean_product_title(self):
        """
        Cleans the product title by trimming whitespace.
        Empty strings are converted to NULL.
        """

        self.df = self.df.withColumn(
            "product_title",
            when(trim(col("product_title")) == "", None).otherwise(
                trim(col("product_title"))
            ),
        )

        return self

    def reorder_columns(self):
        """
        Reorders columns according to the Silver metadata schema.
        """

        self.df = self.df.select(
            "parent_asin",
            "product_title",
            "store",
            "main_category",
            "sub_category",
            "product_price",
            "product_average_rating",
            "product_rating_count",
            "description_text",
            "features_text",
            "product_image_url",
        )

        return self

    def transform(self) -> DataFrame:
        """
        Executes all metadata transformations in order.
        """

        self.rename_columns()
        self.drop_unused_columns()
        self.clean_price()
        self.extract_primary_image()
        self.flatten_description()
        self.flatten_features()
        self.standardize_categories()
        self.standardize_store()
        self.clean_product_title()
        self.reorder_columns()

        return cast(DataFrame, self.df)
