"""
Initialization Pipeline

Builds all offline artifacts required by the
Hybrid RAG system.

Pipeline:

S3 Cleaned Data
        │
        ▼
Product Documents
        │
        ▼
Embeddings
        │
        ▼
ChromaDB
        │
        ▼
BM25
"""

import pandas as pd

from common.config import get_setting
from common.logger import get_logger

from common.s3_io import (
    read_parquet_from_s3,
    write_parquet_to_s3,
)

from embeddings.embedding_generator import (
    EmbeddingGenerator,
)

from product_documents.document_builder import (
    ProductDocumentBuilder,
)

from retrieval.bm25_builder import (
    BM25Builder,
)

from vectordb.persistence import (
    Persistence,
)

# ==========================================================
# Logger
# ==========================================================

logger = get_logger(__name__)


# ==========================================================
# Initialization Pipeline
# ==========================================================


class InitializePipeline:
    """
    Orchestrates the offline initialization pipeline
    for the Hybrid RAG system.
    """

    def __init__(self) -> None:
        """
        Initialize all pipeline components.
        """

        self.document_builder = ProductDocumentBuilder()

        self.embedding_generator = EmbeddingGenerator()

    # ==========================================================
    # Run Pipeline
    # ==========================================================

    def run(
        self,
        category: str,
    ) -> None:
        """
        Build all retrieval artifacts for a single category.
        """

        logger.info(
            "Initializing pipeline for category: %s",
            category,
        )

        # Step 1
        dataframe = self._load_cleaned_data(
            category,
        )

        # Step 2
        product_documents = self._build_product_documents(
            dataframe,
        )

        # Step 3
        self._save_product_documents(
            product_documents,
            category,
        )

        # Step 4
        embeddings = self._generate_embeddings(
            product_documents,
        )

        # Step 5
        self._save_embeddings(
            embeddings,
            category,
        )

        # Step 6
        self._persist_chromadb(
            embeddings,
            category,
        )

        # Step 7
        self._build_bm25(
            product_documents,
            category,
        )

        logger.info(
            "Initialization completed for category: %s",
            category,
        )

    # ==========================================================
    # Load Cleaned Data
    # ==========================================================

    def _load_cleaned_data(
        self,
        category: str,
    ) -> pd.DataFrame:
        """
        Load the cleaned dataset for a category from Amazon S3.
        """

        logger.info(
            "Loading cleaned data for category: %s",
            category,
        )

        s3_key = f"{get_setting('paths', 'cleaned')}" f"/{category}/"

        dataframe = read_parquet_from_s3(
            s3_key,
        )

        logger.info(
            "Loaded %d records.",
            len(dataframe),
        )

        return dataframe

    # ==========================================================
    # Build Product Documents
    # ==========================================================

    def _build_product_documents(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Build product documents from the cleaned dataset.
        """

        logger.info("Building product documents...")

        product_documents = self.document_builder.build_documents(
            dataframe,
        )

        logger.info(
            "Built %d product documents.",
            len(product_documents),
        )

        return product_documents

    # ==========================================================
    # Save Product Documents
    # ==========================================================

    def _save_product_documents(
        self,
        product_documents: pd.DataFrame,
        category: str,
    ) -> None:
        """
        Save product documents to Amazon S3.
        """

        logger.info(
            "Saving product documents for category: %s",
            category,
        )

        s3_key = f"{get_setting('paths', 'product_documents')}" f"/{category}/"

        write_parquet_to_s3(
            dataframe=product_documents,
            s3_key=s3_key,
        )

        logger.info("Product documents saved successfully.")

    # ==========================================================
    # Generate Embeddings
    # ==========================================================

    def _generate_embeddings(
        self,
        product_documents: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Generate embeddings for product documents.
        """

        logger.info("Generating embeddings...")

        embeddings = self.embedding_generator.generate_embeddings(
            product_documents,
        )

        logger.info(
            "Generated %d embeddings.",
            len(embeddings),
        )

        return embeddings

    # ==========================================================
    # Save Embeddings
    # ==========================================================

    def _save_embeddings(
        self,
        embeddings: pd.DataFrame,
        category: str,
    ) -> None:
        """
        Save embeddings to Amazon S3.
        """

        logger.info(
            "Saving embeddings for category: %s",
            category,
        )

        s3_key = f"{get_setting('paths', 'embeddings')}" f"/{category}/"

        write_parquet_to_s3(
            dataframe=embeddings,
            s3_key=s3_key,
        )

        logger.info("Embeddings saved successfully.")

    # ==========================================================
    # Persist ChromaDB
    # ==========================================================

    def _persist_chromadb(
        self,
        embeddings: pd.DataFrame,
        category: str,
    ) -> None:
        """
        Persist embeddings into ChromaDB.
        """

        logger.info(
            "Persisting embeddings for category: %s",
            category,
        )

        persistence = Persistence(
            category=category,
        )

        persistence.persist(
            dataframe=embeddings,
            reset_collection=True,
        )

        logger.info("ChromaDB persistence completed.")

    # ==========================================================
    # Build BM25
    # ==========================================================

    def _build_bm25(
        self,
        product_documents: pd.DataFrame,
        category: str,
    ) -> None:
        """
        Build and persist the BM25 index.
        """

        logger.info(
            "Building BM25 index for category: %s",
            category,
        )

        bm25_builder = BM25Builder(
            category=category,
        )

        bm25_builder.build(
            product_documents,
        )

        logger.info("BM25 index created successfully.")
