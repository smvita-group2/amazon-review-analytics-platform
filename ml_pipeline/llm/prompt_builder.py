"""
Prompt Builder

Builds prompts for the Gemini model using
retrieved product documents.
"""

from common.constants import (
    DOCUMENT,
    MAIN_CATEGORY,
    METADATA,
    PRODUCT_AVERAGE_RATING,
    PRODUCT_REVIEW_COUNT,
    PRODUCT_TITLE,
    STORE,
    SUB_CATEGORY,
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

        Parameters
        ----------
        query : str
            User question.

        documents : list[dict]
            Retrieved product documents.

        Returns
        -------
        str
            Prompt sent to Gemini.
        """

        context = PromptBuilder._build_context(
            documents,
        )

        return f"""
You are an intelligent shopping assistant.

Answer the user's question ONLY using the provided product information.

Instructions:
- Do not make up facts.
- If the answer cannot be found in the provided context, reply:
  "The requested information is not available in the retrieved products."
- Keep answers concise and factual.
- Compare products when appropriate.
- Mention product names whenever possible.

=========================
Retrieved Product Context
=========================

{context}

=========================
User Question
=========================

{query}

=========================
Answer
=========================
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

            metadata = result.get(
                METADATA,
                {},
            )

            section = f"""
Product {index}

Name:
{metadata.get(PRODUCT_TITLE, "Unknown")}

Category:
{metadata.get(MAIN_CATEGORY, "Unknown")}

Sub Category:
{metadata.get(SUB_CATEGORY, "Unknown")}

Store:
{metadata.get(STORE, "Unknown")}

Average Rating:
{metadata.get(PRODUCT_AVERAGE_RATING, "Unknown")}

Review Count:
{metadata.get(PRODUCT_REVIEW_COUNT, "Unknown")}

Information:
{result.get(DOCUMENT, "")}
""".strip()

            sections.append(
                section,
            )

        return "\n\n".join(
            sections,
        )