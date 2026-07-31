"""
Persistence

Persists product documents into ChromaDB.
"""

import pandas as pd
from vectordb.chromadb_manager import ChromaDBManager
from vectordb.metadata_builder import MetadataBuilder

from ml_pipeline.common.constants import (
    CHROMA_REQUIRED_COLUMNS,
    EMBEDDING,
    PARENT_ASIN,
    PRODUCT_DOCUMENT,
)
from ml_pipeline.common.logger import get_logger

logger = get_logger(__name__)


class Persistence:
    """
    Persists product documents into ChromaDB.
    """

    def __init__(
        self,
        category: str,
    ) -> None:

        self.category = category

        self.chroma = ChromaDBManager(
            category=category,
        )

    def persist(
        self,
        dataframe: pd.DataFrame,
        reset_collection: bool = False,
    ) -> None:
        """
        Persist product documents into the category
        specific ChromaDB collection.
        """

        if dataframe.empty:

            logger.warning("Input dataframe is empty.")

            return

        missing_columns = [
            column
            for column in CHROMA_REQUIRED_COLUMNS
            if column not in dataframe.columns
        ]

        if missing_columns:

            raise ValueError(
                "Missing required columns: " f"{', '.join(missing_columns)}"
            )

        if reset_collection and self.chroma.exists():

            logger.info(
                "Resetting collection for '%s'.",
                self.category,
            )

            self.chroma.reset()

        ids = dataframe[PARENT_ASIN].astype(str).tolist()

        documents = dataframe[PRODUCT_DOCUMENT].fillna("").astype(str).tolist()

        embeddings = dataframe[EMBEDDING].tolist()

        metadata = MetadataBuilder.build_metadata(dataframe)

        logger.info(
            "Persisting %d products into '%s'.",
            len(ids),
            self.category,
        )

        self.chroma.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadata,
        )

        logger.info("Persistence completed successfully.")
