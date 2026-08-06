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

    # Send only the top 2 reranked products
    MAX_PRODUCTS = 2

    # Reduce prompt size sent to Gemini
    MAX_DOCUMENT_LENGTH = 1000

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
You are an Amazon shopping assistant.

Answer ONLY using the retrieved products.

Rules:
- Do not invent information.
- Do not use outside knowledge.
- If the exact answer is unavailable, answer using the closest retrieved products.
- Mention product names whenever relevant.

Respond using exactly these sections:

Recommendation

Retrieved Products Summary

Review Summary

Overall Sentiment
(Choose one: Positive, Mostly Positive, Mixed, Mostly Negative, Negative)

RETRIEVED PRODUCTS

{context}

USER QUESTION

{query}

ANSWER
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

        documents = documents[: PromptBuilder.MAX_PRODUCTS]

        for index, result in enumerate(
            documents,
            start=1,
        ):

            document = result.get(
                DOCUMENT,
                "",
            )

            if len(document) > PromptBuilder.MAX_DOCUMENT_LENGTH:

                document = (
                    document[: PromptBuilder.MAX_DOCUMENT_LENGTH].rstrip()
                    + "\n\n[Document Truncated]"
                )

            sections.append(f"""
PRODUCT {index}

{document}
""".strip())

        return "\n\n".join(
            sections,
        )
