"""
BM25 Search

Performs lexical retrieval using a persisted BM25 index.
"""

import pickle
import re
from pathlib import Path
from time import perf_counter

import numpy as np

from ml_pipeline.common.config import get_setting
from ml_pipeline.common.constants import (
    DOCUMENT,
    METADATA,
    PARENT_ASIN_KEY,
    SIMILARITY_SCORE,
)
from ml_pipeline.common.logger import get_logger

logger = get_logger(__name__)


class BM25Search:
    """
    Performs BM25 keyword retrieval.
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
                "paths",
                "bm25",
            )
        )

        self.input_file = (
            self.input_directory / f"{category}.pkl"
        )

        self._load_index()

    # ======================================================
    # Load Index
    # ======================================================

    def _load_index(
        self,
    ) -> None:

        if not self.input_file.exists():

            raise FileNotFoundError(
                f"BM25 index not found: {self.input_file}"
            )

        logger.info(
            "Loading BM25 index for '%s'.",
            self.category,
        )

        with open(
            self.input_file,
            "rb",
        ) as file:

            bundle = pickle.load(file)

        self.bm25 = bundle["bm25"]
        self.documents = bundle["documents"]
        self.metadata = bundle["metadata"]

        logger.info(
            "Loaded BM25 index containing %d documents.",
            len(self.documents),
        )

    # ======================================================
    # Query Preprocessing
    # ======================================================

    def _preprocess_query(
        self,
        query: str,
    ) -> list[str]:

        query = query.strip()

        if self.lowercase:

            query = query.lower()

        # collapse multiple spaces
        query = " ".join(query.split())

        # tokenize
        return re.findall(
            r"\b[a-zA-Z0-9]+\b",
            query,
        )

    # ======================================================
    # Search
    # ======================================================

    def search(
        self,
        query: str,
        top_k: int | None = None,
    ) -> list[dict]:

        if not query or not query.strip():

            logger.warning(
                "Received empty BM25 query."
            )

            return []

        top_k = top_k or self.top_k

        logger.info(
            "Running BM25 Search | Category=%s | TopK=%d",
            self.category,
            top_k,
        )

        start_time = perf_counter()

        tokenized_query = self._preprocess_query(
            query,
        )

        if not tokenized_query:

            return []

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

        top_indices = top_indices[
            np.argsort(
                scores[top_indices]
            )[::-1]
        ]

        results = []

        for index in top_indices:

            score = float(
                scores[index]
            )

            # Skip useless matches
            if score <= 0:

                continue

            results.append(
                {
                    PARENT_ASIN_KEY: self.metadata[index].get(
                        PARENT_ASIN_KEY,
                    ),
                    DOCUMENT: self.documents[index],
                    METADATA: self.metadata[index],
                    SIMILARITY_SCORE: score,
                }
            )

        elapsed = (
            perf_counter() - start_time
        ) * 1000

        logger.info(
            "BM25 Search completed in %.2f ms | Returned %d documents.",
            elapsed,
            len(results),
        )

        return results