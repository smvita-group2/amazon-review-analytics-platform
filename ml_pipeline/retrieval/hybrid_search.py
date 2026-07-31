"""
Hybrid Search

Combines semantic search, BM25 search,
Reciprocal Rank Fusion (RRF), and
CrossEncoder reranking.
"""

from retrieval.bm25_search import BM25Search
from retrieval.reranker import Reranker
from retrieval.rrf import ReciprocalRankFusion
from retrieval.semantic_search import SemanticSearch

from common.config import get_setting
from common.logger import get_logger

logger = get_logger(__name__)


class HybridSearch:
    """
    Hybrid retrieval pipeline.

    Workflow
    --------
    User Query
        ↓
    Semantic Search
        ↓
    BM25 Search
        ↓
    Reciprocal Rank Fusion
        ↓
    CrossEncoder Reranker
        ↓
    Final Documents
    """

    def __init__(
        self,
        category: str,
    ) -> None:
        """
        Initialize the hybrid retrieval pipeline.
        """

        self.category = category

        self.final_top_k = get_setting(
            "retrieval",
            "final_top_k",
        )

        self.semantic_search = SemanticSearch(
            category=category,
        )

        self.bm25_search = BM25Search(
            category=category,
        )

        self.reranker = Reranker()

    def search(
        self,
        query: str,
        final_top_k: int | None = None,
    ) -> list[dict]:
        """
        Perform hybrid retrieval.

        Parameters
        ----------
        query : str
            User search query.

        final_top_k : int | None
            Number of documents to return after
            reranking.

        Returns
        -------
        list[dict]
            Final reranked retrieval results.
        """

        if final_top_k is None:

            final_top_k = self.final_top_k

        logger.info(
            "Running hybrid search for category '%s'.",
            self.category,
        )

        semantic_results = self.semantic_search.search(
            query=query,
        )

        bm25_results = self.bm25_search.search(
            query=query,
        )

        logger.info(
            "Retrieved %d semantic and %d BM25 results.",
            len(semantic_results),
            len(bm25_results),
        )

        fused_results = ReciprocalRankFusion.fuse(
            semantic_results=semantic_results,
            bm25_results=bm25_results,
        )

        logger.info(
            "Fused %d unique retrieval results.",
            len(fused_results),
        )

        reranked_results = self.reranker.rerank(
            query=query,
            results=fused_results,
            top_k=final_top_k,
        )

        logger.info(
            "Returning %d reranked documents.",
            len(reranked_results),
        )

        return reranked_results
