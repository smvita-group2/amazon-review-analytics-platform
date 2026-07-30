"""
Semantic Search

Performs semantic retrieval using ChromaDB.
"""

from typing import Any

from common.config import get_setting
from common.constants import (
    DOCUMENT,
    METADATA,
    PARENT_ASIN_KEY,
    SIMILARITY_SCORE,
)
from common.logger import get_logger

from embeddings.embedding_model import EmbeddingModel
from vectordb.chromadb_manager import ChromaDBManager

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

        Parameters
        ----------
        query : str
            User query.

        top_k : int | None
            Number of documents to retrieve.

        where : dict | None
            Optional metadata filters.

        Returns
        -------
        list[dict]
            Semantic search results.
        """

        query = query.strip()

        if not query:

            logger.warning(
                "Received an empty query."
            )

            return []

        top_k = top_k or self.top_k

        logger.info(
            "Performing semantic search on '%s' (top_k=%d).",
            self.category,
            top_k,
        )

        query_embedding = EmbeddingModel.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=self.normalize_query_embeddings,
        ).tolist()

        response = self.chroma.query(
            query_embedding=query_embedding,
            n_results=top_k,
            where=where,
        )

        documents = response.get("documents") or [[]]
        metadatas = response.get("metadatas") or [[]]
        distances = response.get("distances") or [[]]

        documents = documents[0] if documents else []
        metadatas = metadatas[0] if metadatas else []
        distances = distances[0] if distances else []

        semantic_results = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):

            similarity_score = max(
                0.0,
                1.0 - float(distance),
            )

            semantic_results.append(
                {
                    PARENT_ASIN_KEY: metadata.get(
                        PARENT_ASIN_KEY,
                    ),
                    DOCUMENT: document,
                    METADATA: metadata,
                    SIMILARITY_SCORE: similarity_score,
                }
            )

        semantic_results.sort(
            key=lambda result: result[
                SIMILARITY_SCORE
            ],
            reverse=True,
        )

        logger.info(
            "Retrieved %d semantic results from '%s'.",
            len(semantic_results),
            self.category,
        )

        return semantic_results