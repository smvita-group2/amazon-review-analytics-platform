"""
Prompt Builder

Builds prompts for the Gemini model using
retrieved product documents.
"""

from common.constants import (
    DOCUMENT,
)


class PromptBuilder:
    """
    Utility class for constructing RAG prompts.
    """

    @staticmethod
    def build(
        query: str,
        documents: list[dict],
    ) -> str:
        """
        Build the final prompt.
        """

        context = PromptBuilder._build_context(
            documents,
        )

        return f"""
You are an expert Amazon shopping assistant.

Answer the user's question ONLY using the retrieved product documents.

Rules:

- Use ONLY the provided product documents.
- Never invent, assume or infer facts that are not present.
- Use information from:
  • Product Information
  • Description
  • Features
  • Representative Reviews
- Compare products whenever appropriate.
- Mention product names in comparisons.
- If multiple products satisfy the request, mention all relevant products.
- If the answer cannot be determined from the retrieved products, reply EXACTLY with:

The requested information is not available in the retrieved products.

Keep the answer concise, factual, well-structured and easy to read.

========================================
RETRIEVED PRODUCT DOCUMENTS
========================================

{context}

========================================
USER QUESTION
========================================

{query}

========================================
ANSWER
========================================
""".strip()

    @staticmethod
    def _build_context(
        documents: list[dict],
    ) -> str:
        """
        Convert retrieved documents into
        formatted prompt context.
        """

        if not documents:

            return "No relevant products were retrieved."

        sections = []

        for index, result in enumerate(
            documents,
            start=1,
        ):

            section = f"""
========================================
PRODUCT {index}
========================================

{result.get(DOCUMENT, "")}
""".strip()

            sections.append(
                section,
            )

        return "\n\n".join(
            sections,
        )
