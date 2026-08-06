"""
Prompt Builder

Builds prompts for Gemini using retrieved
Hybrid RAG product documents.
"""

from ml_pipeline.common.constants import (
    DOCUMENT,
)


class PromptBuilder:
    """
    Utility class for constructing RAG prompts.
    """

    MAX_PRODUCTS = 3
    MAX_DOCUMENT_LENGTH = 1800

    @staticmethod
    def build(
        query: str,
        documents: list[dict],
    ) -> str:
        """
        Build the final Gemini prompt.
        """

        context = PromptBuilder._build_context(
            documents,
        )

        return f"""
You are an expert Amazon shopping assistant.

Answer the user's question ONLY using the retrieved product information.

Rules:

- Use ONLY the retrieved products.
- Never invent facts.
- If the answer is unavailable, reply exactly:

The requested information is not available in the retrieved products.

- Compare products when appropriate.
- Mention product names.
- Keep the answer concise, factual and well structured.

==============================
RETRIEVED PRODUCTS
==============================

{context}

==============================
USER QUESTION
==============================

{query}

==============================
ANSWER
==============================
""".strip()

    @staticmethod
    def _build_context(
        documents: list[dict],
    ) -> str:
        """
        Convert retrieved documents into
        prompt context.
        """

        if not documents:

            return "No relevant products were retrieved."

        sections = []

        # Only send the best reranked products
        documents = documents[: PromptBuilder.MAX_PRODUCTS]

        for index, result in enumerate(
            documents,
            start=1,
        ):

            document = result.get(
                DOCUMENT,
                "",
            )

            # Reduce Gemini input size
            if len(document) > PromptBuilder.MAX_DOCUMENT_LENGTH:

                document = (
                    document[: PromptBuilder.MAX_DOCUMENT_LENGTH].rstrip()
                    + "\n\n[Document Truncated]"
                )

            section = f"""
==============================
PRODUCT {index}
==============================

{document}
""".strip()

            sections.append(
                section,
            )

        return "\n\n".join(
            sections,
        )
