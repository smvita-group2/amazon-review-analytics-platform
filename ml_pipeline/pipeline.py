"""
Pipeline

Main application pipeline that coordinates
retrieval and LLM generation.
"""

from llm.gemini_client import GeminiClient
from llm.prompt_builder import PromptBuilder
from retrieval.hybrid_search import HybridSearch

from common.logger import get_logger

logger = get_logger(__name__)


class Pipeline:
    """
    Main application pipeline.
    """

    def __init__(
        self,
        category: str,
    ) -> None:
        """
        Initialize the application pipeline.

        Parameters
        ----------
        category : str
            Product category.
        """

        self.category = category

        self.hybrid_search = HybridSearch(
            category=category,
        )

    def run(
        self,
        query: str,
    ) -> dict:
        """
        Execute the complete Hybrid RAG pipeline.

        Parameters
        ----------
        query : str
            User question.

        Returns
        -------
        dict
            Generated answer and retrieved
            documents.
        """

        if not query.strip():

            raise ValueError("Query cannot be empty.")

        logger.info(
            "Executing pipeline for category '%s'.",
            self.category,
        )

        try:

            documents = self.hybrid_search.search(
                query=query,
            )

            prompt = PromptBuilder.build(
                query=query,
                documents=documents,
            )

            answer = GeminiClient.generate(
                prompt=prompt,
            )

            logger.info("Pipeline execution completed successfully.")

            return {
                "query": query,
                "answer": answer,
                "documents": documents,
            }

        except Exception:

            logger.exception("Pipeline execution failed.")

            raise
