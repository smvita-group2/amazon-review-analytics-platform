"""
Prompt Builder

Builds prompts for the Gemini model using
retrieved product documents.
"""

from common.constants import (
    PRODUCT_NAME_KEY,
    FINAL_CATEGORY_KEY,
    SUB_CATEGORY_KEY,
    STORE_KEY,
    PRICE_KEY,
    AVERAGE_RATING_KEY,
    REVIEW_COUNT_KEY,
    PRODUCT_DOCUMENT_KEY,
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

        for index, document in enumerate(
            documents,
            start=1,
        ):

            product_name = document.get(
                PRODUCT_NAME_KEY,
                "Unknown",
            )

            category = document.get(
                FINAL_CATEGORY_KEY,
                "Unknown",
            )

            sub_category = document.get(
                SUB_CATEGORY_KEY,
                "Unknown",
            )

            store = document.get(
                STORE_KEY,
                "Unknown",
            )

            price = document.get(
                PRICE_KEY,
                "Unknown",
            )

            rating = document.get(
                AVERAGE_RATING_KEY,
                "Unknown",
            )

            review_count = document.get(
                REVIEW_COUNT_KEY,
                "Unknown",
            )

            description = document.get(
                PRODUCT_DOCUMENT_KEY,
                "",
            )

            section = f"""
Product {index}

Name:
{product_name}

Category:
{category}

Sub Category:
{sub_category}

Store:
{store}

Price:
{price}

Average Rating:
{rating}

Review Count:
{review_count}

Information:
{description}
""".strip()

            sections.append(section)

        return "\n\n".join(
            sections,
        )