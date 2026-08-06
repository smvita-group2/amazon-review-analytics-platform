"""
Semantic Search

Performs semantic retrieval using ChromaDB.
"""

from time import perf_counter
from typing import Any

from ml_pipeline.common.config import get_setting
from ml_pipeline.common.constants import (
    DOCUMENT,
    METADATA,
    PARENT_ASIN_KEY,
    SIMILARITY_SCORE,
)
from ml_pipeline.common.logger import get_logger
from ml_pipeline.embeddings.embedding_model import EmbeddingModel
from ml_pipeline.vectordb.chromadb_manager import ChromaDBManager

logger = get_logger(__name__)


class SemanticSearch:
    """
    Performs semantic search using vector similarity.
    """

    def __init__(
        self,
        category: str,
    ) -> None:

        self.category = category

        self.top_k = get_setting(
            "retrieval",
            "top_k_semantic",
        )

        self.normalize_query_embeddings = get_setting(
            "retrieval",
            "normalize_query_embeddings",
        )

        self.min_similarity = get_setting(
            "retrieval",
            "min_similarity",
        )

        self.chroma = ChromaDBManager(
            category=category,
        )

    def search(
        self,
        query: str,
        top_k: int | None = None,
        where: dict[str, Any] | None = None,
    ) -> list[dict]:
        """
        Perform semantic search.
        """

        query = query.strip()

        if not query:

            logger.warning("Received empty semantic query.")

            return []

        top_k = top_k or self.top_k

        logger.info(
            "Running Semantic Search | Category=%s | TopK=%d",
            self.category,
            top_k,
        )

        start_time = perf_counter()

        # --------------------------------------------------
        # Encode Query
        # --------------------------------------------------

        query_embedding = EmbeddingModel.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=self.normalize_query_embeddings,
        )[0].tolist()

        # --------------------------------------------------
        # Chroma Search
        # --------------------------------------------------

        response = self.chroma.query(
            query_embedding=query_embedding,
            n_results=top_k,
            where=where,
        )

        documents = response.get(
            "documents",
            [[]],
        )[0]

        metadatas = response.get(
            "metadatas",
            [[]],
        )[0]

        distances = response.get(
            "distances",
            [[]],
        )[0]

        semantic_results = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):

            distance = float(distance)

            similarity = max(
                0.0,
                1.0 - distance,
            )

            # Skip weak matches
            if similarity < self.min_similarity:

                continue

            semantic_results.append(
                {
                    PARENT_ASIN_KEY: metadata.get(
                        PARENT_ASIN_KEY,
                    ),
                    DOCUMENT: document,
                    METADATA: metadata,
                    SIMILARITY_SCORE: round(
                        similarity,
                        4,
                    ),
                    "distance": round(
                        distance,
                        4,
                    ),
                }
            )

        semantic_results.sort(
            key=lambda result: result[SIMILARITY_SCORE],
            reverse=True,
        )

        elapsed = (perf_counter() - start_time) * 1000

        logger.info(
            "Semantic Search completed in %.2f ms | Returned %d documents.",
            elapsed,
            len(semantic_results),
        )

        return semantic_results
