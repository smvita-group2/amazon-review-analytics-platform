from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    array_join,
    coalesce,
    col,
    get,
    regexp_replace,
    size,
    slice,
    trim,
    when,
)


class MetadataTransformer:
    """
    Transforms Bronze metadata into Silver metadata.
    """

    def __init__(self):
        pass

    def rename_columns(self, df: DataFrame) -> DataFrame:
        """
        Rename Bronze columns to Silver naming convention.
        """

        return (
            df
            .withColumnRenamed("title", "product_title")
            .withColumnRenamed("average_rating", "product_average_rating")
            .withColumnRenamed("rating_number", "product_rating_count")
            .withColumnRenamed("price", "product_price")
            .withColumnRenamed("description", "description_text")
            .withColumnRenamed("features", "features_text")
        )

    def drop_unused_columns(self, df: DataFrame) -> DataFrame:
        """
        Remove columns that are not required in the Silver layer.
        """

        return df.drop(
            "videos",
            "details",
            "bought_together",
        )

    def extract_primary_image(self, df: DataFrame) -> DataFrame:
        """
        Extract the primary product image URL.
        """

        return (
            df
            .withColumn(
                "product_image_url",
                coalesce(
                    get(col("images"), 0)["hi_res"],
                    get(col("images"), 0)["large"],
                ),
            )
            .drop("images")
        )

    def flatten_description(self, df: DataFrame) -> DataFrame:
        """
        Convert description array into a single string.
        """

        return df.withColumn(
            "description_text",
            when(
                col("description_text").isNull()
                | (size(col("description_text")) == 0),
                None,
            ).otherwise(
                array_join(col("description_text"), " ")
            ),
        )

    def flatten_features(self, df: DataFrame) -> DataFrame:
        """
        Convert features array into a single string.
        """

        return df.withColumn(
            "features_text",
            when(
                col("features_text").isNull()
                | (size(col("features_text")) == 0),
                None,
            ).otherwise(
                array_join(col("features_text"), " | ")
            ),
        )

    def standardize_categories(self, df: DataFrame) -> DataFrame:
        """
        Split categories into main_category and sub_category.
        """

        return (
            df
            .withColumn(
                "main_category",
                when(
                    size(col("categories")) > 0,
                    col("categories")[0],
                ),
            )
            .withColumn(
                "sub_category",
                when(
                    size(col("categories")) > 1,
                    array_join(
                        slice(col("categories"), 2, 100),
                        " > ",
                    ),
                ),
            )
            .drop("categories")
        )

    def clean_store(self, df: DataFrame) -> DataFrame:
        """
        Clean store names by removing extra spaces.
        """

        return df.withColumn(
            "store",
            when(
                trim(col("store")) == "",
                None,
            ).otherwise(
                trim(col("store"))
            ),
        )

    def clean_product_title(self, df: DataFrame) -> DataFrame:
        """
        Clean product titles by removing extra spaces.
        """

        return df.withColumn(
            "product_title",
            when(
                trim(col("product_title")) == "",
                None,
            ).otherwise(
                regexp_replace(
                    trim(col("product_title")),
                    "\\s+",
                    " ",
                )
            ),
        )

    def reorder_columns(self, df: DataFrame) -> DataFrame:
        """
        Arrange columns in the Silver layer schema.
        """

        return df.select(
            "parent_asin",
            "product_title",
            "store",
            "main_category",
            "sub_category",
            "product_average_rating",
            "product_rating_count",
            "product_price",
            "description_text",
            "features_text",
            "product_image_url",
        )

    def transform(self, df: DataFrame) -> DataFrame:
        """
        Apply all metadata transformations.
        """

        df = self.rename_columns(df)
        df = self.drop_unused_columns(df)
        df = self.extract_primary_image(df)
        df = self.flatten_description(df)
        df = self.flatten_features(df)
        df = self.standardize_categories(df)
        df = self.clean_store(df)
        df = self.clean_product_title(df)
        df = self.reorder_columns(df)

        return df