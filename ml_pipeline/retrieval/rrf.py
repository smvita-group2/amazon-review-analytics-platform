"""
Reciprocal Rank Fusion (RRF)

Combines semantic and BM25 search results using
Reciprocal Rank Fusion (RRF).
"""

from operator import itemgetter

from common.constants import (
    PARENT_ASIN_KEY,
    RRF_SCORE,
)
from common.logger import get_logger

logger = get_logger(__name__)


class ReciprocalRankFusion:
    """
    Performs Reciprocal Rank Fusion (RRF).

    Reference
    ---------
    Cormack, Clarke & Büttcher (2009)

    RRF Score:

        score += 1 / (k + rank)

    where:
        k = 60 (industry standard)
    """

    RRF_K = 60

    @staticmethod
    def fuse(
        semantic_results: list[dict],
        bm25_results: list[dict],
    ) -> list[dict]:
        """
        Fuse semantic and BM25 search results.

        Parameters
        ----------
        semantic_results : list[dict]
            Results from semantic search.

        bm25_results : list[dict]
            Results from BM25 search.

        Returns
        -------
        list[dict]
            All fused retrieval results sorted by
            RRF score.
        """

        if not semantic_results and not bm25_results:

            logger.warning("No retrieval results available.")

            return []

        fused_results: dict[
            str,
            dict,
        ] = {}

        ReciprocalRankFusion._add_results(
            fused_results=fused_results,
            results=semantic_results,
        )

        ReciprocalRankFusion._add_results(
            fused_results=fused_results,
            results=bm25_results,
        )

        ranked_results = sorted(
            fused_results.values(),
            key=itemgetter(
                RRF_SCORE,
            ),
            reverse=True,
        )

        for result in ranked_results:

            result.pop(
                RRF_SCORE,
                None,
            )

        logger.info(
            "Generated %d fused retrieval results.",
            len(ranked_results),
        )

        return ranked_results

    @staticmethod
    def _add_results(
        fused_results: dict[
            str,
            dict,
        ],
        results: list[dict],
    ) -> None:
        """
        Add one ranked retrieval list into the
        fused ranking.
        """

        for rank, result in enumerate(
            results,
            start=1,
        ):

            parent_asin = result.get(
                PARENT_ASIN_KEY,
            )

            if not parent_asin:

                continue

            rrf_score = 1.0 / (ReciprocalRankFusion.RRF_K + rank)

            if parent_asin not in fused_results:

                fused_results[parent_asin] = result.copy()

                fused_results[parent_asin][RRF_SCORE] = rrf_score

            else:

                fused_results[parent_asin][RRF_SCORE] += rrf_score
