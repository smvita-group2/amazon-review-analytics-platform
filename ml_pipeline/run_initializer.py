"""
Run Initializer

Entry point for building all offline
Hybrid RAG artifacts.

Workflow:

Categories
    ↓
Initialize Pipeline
    ↓
Product Documents
    ↓
Embeddings
    ↓
ChromaDB
    ↓
BM25
"""

from common.constants import CATEGORIES
from common.logger import get_logger

from initialize_pipeline import InitializePipeline

# ==========================================================
# Logger
# ==========================================================

logger = get_logger(__name__)


# ==========================================================
# Main
# ==========================================================

def main() -> None:
    """
    Run the initialization pipeline for all categories.
    """

    logger.info(
        "Starting offline initialization pipeline..."
    )

    pipeline = InitializePipeline()

    successful_categories = []
    failed_categories = []

    for category in CATEGORIES:

        logger.info(
            "=" * 80
        )

        logger.info(
            "Processing category: %s",
            category,
        )

        try:

            pipeline.run(
                category,
            )

            successful_categories.append(
                category,
            )

            logger.info(
                "Successfully completed category: %s",
                category,
            )

        except Exception as error:

            failed_categories.append(
                category,
            )

            logger.exception(
                "Failed to initialize category: %s",
                category,
            )

            logger.exception(error)

            continue

    logger.info("=" * 80)

    logger.info(
        "Initialization completed."
    )

    logger.info(
        "Successful Categories (%d): %s",
        len(successful_categories),
        successful_categories,
    )

    logger.info(
        "Failed Categories (%d): %s",
        len(failed_categories),
        failed_categories,
    )


# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":
    main()