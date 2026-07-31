"""
Metadata Builder

Builds metadata dictionaries for ChromaDB.
"""

import pandas as pd

from common.constants import CHROMA_METADATA_FIELDS
from common.logger import get_logger

logger = get_logger(__name__)


class MetadataBuilder:
    """
    Builds metadata dictionaries for ChromaDB documents.
    """

    @staticmethod
    def build_metadata(
        dataframe: pd.DataFrame,
    ) -> list[dict]:
        """
        Build metadata for all products.

        Parameters
        ----------
        dataframe : pd.DataFrame
            Product dataframe.

        Returns
        -------
        list[dict]
            Metadata dictionaries.
        """

        if dataframe.empty:

            logger.warning("Input dataframe is empty.")

            return []

        missing_columns = [
            column
            for column in CHROMA_METADATA_FIELDS
            if column not in dataframe.columns
        ]

        if missing_columns:

            raise ValueError(
                "Missing metadata columns: " f"{', '.join(missing_columns)}"
            )

        logger.info(
            "Building metadata for %d products.",
            len(dataframe),
        )

        metadata = (
            dataframe.loc[:, CHROMA_METADATA_FIELDS]
            .fillna("")
            .to_dict(orient="records")
        )

        logger.info(
            "Successfully built %d metadata records.",
            len(metadata),
        )

        return metadata
