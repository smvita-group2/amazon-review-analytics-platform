"""
Retrieval Relevance Evaluation

Evaluates whether the top retrieved products
are relevant to the user's query.
"""

import json

from ml_pipeline.llm.gemini_client import GeminiClient


class RetrievalRelevanceEvaluator:
    """
    Evaluates retrieval relevance using Gemini.
    """

    # ==========================================================
    # Configuration
    # ==========================================================

    TOP_K = 5

    # ==========================================================
    # Main Evaluation
    # ==========================================================

    @staticmethod
    def evaluate(
        query: str,
        documents: list[dict],
    ) -> dict:
        """
        Evaluate whether the top retrieved products
        are relevant to the user's query.

        Parameters
        ----------
        query : str
            User's search query.

        documents : list[dict]
            Retrieved product documents.

        Returns
        -------
        dict
            Retrieval relevance evaluation result.
        """

        # ==========================================================
        # Validate Query
        # ==========================================================

        if not query or not query.strip():

            return {
                "score": None,
                "relevant_products": 0,
                "total_products": 0,
                "product_analysis": [],
            }

        # ==========================================================
        # Use ONLY Top 5 Retrieved Products
        # ==========================================================

        documents = documents[: RetrievalRelevanceEvaluator.TOP_K]

        if not documents:

            return {
                "score": None,
                "relevant_products": 0,
                "total_products": 0,
                "product_analysis": [],
            }

        # ==========================================================
        # Build Retrieved Product Context
        # ==========================================================

        context_parts = []

        for index, document in enumerate(
            documents,
            start=1,
        ):

            product_document = document.get(
                "document",
                "",
            )

            metadata = document.get(
                "metadata",
                {},
            )

            product_title = metadata.get(
                "product_title",
                "Unknown Product",
            )

            if not product_document:

                product_document = "No product document available."

            context_parts.append(f"""
==============================
PRODUCT {index}
==============================

Product Title:
{product_title}

Retrieved Product Information:
{product_document}
""".strip())

        context = "\n\n".join(
            context_parts,
        )

        # ==========================================================
        # Evaluation Prompt
        # ==========================================================

        prompt = f"""
You are a STRICT retrieval relevance evaluator
for an Amazon shopping Retrieval-Augmented
Generation (RAG) system.

Your task is to determine whether each of the
retrieved products is relevant to the user's
query.

==================================================
IMPORTANT RULES
==================================================

1. Evaluate ONLY the retrieved products provided
   below.

2. Use ONLY the user's query and the retrieved
   product information.

3. Do NOT use outside knowledge.

4. A product is RELEVANT only if its retrieved
   information directly relates to what the user
   is asking for.

5. Do NOT mark a product relevant merely because
   it belongs to the same broad category.

6. Product category alone is NOT sufficient.

   Example:

   Query:
   "Which video game has the best gameplay?"

   A video game is potentially relevant.

   A kitchen appliance is NOT relevant even though
   it is a product from Amazon.

7. The product should match the user's requested
   product type, purpose, or subject.

8. If the query asks about a specific attribute,
   the retrieved product should provide information
   relevant to that attribute.

9. Do NOT infer relevance from information that is
   not present in the retrieved document.

10. When uncertain, mark the product as
    NOT RELEVANT.

11. Evaluate every retrieved product separately.

12. Do NOT calculate the final percentage yourself.

==================================================
OUTPUT
==================================================

Return ONLY valid JSON.

Do NOT use Markdown.
Do NOT use ```json.
Do NOT add explanations outside the JSON.

Use exactly this structure:

{{
    "products": [
        {{
            "product_index": 1,
            "relevant": true,
            "reason": "Why this product is relevant to the query"
        }}
    ]
}}

Every retrieved product MUST have exactly
one evaluation.

==================================================
USER QUERY
==================================================

{query}

==================================================
TOP RETRIEVED PRODUCTS
==================================================

{context}

==================================================
BEGIN EVALUATION
==================================================
""".strip()

        # ==========================================================
        # Gemini Evaluation
        # ==========================================================

        response, _ = GeminiClient.generate(
            prompt=prompt,
        )

        # ==========================================================
        # Parse Gemini Response
        # ==========================================================

        try:

            response = response.strip()

            # ------------------------------------------------------
            # Remove Markdown JSON Fences
            # ------------------------------------------------------

            if response.startswith("```json"):

                response = response[len("```json") :].strip()

            if response.startswith("```"):

                response = response[len("```") :].strip()

            if response.endswith("```"):

                response = response[: -len("```")].strip()

            # ------------------------------------------------------
            # Parse JSON
            # ------------------------------------------------------

            result = json.loads(
                response,
            )

            products = result.get(
                "products",
                [],
            )

            if not isinstance(
                products,
                list,
            ):

                products = []

            # ======================================================
            # Validate Product Results
            # ======================================================

            valid_results = []

            for index in range(
                1,
                len(documents) + 1,
            ):

                matching_result = None

                for product in products:

                    if not isinstance(
                        product,
                        dict,
                    ):

                        continue

                    try:

                        product_index = int(
                            product.get(
                                "product_index",
                                0,
                            )
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):

                        continue

                    if product_index == index:

                        matching_result = product

                        break

                # --------------------------------------------------
                # Missing Evaluation
                # --------------------------------------------------

                if matching_result is None:

                    valid_results.append(
                        {
                            "product_index": index,
                            "relevant": False,
                            "reason": ("No relevance evaluation " "was returned."),
                        }
                    )

                    continue

                # --------------------------------------------------
                # Extract Evaluation
                # --------------------------------------------------

                relevant = bool(
                    matching_result.get(
                        "relevant",
                        False,
                    )
                )

                reason = str(
                    matching_result.get(
                        "reason",
                        "",
                    )
                ).strip()

                metadata = documents[index - 1].get(
                    "metadata",
                    {},
                )

                product_title = metadata.get(
                    "product_title",
                    "Unknown Product",
                )

                valid_results.append(
                    {
                        "product_index": index,
                        "product_title": product_title,
                        "relevant": relevant,
                        "reason": reason,
                    }
                )

            # ======================================================
            # Calculate Metrics
            # ======================================================

            total_products = len(
                valid_results,
            )

            relevant_products = sum(
                1 for product in valid_results if product["relevant"]
            )

            # ======================================================
            # Calculate Retrieval Relevance
            # ======================================================

            if total_products > 0:

                score = (relevant_products / total_products) * 100

            else:

                score = None

            # ======================================================
            # Return Evaluation
            # ======================================================

            return {
                "score": score,
                "relevant_products": relevant_products,
                "total_products": total_products,
                "product_analysis": valid_results,
            }

        except (
            json.JSONDecodeError,
            TypeError,
            ValueError,
        ):

            return {
                "score": None,
                "relevant_products": 0,
                "total_products": 0,
                "product_analysis": [],
            }
