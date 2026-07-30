"""
Review Selector

Selects representative reviews for each product.
"""

import pandas as pd

from common.config import get_setting
from common.constants import (
    HELPFUL_VOTE,
    REVIEW_RATING,
    REVIEW_TIMESTAMP,
)
from common.logger import get_logger

logger = get_logger(__name__)


class ReviewSelector:
    """
    Select representative reviews for a product.
    """

    def __init__(self):
        """
        Load review selection configuration.
        """

        self.helpful_reviews = get_setting(
            "review_selection",
            "helpful_reviews",
        )

        self.recent_reviews = get_setting(
            "review_selection",
            "recent_reviews",
        )

        self.total_required_reviews = (
            self.helpful_reviews +
            self.recent_reviews
        )

    def select_reviews(
        self,
        reviews_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Select representative reviews for a product.

        Strategy
        --------
        1. Return all reviews if the product has fewer than the
           configured number of reviews.
        2. Select top helpful reviews using:
              - Helpful Vote (descending)
              - Review Rating (descending)
              - Review Timestamp (descending)
        3. Select most recent reviews.
        4. Merge both sets.
        5. Remove duplicates.
        6. Sort final reviews by timestamp (newest first).
        """

        if reviews_df.empty:

            logger.warning(
                "No reviews found for product."
            )

            return reviews_df

        # --------------------------------------------------
        # Small Review Set
        # --------------------------------------------------

        if len(reviews_df) <= self.total_required_reviews:

            logger.info(
                "Product has only %d reviews. Returning all reviews.",
                len(reviews_df),
            )

            return (
                reviews_df
                .sort_values(
                    by=REVIEW_TIMESTAMP,
                    ascending=False,
                )
                .reset_index(drop=True)
            )

        # --------------------------------------------------
        # Most Helpful Reviews
        # --------------------------------------------------

        helpful_reviews = (
            reviews_df
            .sort_values(
                by=[
                    HELPFUL_VOTE,
                    REVIEW_RATING,
                    REVIEW_TIMESTAMP,
                ],
                ascending=[
                    False,
                    False,
                    False,
                ],
            )
            .head(self.helpful_reviews)
        )

        # --------------------------------------------------
        # Most Recent Reviews
        # --------------------------------------------------

        recent_reviews = (
            reviews_df
            .sort_values(
                by=REVIEW_TIMESTAMP,
                ascending=False,
            )
            .head(self.recent_reviews)
        )

        # --------------------------------------------------
        # Combine Reviews
        # --------------------------------------------------

        selected_reviews = (
            pd.concat(
                [
                    helpful_reviews,
                    recent_reviews,
                ],
                ignore_index=True,
            )
            .drop_duplicates()
            .sort_values(
                by=REVIEW_TIMESTAMP,
                ascending=False,
            )
            .reset_index(drop=True)
        )

        logger.info(
            "Selected %d representative reviews.",
            len(selected_reviews),
        )

        return selected_reviews