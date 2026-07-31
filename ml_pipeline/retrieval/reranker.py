"""
CrossEncoder Reranker

Re-ranks hybrid retrieval results using
a CrossEncoder model.
"""

from operator import itemgetter

from common.config import get_setting
from common.constants import (
    DOCUMENT,
    RERANK_SCORE,
)
from common.logger import get_logger

from retrieval.cross_encoder_model import (
    CrossEncoderModel,
)

logger = get_logger(__name__)


class Reranker:
    """
    CrossEncoder-based reranker.
    """

    def __init__(
        self,
    ) -> None:

        self.top_k = get_setting(
            "reranker",
            "top_k",
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

        reranked_results = [result.copy() for result in results]

        for result, score in zip(
            reranked_results,
            scores,
        ):

            result[RERANK_SCORE] = float(
                score,
            )

        reranked_results.sort(
            key=itemgetter(
                RERANK_SCORE,
            ),
            reverse=True,
        )

        final_results = reranked_results[:top_k]

        for result in final_results:

            result.pop(
                RERANK_SCORE,
                None,
            )

        logger.info(
            "Returned %d reranked documents.",
            len(final_results),
        )

        return final_results
