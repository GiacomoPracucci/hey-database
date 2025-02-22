import logging
from store.vectorstore_client import VectorStore
from src.models.metadata import Metadata

logger = logging.getLogger("hey-database")


class VectorStoreStartup:
    """
    Manages vector store collection initialization and first population.
    Follows same patterns as metadata startup:
    - Check if store exists and is populate
    - Create and populate if needed
    - Handle updates when metadata changes
    """

    def __init__(self, vector_store: VectorStore):
        """
        Args:
            vector_store (VectorStore): initialized vector store instance (that contains the vector store client)
        """
        self.vector_store = vector_store

    def initialize(self, metadata: Metadata) -> bool:
        """
        Initialize and sync the vector store with current metadata state.

        Args:
            metadata: Current metadata state to sync
        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("Initializing vector store collection")
            if not self.vector_store.initialize_collection():
                raise RuntimeError("Failed to initialize vector store collection")

            # Always sync metadata to ensure consistency
            logger.info("Syncing metadata to vector store")
            if not self._sync_metadata(metadata):
                raise RuntimeError("Failed to sync metadata to vector store")

            logger.info("Vector store initialization completed successfully")
            return True

        except Exception as e:
            logger.exception(f"Error during vector store initialization: {str(e)}")
            return False

    def _sync_metadata(self, metadata: Metadata) -> bool:
        """
        Sync current metadata state to vector store through upserts.
        Uses deterministic IDs to ensure proper updates.
        """
        try:
            # Sync table metadata
            for table_name, table_metadata in metadata.tables.items():
                if not self.vector_store.add_table(table_metadata):
                    logger.error(f"Failed to sync table metadata: {table_name}")
                    return False

            # Sync column metadata
            for table_name, table_columns in metadata.columns.items():
                for column_name, column_metadata in table_columns.items():
                    if not self.vector_store.add_column(column_metadata):
                        logger.error(
                            f"Failed to sync column metadata: {table_name}.{column_name}"
                        )
                        # Continue syncing other columns even if one fails
                        continue

            return True

        except Exception as e:
            logger.error(f"Error syncing metadata: {str(e)}")
            return False

    def refresh(self, metadata: Metadata) -> bool:
        """
        Force refresh of vector store data using current metadata
        """
        try:
            return self.vector_store.update_table_documents(metadata.tables)
        except Exception as e:
            logger.error(f"Error refreshing vector store: {str(e)}")
            return False
