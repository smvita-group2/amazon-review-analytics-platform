"""
Product Document Formatter

Builds an enriched product document for embedding into
the Hybrid RAG vector database.
"""

import pandas as pd

from ml_pipeline.common.constants import (
    MAIN_CATEGORY,
    PRODUCT_AVERAGE_RATING,
    PRODUCT_RATING_COUNT,
    PRODUCT_TITLE,
    STORE,
    SUB_CATEGORY,
)
from ml_pipeline.common.logger import get_logger
from ml_pipeline.common.utils import (
    format_number,
    format_rating,
    safe_string,
)

logger = get_logger(__name__)


class ProductDocumentFormatter:
    """
    Formats a product into a structured document
    for semantic retrieval.
    """

    MAX_REVIEW_LENGTH = 500

    def build_document(
        self,
        product: pd.Series,
        reviews: pd.DataFrame,
        analytics: dict,
        description: str,
        features: str,
    ) -> str:
        """
        Build the complete product document.
        """

        sections = [
            self._format_product_information(product),
            self._format_customer_insights(analytics),
            self._format_description(description),
            self._format_features(features),
            self._format_reviews(reviews),
        ]

        return "\n\n".join(
            section
            for section in sections
            if section.strip()
        )

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
    # Customer Insights
    # ======================================================

    def _format_customer_insights(
        self,
        analytics: dict,
    ) -> str:

        if not analytics:

            return ""

        return (
            "==============================\n"
            "CUSTOMER INSIGHTS\n"
            "==============================\n\n"
            f"Overall Sentiment: {analytics.get('overall_sentiment', 'Unknown')}\n"
            f"Sentiment Score: {analytics.get('sentiment_score', 'N/A')} / 100\n"
            f"Confidence Level: {analytics.get('confidence_level', 'Unknown')}\n"
            f"Review Count: {analytics.get('review_count', 0)}\n"
            f"Positive Reviews: {analytics.get('positive_percentage', 0)}%\n"
            f"Neutral Reviews: {analytics.get('neutral_percentage', 0)}%\n"
            f"Negative Reviews: {analytics.get('negative_percentage', 0)}%\n"
            f"Verified Purchases: {analytics.get('verified_purchase_percentage', 0)}%\n"
            f"Average Helpful Votes: {analytics.get('average_helpful_vote', 0)}"
        )

    # ======================================================
    # Description
    # ======================================================

    def _format_description(
        self,
        description: str,
    ) -> str:

        description = safe_string(description)

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
        features: str,
    ) -> str:

        features = safe_string(features)

        if not features:

            return ""

        return (
            "==============================\n"
            "FEATURES\n"
            "==============================\n\n"
            f"{features}"
        )

    # ======================================================
    # Representative Reviews
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

            review_text = safe_string(
                review.review_text,
            )

            if len(review_text) > self.MAX_REVIEW_LENGTH:

                review_text = (
                    review_text[
                        : self.MAX_REVIEW_LENGTH
                    ].rstrip()
                    + "..."
                )

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
                    review_text,
                    "",
                    "-" * 60,
                    "",
                ]
            )

        return "\n".join(lines)