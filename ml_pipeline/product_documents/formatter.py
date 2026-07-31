"""
Product Document Formatter

Builds a structured text document for a product that will
be embedded into the vector database.
"""

import pandas as pd

from common.constants import (
    DESCRIPTION_TEXT,
    FEATURES_TEXT,
    HELPFUL_VOTE,
    MAIN_CATEGORY,
    PRODUCT_AVERAGE_RATING,
    PRODUCT_RATING_COUNT,
    PRODUCT_TITLE,
    REVIEW_RATING,
    REVIEW_TEXT,
    REVIEW_TITLE,
    STORE,
    SUB_CATEGORY,
    VERIFIED_PURCHASE,
)

from common.logger import get_logger
from common.utils import (
    format_number,
    format_rating,
    safe_string,
)

logger = get_logger(__name__)


class ProductDocumentFormatter:
    """
    Formats product information and representative reviews
    into a single text document.
    """

    def build_document(
        self,
        product: pd.Series,
        reviews: pd.DataFrame,
    ) -> str:
        """
        Build the complete product document.
        """

        sections = [
            self._format_product_information(product),
            self._format_description(product),
            self._format_features(product),
            self._format_reviews(reviews),
        ]

        return "\n\n".join(section for section in sections if section.strip())

    # ======================================================
    # Product Information
    # ======================================================

    def _format_product_information(
        self,
        product: pd.Series,
    ) -> str:

        return (
            "==============================\n"
            "PRODUCT INFORMATION\n"
            "==============================\n\n"
            f"Title: {safe_string(product.get(PRODUCT_TITLE))}\n"
            f"Store: {safe_string(product.get(STORE))}\n"
            f"Main Category: {safe_string(product.get(MAIN_CATEGORY))}\n"
            f"Sub Category: {safe_string(product.get(SUB_CATEGORY))}\n"
            f"Average Rating: {format_rating(product.get(PRODUCT_AVERAGE_RATING))}\n"
            f"Total Ratings: {format_number(product.get(PRODUCT_RATING_COUNT))}"
        )

    # ======================================================
    # Description
    # ======================================================

    def _format_description(
        self,
        product: pd.Series,
    ) -> str:

        description = safe_string(product.get(DESCRIPTION_TEXT))

        if not description:

            return ""

        return (
            "==============================\n"
            "DESCRIPTION\n"
            "==============================\n\n"
            f"{description}"
        )

    # ======================================================
    # Features
    # ======================================================

    def _format_features(
        self,
        product: pd.Series,
    ) -> str:

        features = safe_string(product.get(FEATURES_TEXT))

        if not features:

            return ""

        return (
            "==============================\n"
            "FEATURES\n"
            "==============================\n\n"
            f"{features}"
        )

    # ======================================================
    # Reviews
    # ======================================================

    def _format_reviews(
        self,
        reviews: pd.DataFrame,
    ) -> str:

        if reviews.empty:

            return ""

        lines = [
            "==============================",
            "REPRESENTATIVE REVIEWS",
            "==============================",
            "",
        ]

        for index, review in enumerate(
            reviews.itertuples(index=False),
            start=1,
        ):

            lines.extend(
                [
                    f"Review {index}",
                    f"Rating: {review.review_rating}/5",
                    f"Verified Purchase: {'Yes' if review.verified_purchase else 'No'}",
                    f"Helpful Votes: {review.helpful_vote}",
                    "",
                    f"Title: {safe_string(review.review_title)}",
                    "",
                    "Review:",
                    safe_string(review.review_text),
                    "",
                    "-" * 60,
                    "",
                ]
            )

        return "\n".join(lines)
