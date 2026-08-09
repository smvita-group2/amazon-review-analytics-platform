"""
Embedding Model

Singleton wrapper around SentenceTransformer model.
"""

from typing import Any

import torch
from sentence_transformers import SentenceTransformer

from ml_pipeline.common.config import get_setting
from ml_pipeline.common.logger import get_logger

logger = get_logger(__name__)


class EmbeddingModel:
    """
    SentenceTransformer model wrapper.
    """

    _model: SentenceTransformer | None = None

    @classmethod
    def get_model(cls) -> SentenceTransformer:
        """
        Lazy load SentenceTransformer model instance.
        """
        if cls._model is None:
            model_name = get_setting("embedding", "model_name")
            logger.info("Loading SentenceTransformer model: %s", model_name)
            cls._model = SentenceTransformer(model_name)
            max_seq_length = get_setting("embedding", "max_seq_length")
            if max_seq_length:
                cls._model.max_seq_length = max_seq_length
        return cls._model

    @classmethod
    def encode(
        cls,
        sentences: str | list[str],
        convert_to_numpy: bool = True,
        normalize_embeddings: bool = True,
        **kwargs: Any,
    ) -> Any:
        """
        Encode text sentences into embeddings using torch.inference_mode.
        """
        model = cls.get_model()
        with torch.inference_mode():
            return model.encode(
                sentences,
                convert_to_numpy=convert_to_numpy,
                normalize_embeddings=normalize_embeddings,
                **kwargs,
            )
