"""
ChromaDB Manager

Manages ChromaDB client and collection operations.
"""

from typing import Any

from chromadb import PersistentClient
from chromadb.api.models.Collection import Collection

from common.config import get_setting
from common.logger import get_logger

logger = get_logger(__name__)


class ChromaDBManager:
    """
    Handles all ChromaDB operations.

    Responsibilities
    ----------------
    - Initialize ChromaDB client
    - Create or load category-specific collection
    - Insert vectors
    - Query vectors
    - Delete vectors
    - Reset collection
    """

    def __init__(
        self,
        category: str,
    ) -> None:

        self.category = category

        self.persist_directory = get_setting(
            "chromadb",
            "persist_directory",
        )

        self.collection_name = category

        logger.info("Initializing ChromaDB.")

        logger.info(
            "Persist Directory : %s",
            self.persist_directory,
        )

        logger.info(
            "Category : %s",
            self.category,
        )

        logger.info(
            "Collection Name : %s",
            self.collection_name,
        )

        self.client = PersistentClient(
            path=self.persist_directory,
        )

        self.collection = self._load_collection()

    def _load_collection(self) -> Collection:
        """
        Create or load the category collection.
        """

        collection = self.client.get_or_create_collection(
            name=self.collection_name,
        )

        logger.info(
            "Collection ready: %s",
            collection.name,
        )

        return collection

    def add(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
    ) -> None:
        """
        Add documents to ChromaDB.
        """

        if not ids:

            logger.warning("No documents to add.")

            return

        logger.info(
            "Adding %d documents to '%s'.",
            len(ids),
            self.collection_name,
        )

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        logger.info("Documents added successfully.")

    def query(
        self,
        query_embedding: list[float],
        n_results: int = 5,
        where: dict[str, Any] | None = None,
    ) -> dict:
        """
        Query similar documents.
        """

        logger.info(
            "Searching top %d documents from '%s'.",
            n_results,
            self.collection_name,
        )

        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
        )

    def count(self) -> int:
        """
        Return the number of vectors in the collection.
        """

        return self.collection.count()

    def exists(self) -> bool:
        """
        Return True if the collection contains vectors.
        """

        return self.count() > 0

    def delete(
        self,
        ids: list[str],
    ) -> None:
        """
        Delete vectors by IDs.
        """

        if not ids:

            logger.warning("No IDs provided for deletion.")

            return

        logger.info(
            "Deleting %d documents from '%s'.",
            len(ids),
            self.collection_name,
        )

        self.collection.delete(
            ids=ids,
        )

    def reset(self) -> None:
        """
        Delete all vectors from the collection.
        """

        logger.warning(
            "Resetting collection '%s'.",
            self.collection_name,
        )

        self.client.delete_collection(
            self.collection_name,
        )

        self.collection = self._load_collection()

        logger.info("Collection reset completed.")

    def get_collection(self) -> Collection:
        """
        Return the underlying ChromaDB collection.

        Useful for advanced operations not wrapped
        by this manager.
        """

        return self.collection
