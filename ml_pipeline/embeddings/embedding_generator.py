"""
Embedding Generator

Generates embeddings for product document DataFrames.
"""

import numpy as np
import pandas as pd

from ml_pipeline.common.config import get_setting
from ml_pipeline.common.constants import PARENT_ASIN, PRODUCT_DOCUMENT
from ml_pipeline.common.logger import get_logger
from ml_pipeline.embeddings.embedding_model import EmbeddingModel

logger = get_logger(__name__)


class EmbeddingGenerator:
    """
    Generates embeddings for batch product documents with vector dimension trimming.
    """

    @staticmethod
    def _trim_and_normalize(embeddings: np.ndarray, target_dim: int) -> np.ndarray:
        """
        Trim embeddings to target_dim and re-normalize L2 norm.
        """
        if embeddings.shape[1] <= target_dim:
            return embeddings

        trimmed = embeddings[:, :target_dim]
        norms = np.linalg.norm(trimmed, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return trimmed / norms

    def generate_embeddings(
        self,
        product_documents: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Generate embedding vectors for product document DataFrame.
        """
        logger.info("Generating embeddings for %d documents...", len(product_documents))

        if (
            product_documents.empty
            or PRODUCT_DOCUMENT not in product_documents.columns
        ):
            logger.warning(
                "Empty product documents DataFrame or missing '%s' column.",
                PRODUCT_DOCUMENT,
            )
            return pd.DataFrame(columns=[PARENT_ASIN, "embedding"])

        target_dim = get_setting("embedding", "dimension", default=256)
        batch_size = get_setting("embedding", "batch_size", default=128)

        texts = product_documents[PRODUCT_DOCUMENT].tolist()
        embeddings = EmbeddingModel.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        # Apply vector dimension trimming & L2 re-normalization
        embeddings = self._trim_and_normalize(embeddings, target_dim=target_dim)

        embedding_list = [emb.tolist() for emb in embeddings]

        result_df = pd.DataFrame(
            {
                PARENT_ASIN: product_documents[PARENT_ASIN].values,
                "embedding": embedding_list,
            }
        )

        logger.info(
            "Successfully generated %d embeddings (%dd trimmed).",
            len(result_df),
            target_dim,
        )
        return result_df
