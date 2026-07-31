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
    ↓
Backup ChromaDB
"""

from initialize_pipeline import InitializePipeline

from ml_pipeline.common.constants import CATEGORIES
from ml_pipeline.common.logger import get_logger

# from ml_pipeline.common.config import get_setting
# from ml_pipeline.common.s3_utils import upload_directory

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

    logger.info("Starting offline initialization pipeline...")

    pipeline = InitializePipeline()

    successful_categories = []
    failed_categories = []

    for category in CATEGORIES:

        logger.info("=" * 80)

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

        except Exception:

            failed_categories.append(
                category,
            )

            logger.exception(
                "Failed to initialize category: %s",
                category,
            )

            continue

    logger.info("=" * 80)

    # ======================================================


# Backup ChromaDB
# ======================================================

logger.info("Skipping ChromaDB backup to S3 (local execution).")


# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":
    main()
