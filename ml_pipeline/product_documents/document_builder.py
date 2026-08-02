"""
Product Document Builder

Builds one enriched product document per unique product
using product metadata, representative reviews, and
review analytics.
"""

import pandas as pd

from ml_pipeline.common.constants import (
    DESCRIPTION_TEXT,
    FEATURES_TEXT,
    MAIN_CATEGORY,
    PARENT_ASIN,
    PRODUCT_AVERAGE_RATING,
    PRODUCT_DOCUMENT,
    PRODUCT_IMAGE_URL,
    PRODUCT_RATING_COUNT,
    PRODUCT_REVIEW_COUNT,
    PRODUCT_TITLE,
    STORE,
    SUB_CATEGORY,
    CONFIDENCE_LEVEL,
    OVERALL_SENTIMENT,
    SENTIMENT_SCORE,
)
from ml_pipeline.common.logger import get_logger
from ml_pipeline.product_documents.formatter import ProductDocumentFormatter
from ml_pipeline.product_documents.review_selector import ReviewSelector

logger = get_logger(__name__)


class ProductDocumentBuilder:
    """
    Builds one enriched document for every product.
    """

    DESCRIPTION_LIMIT = 700
    FEATURES_LIMIT = 400

    def __init__(
        self,
    ):

        self.selector = ReviewSelector()

        self.formatter = ProductDocumentFormatter()

    @staticmethod
    def _truncate_text(
        text: str,
        limit: int,
    ) -> str:
        """
        Truncate long text fields.
        """

        if pd.isna(text):

            return ""

        text = str(text).strip()

        if len(text) <= limit:

            return text

        return text[:limit].rstrip() + "..."

    def build_documents(
        self,
        cleaned_df: pd.DataFrame,
        review_analytics_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Build enriched product documents.
        """

        logger.info(
            "Building product documents...",
        )

        analytics_lookup = (
            review_analytics_df.set_index(
                PARENT_ASIN,
            ).to_dict(
                orient="index",
            )
        )

        documents = []

        total_products = cleaned_df[PARENT_ASIN].nunique()

        logger.info(
            "Found %d products.",
            total_products,
        )

        for parent_asin, reviews_df in cleaned_df.groupby(
            PARENT_ASIN,
        ):

            try:

                analytics = analytics_lookup.get(
                    parent_asin,
                    {},
                )

                document = self._build_single_document(
                    reviews_df=reviews_df,
                    analytics=analytics,
                )

                documents.append(
                    document,
                )

            except Exception:

                logger.exception(
                    "Failed building document for %s",
                    parent_asin,
                )

        logger.info(
            "Successfully built %d documents.",
            len(
                documents,
            ),
        )

        return pd.DataFrame(
            documents,
        )

    def _build_single_document(
        self,
        reviews_df: pd.DataFrame,
        analytics: dict,
    ) -> dict:
        """
        Build one enriched product document.
        """

        product = reviews_df.iloc[0]

        selected_reviews = self.selector.select_reviews(
            reviews_df,
        )

        description = self._truncate_text(
            product.get(
                DESCRIPTION_TEXT,
                "",
            ),
            self.DESCRIPTION_LIMIT,
        )

        features = self._truncate_text(
            product.get(
                FEATURES_TEXT,
                "",
            ),
            self.FEATURES_LIMIT,
        )

        product_document = self.formatter.build_document(
            product=product,
            reviews=selected_reviews,
            analytics=analytics,
            description=description,
            features=features,
        )

        return {
    PARENT_ASIN: product[PARENT_ASIN],
    PRODUCT_TITLE: product[PRODUCT_TITLE],
    STORE: product[STORE],
    MAIN_CATEGORY: product[MAIN_CATEGORY],
    SUB_CATEGORY: product[SUB_CATEGORY],
    PRODUCT_AVERAGE_RATING: product[
        PRODUCT_AVERAGE_RATING
    ],
    PRODUCT_RATING_COUNT: product[
        PRODUCT_RATING_COUNT
    ],
    PRODUCT_REVIEW_COUNT: len(
        reviews_df,
    ),
    PRODUCT_IMAGE_URL: product[
        PRODUCT_IMAGE_URL
    ],
    OVERALL_SENTIMENT: analytics.get(
        OVERALL_SENTIMENT,
        "",
    ),
    CONFIDENCE_LEVEL: analytics.get(
        CONFIDENCE_LEVEL,
        "",
    ),
    SENTIMENT_SCORE: analytics.get(
        SENTIMENT_SCORE,
        None,
    ),
    PRODUCT_DOCUMENT: product_document,
}