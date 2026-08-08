"""
Pipeline

Main application pipeline that coordinates
retrieval and LLM generation.
"""

from ml_pipeline.common.logger import get_logger
from ml_pipeline.llm.gemini_client import GeminiClient
from ml_pipeline.llm.prompt_builder import PromptBuilder
from ml_pipeline.retrieval.hybrid_search import HybridSearch


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
            Generated answer, token usage,
            and retrieved documents.
        """

        if not query.strip():

            raise ValueError(
                "Query cannot be empty."
            )

        logger.info(
            "Executing pipeline for category '%s'.",
            self.category,
        )

        try:

            # ==================================================
            # Hybrid Retrieval
            # ==================================================

            documents = self.hybrid_search.search(
                query=query,
            )

            # ==================================================
            # Prompt Construction
            # ==================================================

            prompt = PromptBuilder.build(
                query=query,
                documents=documents,
            )

            # ==================================================
            # Gemini Generation
            # ==================================================

            answer, total_tokens = GeminiClient.generate(
                prompt=prompt,
            )

            logger.info(
                "Gemini generation completed | Tokens=%s",
                total_tokens,
            )

            logger.info(
                "Pipeline execution completed successfully."
            )

            # ==================================================
            # DEBUG
            # ==================================================

            print(
                "\n========== FIRST DOCUMENT =========="
            )

            if documents:

                print(
                    documents[0]
                )

            else:

                print(
                    "No documents returned."
                )

            print(
                "====================================\n"
            )

            # ==================================================
            # Pipeline Result
            # ==================================================

            return {
                "query": query,
                "answer": answer,
                "documents": documents,
                "total_tokens": total_tokens,
            }

        except Exception:

            logger.exception(
                "Pipeline execution failed."
            )

            raise