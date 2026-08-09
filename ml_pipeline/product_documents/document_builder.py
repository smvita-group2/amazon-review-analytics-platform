"""
Product Document Builder

Builds one product document per unique product.
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
)
from ml_pipeline.common.logger import get_logger
from ml_pipeline.product_documents.formatter import ProductDocumentFormatter
from ml_pipeline.product_documents.review_selector import ReviewSelector

logger = get_logger(__name__)


class ProductDocumentBuilder:
    """
    Builds one document for every unique product.
    """

    DESCRIPTION_LIMIT = 700
    FEATURES_LIMIT = 400

    def __init__(self):
        self.selector = ReviewSelector()
        self.formatter = ProductDocumentFormatter()

    @staticmethod
    def _truncate_text(
        text: str,
        limit: int,
    ) -> str:
        """
        Truncate long text fields to reduce
        embedding and ChromaDB size.
        """

        if pd.isna(text):
            return ""

        text = str(text).strip()

        if len(text) <= limit:
            return text

        return text[:limit].rstrip() + "..."

    def build_documents(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Build product documents for all products.
        """

        logger.info("Building product documents...")

        total_products = dataframe[PARENT_ASIN].nunique()

        logger.info(
            "Found %d unique products.",
            total_products,
        )

        documents = []

        for _, reviews_df in dataframe.groupby(PARENT_ASIN):
            try:
                document = self._build_single_document(
                    reviews_df,
                )

                documents.append(document)

            except Exception:
                logger.exception("Failed to build product document.")

        logger.info(
            "Successfully built %d product documents.",
            len(documents),
        )

        return pd.DataFrame(documents)

    def _build_single_document(
        self,
        reviews_df: pd.DataFrame,
    ) -> dict:
        """
        Build one product document.
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
            description=description,
            features=features,
        )

        return {
            PARENT_ASIN: product[PARENT_ASIN],
            PRODUCT_TITLE: product[PRODUCT_TITLE],
            STORE: product[STORE],
            MAIN_CATEGORY: product[MAIN_CATEGORY],
            SUB_CATEGORY: product[SUB_CATEGORY],
            PRODUCT_AVERAGE_RATING: product[PRODUCT_AVERAGE_RATING],
            PRODUCT_RATING_COUNT: product[PRODUCT_RATING_COUNT],
            PRODUCT_REVIEW_COUNT: len(reviews_df),
            PRODUCT_IMAGE_URL: product[PRODUCT_IMAGE_URL],
            PRODUCT_DOCUMENT: product_document,
        }
