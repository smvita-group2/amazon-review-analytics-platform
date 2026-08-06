"""
CrossEncoder Reranker

Re-ranks hybrid retrieval results using
a CrossEncoder model and computes a
Recommendation Score.
"""

import math

from ml_pipeline.common.config import get_setting
from ml_pipeline.common.constants import (
    DOCUMENT,
    METADATA,
    RERANK_SCORE,
    RECOMMENDATION_SCORE,
)
from ml_pipeline.common.logger import get_logger
from ml_pipeline.retrieval.cross_encoder_model import CrossEncoderModel

logger = get_logger(__name__)


class Reranker:
    """
    CrossEncoder-based reranker.
    """

    def __init__(
        self,
    ) -> None:

        self.top_k = get_setting(
            "retrieval",
            "final_top_k",
        )

        self.batch_size = get_setting(
            "reranker",
            "batch_size",
        )

        self.show_progress_bar = get_setting(
            "reranker",
            "show_progress_bar",
        )

        self.model = CrossEncoderModel.get_model()

    def rerank(
        self,
        query: str,
        results: list[dict],
        top_k: int | None = None,
    ) -> list[dict]:
        """
        Re-rank retrieved documents using the
        CrossEncoder and compute a recommendation
        score.
        """

        if not results:

            logger.warning(
                "No documents available for reranking."
            )

            return []

        if top_k is None:

            top_k = self.top_k

        sentence_pairs = [
            (
                query,
                result[DOCUMENT],
            )
            for result in results
        ]

        scores = self.model.predict(
            sentence_pairs,
            batch_size=self.batch_size,
            show_progress_bar=self.show_progress_bar,
        )

        reranked_results = []

        for result, score in zip(
            results,
            scores,
        ):

            item = result.copy()

            item[RERANK_SCORE] = float(score)

            reranked_results.append(item)

        # --------------------------------------------------
        # Normalize CrossEncoder Scores
        # --------------------------------------------------

        raw_scores = [
            item[RERANK_SCORE]
            for item in reranked_results
        ]

        min_score = min(raw_scores)
        max_score = max(raw_scores)

        max_reviews = max(
            (
                item[METADATA].get(
                    "product_review_count",
                    1,
                )
                for item in reranked_results
            ),
            default=1,
        )

        for item in reranked_results:

            # -----------------------------
            # Normalized Relevance
            # -----------------------------

            if max_score == min_score:

                relevance = 1.0

            else:

                relevance = (
                    item[RERANK_SCORE] - min_score
                ) / (
                    max_score - min_score
                )

            # -----------------------------
            # Rating
            # -----------------------------

            rating = float(
                item[METADATA].get(
                    "product_average_rating",
                    0,
                )
            )

            normalized_rating = rating / 5.0

            # -----------------------------
            # Review Confidence
            # -----------------------------

            review_count = float(
                item[METADATA].get(
                    "product_review_count",
                    0,
                )
            )

            normalized_reviews = (
                math.log1p(review_count)
                / math.log1p(max_reviews)
            )

            # -----------------------------
            # Final Recommendation Score
            # -----------------------------

            recommendation = (
                0.55 * relevance
                + 0.30 * normalized_rating
                + 0.15 * normalized_reviews
            )

            item[RERANK_SCORE] = round(
                relevance * 100,
                1,
            )

            item[RECOMMENDATION_SCORE] = round(
                recommendation * 100,
                1,
            )

        # --------------------------------------------------
        # Sort by Recommendation Score
        # --------------------------------------------------

        reranked_results.sort(
            key=lambda x: x[
                RECOMMENDATION_SCORE
            ],
            reverse=True,
        )

        final_results = reranked_results[
            :top_k
        ]

        logger.info(
            "Returned %d reranked documents.",
            len(final_results),
        )

        return final_results