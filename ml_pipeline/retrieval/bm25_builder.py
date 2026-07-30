"""
BM25 Builder

Builds and persists a BM25 index for a product category.
"""

import pickle

import pandas as pd
from rank_bm25 import BM25Okapi

from common.config import get_setting
from common.constants import (
    CHROMA_METADATA_FIELDS,
    PRODUCT_DOCUMENT,
)
from common.logger import get_logger
from common.s3_utils import upload_bytes

logger = get_logger(__name__)


class BM25Builder:
    """
    Builds and persists a BM25 index for a category.
    """

    def __init__(
        self,
        category: str,
    ) -> None:

        self.category = category

        self.lowercase = get_setting(
            "bm25",
            "lowercase",
        )

        self.s3_key = (
            f"{get_setting('paths', 'bm25')}"
            f"/{category}.pkl"
        )

    def build(
        self,
        dataframe: pd.DataFrame,
    ) -> None:
        """
        Build and persist the BM25 index directly to Amazon S3.
        """

        if dataframe.empty:

            logger.warning(
                "Input dataframe is empty."
            )

            return

        if PRODUCT_DOCUMENT not in dataframe.columns:

            raise ValueError(
                f"Missing required column: {PRODUCT_DOCUMENT}"
            )

        logger.info(
            "Building BM25 index for '%s'.",
            self.category,
        )

        documents = (
            dataframe[PRODUCT_DOCUMENT]
            .fillna("")
            .astype(str)
            .tolist()
        )

        corpus = documents

        if self.lowercase:

            corpus = [
                document.lower()
                for document in corpus
            ]

        tokenized_corpus = [
            document.split()
            for document in corpus
        ]

        bm25 = BM25Okapi(
            tokenized_corpus
        )

        metadata = dataframe[
            list(CHROMA_METADATA_FIELDS)
        ].to_dict(
            orient="records"
        )

        bundle = {
            "bm25": bm25,
            "documents": documents,
            "metadata": metadata,
        }

        logger.info(
            "Uploading BM25 index to '%s'.",
            self.s3_key,
        )

        serialized = pickle.dumps(
            bundle,
            protocol=pickle.HIGHEST_PROTOCOL,
        )

        upload_bytes(
            data=serialized,
            s3_key=self.s3_key,
        )

        logger.info(
            "BM25 index uploaded successfully for '%s' (%d documents).",
            self.category,
            len(documents),
        )