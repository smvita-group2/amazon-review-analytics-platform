"""
Hybrid Search

Combines Semantic Search, BM25 Search,
Reciprocal Rank Fusion (RRF),
and CrossEncoder reranking.
"""

from concurrent.futures import ThreadPoolExecutor
from time import perf_counter

from ml_pipeline.common.config import get_setting
from ml_pipeline.common.logger import get_logger
from ml_pipeline.retrieval.bm25_search import BM25Search
from ml_pipeline.retrieval.reranker import Reranker
from ml_pipeline.retrieval.rrf import ReciprocalRankFusion
from ml_pipeline.retrieval.semantic_search import SemanticSearch

logger = get_logger(__name__)


class HybridSearch:
    """
    Hybrid Retrieval Pipeline

          User Query
               │
               ▼
     ┌──────────────────┐
     │ Semantic Search  │
     └──────────────────┘
               │
               │
     ┌──────────────────┐
     │   BM25 Search    │
     └──────────────────┘
               │
               ▼
    Reciprocal Rank Fusion
               │
               ▼
       CrossEncoder Reranker
               │
               ▼
         Final Top Documents
    """

    def __init__(
        self,
        category: str,
    ) -> None:

        self.category = category

        self.final_top_k = get_setting(
            "retrieval",
            "final_top_k",
        )

        self.rerank_top_k = get_setting(
            "retrieval",
            "rerank_top_k",
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
        Execute Hybrid Retrieval.
        """

        query = query.strip()

        if not query:

            logger.warning("Received empty search query.")

            return []

        final_top_k = final_top_k or self.final_top_k

        logger.info(
            "Running Hybrid Search | Category=%s",
            self.category,
        )

        start_time = perf_counter()

        try:

            # ------------------------------------------
            # Semantic + BM25 (Parallel)
            # ------------------------------------------

            with ThreadPoolExecutor(max_workers=2) as executor:

                semantic_future = executor.submit(
                    self.semantic_search.search,
                    query=query,
                )

                bm25_future = executor.submit(
                    self.bm25_search.search,
                    query=query,
                )

                semantic_results = semantic_future.result()
                bm25_results = bm25_future.result()

            logger.info(
                "Semantic Results : %d | BM25 Results : %d",
                len(semantic_results),
                len(bm25_results),
            )

            if not semantic_results and not bm25_results:

                logger.warning("No retrieval results found.")

                return []

            # ------------------------------------------
            # Reciprocal Rank Fusion
            # ------------------------------------------

            fused_results = ReciprocalRankFusion.fuse(
                semantic_results=semantic_results,
                bm25_results=bm25_results,
            )

            logger.info(
                "RRF produced %d unique documents.",
                len(fused_results),
            )

            if not fused_results:

                return []

            # ------------------------------------------
            # Limit candidates before reranking
            # ------------------------------------------

            candidates = fused_results[: self.rerank_top_k]

            logger.info(
                "Sending %d candidates to CrossEncoder.",
                len(candidates),
            )

            # ------------------------------------------
            # CrossEncoder Reranking
            # ------------------------------------------

            reranked_results = self.reranker.rerank(
                query=query,
                results=candidates,
                top_k=final_top_k,
            )

            elapsed = (perf_counter() - start_time) * 1000

            logger.info(
                ("Hybrid Search completed " "in %.2f ms | Returned %d documents."),
                elapsed,
                len(reranked_results),
            )

            return reranked_results

        except Exception:

            logger.exception("Hybrid Search failed.")

            return []
