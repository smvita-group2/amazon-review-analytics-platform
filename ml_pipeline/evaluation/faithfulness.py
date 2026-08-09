"""
Faithfulness Evaluation

Evaluates whether the generated RAG answer
is supported by the retrieved product context.
"""

import json

from ml_pipeline.llm.gemini_client import GeminiClient


class FaithfulnessEvaluator:
    """
    Evaluates RAG answer faithfulness using Gemini.
    """

    @staticmethod
    def evaluate(
        answer: str,
        documents: list[dict],
    ) -> dict:
        """
        Evaluate whether claims in the generated answer
        are directly supported by the retrieved product context.
        """

        # ==========================================================
        # Validate Answer
        # ==========================================================

        if not answer or not answer.strip():

            return {
                "score": None,
                "supported_claims": 0,
                "total_claims": 0,
                "unsupported_claims": [],
                "claim_analysis": [],
            }

        # ==========================================================
        # Build Retrieved Context
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

            if product_document:

                context_parts.append(f"""
==============================
PRODUCT {index}
==============================

{product_document}
""".strip())

        if not context_parts:

            return {
                "score": None,
                "supported_claims": 0,
                "total_claims": 0,
                "unsupported_claims": [],
                "claim_analysis": [],
            }

        context = "\n\n".join(
            context_parts,
        )

        # ==========================================================
        # Evaluation Prompt
        # ==========================================================

        prompt = f"""
You are a STRICT faithfulness evaluator for an
Amazon shopping Retrieval-Augmented Generation
(RAG) system.

Your task is to determine whether every factual
claim in the AI-generated answer is directly
supported by the retrieved product context.

==================================================
STRICT EVALUATION RULES
==================================================

1. USE ONLY THE RETRIEVED CONTEXT.

2. DO NOT use outside knowledge, assumptions,
   common sense, or world knowledge.

3. Extract individual factual claims from the
   AI-generated answer.

4. Evaluate each factual claim independently.

5. A claim is SUPPORTED only when the retrieved
   context provides direct and sufficient evidence
   for the exact claim.

6. A claim being generally related to the retrieved
   context is NOT sufficient.

7. Do NOT infer information that is not explicitly
   present in the retrieved context.

8. Do NOT strengthen the evidence.

   Example:

   Context:
   "One customer said the product was too narrow."

   Claim:
   "Customers commonly complain about sizing."

   Result:
   UNSUPPORTED

9. Frequency or generalization words such as:

   - common
   - usually
   - often
   - most
   - many
   - frequently
   - generally
   - widely

   require explicit evidence supporting that
   frequency or generalization.

10. A single review does NOT prove that something
    is a common or frequent problem.

11. Do NOT infer product compatibility.

    Example:

    Context:
    "Designed for stove and counter gaps."

    Claim:
    "Works with all kitchen appliances."

    Result:
    UNSUPPORTED

12. Do NOT infer product capabilities.

    Example:

    Context:
    "Easy to clean."

    Claim:
    "Dishwasher safe."

    Result:
    UNSUPPORTED

13. Do NOT infer specifications such as:

    - dimensions
    - materials
    - compatibility
    - durability
    - safety
    - performance
    - warranty
    - availability
    - price

    unless explicitly supported by the context.

14. Product titles, descriptions, features,
    metadata, and reviews may all be used as
    evidence if they directly support the claim.

15. When using review evidence, do not turn one
    customer's opinion into a general statement
    about all customers.

16. A subjective review statement should remain
    attributed to the reviewer.

    Example:

    SUPPORTED:
    "One reviewer found the product easy to clean."

    NOT SUPPORTED:
    "The product is proven to be easy to clean."

17. If evidence is incomplete, ambiguous, or only
    indirectly related, mark the claim UNSUPPORTED.

18. Do NOT reward the answer for being plausible.
    The claim must be supported by the retrieved
    context.

19. Ignore:

    - headings
    - section names
    - formatting
    - conversational phrases
    - opinions that contain no factual claim

20. Evaluate factual claims only.

==================================================
EVIDENCE REQUIREMENT
==================================================

For every claim:

- supported = true

  ONLY when direct evidence exists.

- supported = false

  when evidence is missing, incomplete,
  ambiguous, or requires inference.

For supported claims, provide concise evidence
copied or closely referenced from the retrieved
context.

For unsupported claims, explain briefly why the
retrieved context does not sufficiently support
the claim.

==================================================
SCORING
==================================================

The faithfulness score will NOT be generated by you.

The Python application will calculate it as:

Supported Claims / Total Claims × 100

If there are zero factual claims, the score must
remain null.

==================================================
OUTPUT FORMAT
==================================================

Return ONLY valid JSON.

DO NOT use Markdown.

DO NOT use ```json.

DO NOT add explanations outside the JSON.

Use exactly this structure:

{{
    "claims": [
        {{
            "claim": "Individual factual claim",
            "supported": true,
            "evidence": "Direct evidence from retrieved context",
            "reason": "Why the evidence directly supports the claim"
        }}
    ]
}}

==================================================
RETRIEVED PRODUCT CONTEXT
==================================================

{context}

==================================================
AI GENERATED ANSWER
==================================================

{answer}

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
            # Remove Markdown Code Fences
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

            claims = result.get(
                "claims",
                [],
            )

            if not isinstance(
                claims,
                list,
            ):

                claims = []

            # ======================================================
            # Validate Claims
            # ======================================================

            valid_claims = []

            for claim in claims:

                if not isinstance(
                    claim,
                    dict,
                ):

                    continue

                claim_text = str(
                    claim.get(
                        "claim",
                        "",
                    )
                ).strip()

                if not claim_text:

                    continue

                supported = bool(
                    claim.get(
                        "supported",
                        False,
                    )
                )

                evidence = str(
                    claim.get(
                        "evidence",
                        "",
                    )
                ).strip()

                reason = str(
                    claim.get(
                        "reason",
                        "",
                    )
                ).strip()

                valid_claims.append(
                    {
                        "claim": claim_text,
                        "supported": supported,
                        "evidence": evidence,
                        "reason": reason,
                    }
                )

            # ======================================================
            # Calculate Metrics
            # ======================================================

            total_claims = len(
                valid_claims,
            )

            supported_claims = sum(1 for claim in valid_claims if claim["supported"])

            unsupported_claims = [
                claim for claim in valid_claims if not claim["supported"]
            ]

            # ======================================================
            # Calculate Faithfulness
            # ======================================================

            if total_claims > 0:

                score = (supported_claims / total_claims) * 100

            else:

                score = None

            # ======================================================
            # Return Evaluation
            # ======================================================

            return {
                "score": score,
                "supported_claims": supported_claims,
                "total_claims": total_claims,
                "unsupported_claims": unsupported_claims,
                "claim_analysis": valid_claims,
            }

        except (
            json.JSONDecodeError,
            TypeError,
            ValueError,
        ):

            return {
                "score": None,
                "supported_claims": 0,
                "total_claims": 0,
                "unsupported_claims": [],
                "claim_analysis": [],
            }
