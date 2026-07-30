"""
CrossEncoder Model

Provides a singleton instance of the CrossEncoder model.
"""

from sentence_transformers import CrossEncoder

from common.config import get_setting
from common.logger import get_logger

logger = get_logger(__name__)


class CrossEncoderModel:
    """
    Singleton wrapper around the CrossEncoder model.
    """

    _model = None

    @classmethod
    def get_model(
        cls,
    ) -> CrossEncoder:
        """
        Return a singleton CrossEncoder instance.
        """

        if cls._model is None:

            model_name = get_setting(
                "reranker",
                "model_name",
            )

            max_length = get_setting(
                "reranker",
                "max_length",
            )

            logger.info(
                "Loading CrossEncoder '%s'.",
                model_name,
            )

            cls._model = CrossEncoder(
                model_name_or_path=model_name,
                device="cpu",
                max_length=max_length,
            )

            logger.info(
                "CrossEncoder loaded successfully."
            )

        return cls._model

    @classmethod
    def get_model_name(
        cls,
    ) -> str:
        """
        Return the configured model name.
        """

        return get_setting(
            "reranker",
            "model_name",
        )