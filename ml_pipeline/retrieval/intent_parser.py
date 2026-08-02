"""
Intent Parser

Extracts structured intent from a user query
for the Hybrid RAG retrieval pipeline.
"""

import re

from ml_pipeline.retrieval.intent import Intent


class IntentParser:
    """
    Parses user queries into structured intent.
    """

    PRODUCT_TYPES = {
        "air conditioner": [
            "air conditioner",
            "ac",
            "aircon",
        ],
        "refrigerator": [
            "refrigerator",
            "fridge",
        ],
        "washing machine": [
            "washing machine",
            "washer",
        ],
        "microwave": [
            "microwave",
            "oven",
        ],
        "dishwasher": [
            "dishwasher",
        ],
        "vacuum cleaner": [
            "vacuum",
            "vacuum cleaner",
        ],
        "air purifier": [
            "air purifier",
        ],
        "water purifier": [
            "water purifier",
            "ro",
        ],
        "geyser": [
            "geyser",
            "water heater",
        ],
        "ceiling fan": [
            "ceiling fan",
            "fan",
        ],
        "mixer grinder": [
            "mixer",
            "grinder",
            "mixer grinder",
        ],
        "induction cooktop": [
            "induction",
            "cooktop",
        ],
    }

    BUDGET_KEYWORDS = {
        "budget",
        "cheap",
        "affordable",
        "economical",
        "low cost",
        "value for money",
    }

    PREMIUM_KEYWORDS = {
        "premium",
        "luxury",
        "high end",
        "best",
        "top",
    }

    CAPACITY_PATTERNS = (
        r"\b\d+(\.\d+)?\s*ton\b",
        r"\b\d+\s*kg\b",
        r"\b\d+\s*l(itre|iter)?\b",
    )

    def parse(
        self,
        query: str,
    ) -> Intent:
        """
        Parse a user query.
        """

        normalized_query = query.lower().strip()

        intent = Intent(
            original_query=query,
        )

        intent.product_type = self._extract_product_type(
            normalized_query,
        )

        intent.capacity = self._extract_capacity(
            normalized_query,
        )

        intent.budget = self._contains_keyword(
            normalized_query,
            self.BUDGET_KEYWORDS,
        )

        intent.premium = self._contains_keyword(
            normalized_query,
            self.PREMIUM_KEYWORDS,
        )

        return intent

    def _extract_product_type(
        self,
        query: str,
    ) -> str | None:
        """
        Detect product type.
        """

        for product_type, aliases in self.PRODUCT_TYPES.items():

            if any(
                alias in query
                for alias in aliases
            ):

                return product_type

        return None

    def _extract_capacity(
        self,
        query: str,
    ) -> str | None:
        """
        Extract capacity.
        """

        for pattern in self.CAPACITY_PATTERNS:

            match = re.search(
                pattern,
                query,
            )

            if match:

                return match.group(0)

        return None

    @staticmethod
    def _contains_keyword(
        query: str,
        keywords: set[str],
    ) -> bool:
        """
        Check if any keyword exists.
        """

        return any(
            keyword in query
            for keyword in keywords
        )