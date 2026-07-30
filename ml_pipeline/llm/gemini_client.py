"""
Gemini Client

Singleton wrapper for the Google Gemini model.
"""

from google import genai
from google.genai import types

from common.config import get_setting
from common.logger import get_logger
from common.secrets import get_secret

logger = get_logger(__name__)


class GeminiClient:
    """
    Singleton wrapper around the Gemini client.
    """

    _client = None
    _model_name = None
    _temperature = None

    @classmethod
    def _initialize(cls) -> None:
        """
        Initialize the Gemini client.
        """

        if cls._client is not None:

            return

        api_key = get_secret(
            "GEMINI_API_KEY",
        )

        cls._model_name = get_setting(
            "gemini",
            "model_name",
        )

        cls._temperature = get_setting(
            "gemini",
            "temperature",
        )

        cls._client = genai.Client(
            api_key=api_key,
        )

        logger.info(
            "Initialized Gemini model '%s'.",
            cls._model_name,
        )

    @classmethod
    def generate(
        cls,
        prompt: str,
    ) -> str:
        """
        Generate a response from Gemini.

        Parameters
        ----------
        prompt : str
            Prompt sent to Gemini.

        Returns
        -------
        str
            Generated response.
        """

        cls._initialize()

        try:

            response = cls._client.models.generate_content(
                model=cls._model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=cls._temperature,
                ),
            )

            return (
                response.text.strip()
                if response.text
                else ""
            )

        except Exception:

            logger.exception(
                "Gemini generation failed."
            )

            raise