"""
Transformation logic for creating the Silver Master dataset.
"""

from pyspark.sql import DataFrame


class SilverMasterTransformer:
    """
    Creates the Silver Master dataset by joining
    the Silver Reviews and Silver Metadata datasets.
    """

    def __init__(
        self,
        reviews_df: DataFrame,
        metadata_df: DataFrame,
    ):
        self.reviews_df = reviews_df
        self.metadata_df = metadata_df

    def transform(self) -> DataFrame:
        """
        Joins the Silver Reviews and Silver Metadata
        datasets into a single Silver Master dataset.
        """

        master_df = (
            self.reviews_df.join(
                self.metadata_df,
                on="parent_asin",
                how="inner",
            )
        )

        return master_df