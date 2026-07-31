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

from common.config import get_setting
from common.constants import CATEGORIES
from common.logger import get_logger
from common.s3_utils import upload_directory

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

    if successful_categories:

        logger.info("Backing up ChromaDB to Amazon S3...")

        try:

            upload_directory(
                local_directory=get_setting(
                    "chromadb",
                    "persist_directory",
                ),
                s3_prefix=get_setting(
                    "paths",
                    "chromadb_backup",
                ),
            )

            logger.info("ChromaDB backup completed successfully.")

        except Exception:

            logger.exception("Failed to back up ChromaDB.")

    else:

        logger.warning(
            "Skipping ChromaDB backup because no categories were processed successfully."
        )

    logger.info("=" * 80)

    logger.info("Offline initialization pipeline completed.")

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
