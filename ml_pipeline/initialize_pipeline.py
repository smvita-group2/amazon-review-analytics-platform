"""
Initialization Pipeline

Builds all offline artifacts required by the
Hybrid RAG system.
"""

import pandas as pd
from product_documents.document_builder import ProductDocumentBuilder
from vectordb.persistence import Persistence

from ml_pipeline.common.config import get_setting
from ml_pipeline.common.local_io import (
    read_parquet_local,
    write_parquet_local,
)
from ml_pipeline.common.logger import get_logger
from ml_pipeline.embeddings.embedding_generator import EmbeddingGenerator
from ml_pipeline.retrieval.bm25_builder import BM25Builder

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

        self.document_builder = ProductDocumentBuilder()

        self.embedding_generator = EmbeddingGenerator()

    # ==========================================================
    # Run Pipeline
    # ==========================================================

    def run(
        self,
        category: str,
    ) -> None:

        logger.info(
            "Initializing pipeline for category: %s",
            category,
        )

        dataframe = self._load_cleaned_data(category)

        product_documents = self._build_product_documents(
            dataframe,
        )

        self._save_product_documents(
            product_documents,
            category,
        )

        embeddings = self._generate_embeddings(
            product_documents,
        )

        self._save_embeddings(
            embeddings,
            category,
        )

        self._persist_chromadb(
            embeddings,
            category,
        )

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

        logger.info(
            "Loading cleaned data for category: %s",
            category,
        )

        dataframe = read_parquet_local(
            base_path=get_setting(
                "paths",
                "cleaned",
            ),
            category=category,
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

        logger.info(
            "Saving product documents for category: %s",
            category,
        )

        write_parquet_local(
            dataframe=product_documents,
            base_path=get_setting(
                "paths",
                "product_documents",
            ),
            category=category,
            filename="product_documents.parquet",
        )

        logger.info(
            "Product documents saved successfully.",
        )

    # ==========================================================
    # Generate Embeddings
    # ==========================================================

    def _generate_embeddings(
        self,
        product_documents: pd.DataFrame,
    ) -> pd.DataFrame:

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

        logger.info(
            "Saving embeddings for category: %s",
            category,
        )

        write_parquet_local(
            dataframe=embeddings,
            base_path=get_setting(
                "paths",
                "embeddings",
            ),
            category=category,
            filename="embeddings.parquet",
        )

        logger.info(
            "Embeddings saved successfully.",
        )

    # ==========================================================
    # Persist ChromaDB
    # ==========================================================

    def _persist_chromadb(
        self,
        embeddings: pd.DataFrame,
        category: str,
    ) -> None:

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

        logger.info(
            "ChromaDB persistence completed.",
        )

    # ==========================================================
    # Build BM25
    # ==========================================================

    def _build_bm25(
        self,
        product_documents: pd.DataFrame,
        category: str,
    ) -> None:

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

        logger.info(
            "BM25 index created successfully.",
        )
