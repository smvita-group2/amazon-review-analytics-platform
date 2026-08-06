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
You are an Amazon shopping assistant.

Use ONLY the retrieved product information below.

Rules:

- Never invent or assume information.
- Never use outside knowledge.
- Answer ONLY using the retrieved products.
- Mention product names whenever relevant.
- Base the review summary and sentiment ONLY on the
  representative reviews.
- If the exact product or information is not found,
  briefly state that and continue by describing the
  retrieved products.
- ALWAYS complete every section below.

Always respond using this format:

Recommendation:
- Answer the user's question.
- If the exact answer is unavailable, briefly explain
  that the retrieved products do not contain the
  requested information and continue with the closest
  retrieved products.

Retrieved Products Summary:
- Summarize the retrieved products in 2-3 concise
  sentences.
- Mention the main product types that were retrieved.

Review Summary:
- Summarize the representative customer reviews in
  1-2 concise sentences.
- Mention the most common strengths and weaknesses
  if available.

Overall Sentiment:
- Choose ONLY one:
  Positive
  Mostly Positive
  Mixed
  Mostly Negative
  Negative

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

            sections.append(
                f"""
==============================
PRODUCT {index}
==============================

{document}
""".strip()
            )

        return "\n\n".join(
            sections,
        )