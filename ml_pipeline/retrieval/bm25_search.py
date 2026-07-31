"""
BM25 Search

Performs lexical retrieval using a persisted BM25 index.
"""

import pickle
from pathlib import Path

import numpy as np

from common.config import get_setting
from common.constants import (
    DOCUMENT,
    METADATA,
    PARENT_ASIN_KEY,
    SIMILARITY_SCORE,
)
from common.logger import get_logger

logger = get_logger(__name__)


class BM25Search:
    """
    Performs BM25 keyword search using a persisted index.
    """

    def __init__(
        self,
        category: str,
    ) -> None:

        self.category = category

        self.top_k = get_setting(
            "retrieval",
            "top_k_bm25",
        )

        self.lowercase = get_setting(
            "bm25",
            "lowercase",
        )

        self.input_directory = Path(
            get_setting(
                "bm25",
                "directory",
            )
        )

        self.input_file = self.input_directory / f"{category}.pkl"

        self._load_index()

    def _load_index(
        self,
    ) -> None:
        """
        Load the persisted BM25 bundle.
        """

        if not self.input_file.exists():

            raise FileNotFoundError(f"BM25 index not found: {self.input_file}")

        logger.info(
            "Loading BM25 index for '%s'.",
            self.category,
        )

        with open(
            self.input_file,
            "rb",
        ) as file:

            bundle = pickle.load(
                file,
            )

        self.bm25 = bundle["bm25"]
        self.documents = bundle["documents"]
        self.metadata = bundle["metadata"]

        logger.info(
            "Loaded BM25 index containing %d documents.",
            len(self.documents),
        )

    def search(
        self,
        query: str,
        top_k: int | None = None,
    ) -> list[dict]:
        """
        Perform BM25 keyword search.
        """

        query = query.strip()

        if not query:

            logger.warning("Received an empty query.")

            return []

        top_k = top_k or self.top_k

        if self.lowercase:

            query = query.lower()

        tokenized_query = query.split()

        scores = np.asarray(
            self.bm25.get_scores(
                tokenized_query,
            )
        )

        if scores.size == 0:

            return []

        top_k = min(
            top_k,
            scores.size,
        )

        top_indices = np.argpartition(
            scores,
            -top_k,
        )[-top_k:]

        top_indices = top_indices[np.argsort(scores[top_indices])[::-1]]

        documents = self.documents
        metadata = self.metadata

        results = []

        for index in top_indices:

            results.append(
                {
                    PARENT_ASIN_KEY: metadata[index].get(
                        PARENT_ASIN_KEY,
                    ),
                    DOCUMENT: documents[index],
                    METADATA: metadata[index],
                    SIMILARITY_SCORE: float(scores[index]),
                }
            )

        logger.info(
            "Retrieved %d BM25 results from '%s'.",
            len(results),
            self.category,
        )

        return results
