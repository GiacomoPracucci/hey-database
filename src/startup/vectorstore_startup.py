from typing import Optional
import logging
from src.store.vectorstore import VectorStore
from src.models.metadata import MetadataState

logger = logging.getLogger("hey-database")


class VectorStoreStartupManager:
    """
    Manages vector store initialization and population.
    Follows same patterns as metadata startup:
    - Check if store exists and is populated
    - Create and populate if needed
    - Handle updates when metadata changes
    """

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    def initialize(self, metadata_state: MetadataState) -> bool:
        """
        Initialize vector store system.
        Should be called AFTER metadata startup is complete.

        Args:
            metadata_state: Current metadata state to use for population

        Returns:
            bool: True if initialization successful
        """
        try:
            # Check if collection exists and is populated
            if self.vector_store.collection_exists():
                logger.info("Vector store collection already exists")
                return True

            # Create and populate collection
            logger.info("Creating and populating vector store collection")
            if not self.vector_store.initialize():
                raise RuntimeError("Failed to initialize vector store collection")

            # Populate with metadata
            if not self.vector_store.populate_store_with_metadata(  # TODO la chiamata corretta è a questo metodo ma prima va allineato il vectorstore includendo anche documenti colonna
                metadata_state.tables
            ):
                raise RuntimeError("Failed to populate vector store with metadata")

            logger.info("Vector store initialization completed successfully")
            return True

        except Exception as e:
            logger.exception(f"Error during vector store initialization: {str(e)}")
            return False

    def refresh(self, metadata_state: MetadataState) -> bool:
        """
        Force refresh of vector store data using current metadata state
        """
        try:
            return self.vector_store.update_table_documents(metadata_state.tables)
        except Exception as e:
            logger.error(f"Error refreshing vector store: {str(e)}")
            return False
