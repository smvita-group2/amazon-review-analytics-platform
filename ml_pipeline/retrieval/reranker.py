"""
CrossEncoder Reranker

Re-ranks hybrid retrieval results using
a CrossEncoder model.
"""

from operator import itemgetter

from ml_pipeline.retrieval.cross_encoder_model import CrossEncoderModel

from ml_pipeline.common.config import get_setting
from ml_pipeline.common.constants import (
    DOCUMENT,
    RERANK_SCORE,
)
from ml_pipeline.common.logger import get_logger

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
        Re-rank retrieved documents using the CrossEncoder.
        """

        if not results:

            logger.warning("No documents available for reranking.")

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

        reranked_results.sort(
            key=itemgetter(
                RERANK_SCORE,
            ),
            reverse=True,
        )

        final_results = reranked_results[:top_k]

        # ======================================================
        # Normalize reranker scores to 0-100
        # ======================================================

        if final_results:

            raw_scores = [result[RERANK_SCORE] for result in final_results]

            min_score = min(raw_scores)
            max_score = max(raw_scores)

            for result in final_results:

                if max_score == min_score:

                    result[RERANK_SCORE] = 100.0

                else:

                    normalized = (
                        (result[RERANK_SCORE] - min_score) / (max_score - min_score)
                    ) * 100

                    result[RERANK_SCORE] = round(
                        normalized,
                        1,
                    )

        logger.info(
            "Returned %d reranked documents.",
            len(final_results),
        )

        return final_results
