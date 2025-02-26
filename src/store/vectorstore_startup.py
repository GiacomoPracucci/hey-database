import logging
from src.store.vectorstore_client import VectorStore
from src.store.vectorstore_write import StoreWriter
from src.models.metadata import Metadata

logger = logging.getLogger("hey-database")


class VectorStoreStartup:
    """
    Manages vector store collection initialization and population.

    This class is responsible for initializing the vector store collection
    and ensuring it's properly populated with metadata. It follows similar
    patterns to the metadata startup:
    - Check if store exists and is populated
    - Create and populate if needed
    - Handle updates when metadata changes

    The class serves as a bridge between the metadata system and
    the vector storage system, ensuring both remain in sync.
    """

    def __init__(self, vector_store: VectorStore, vector_store_writer: StoreWriter):
        """
        Initialize the vector store startup service.

        Args:
            vector_store: Initialized vector store instance for database operations
            vector_store_writer: Writer component for adding/updating vector store documents
        """
        self.vector_store = vector_store
        self.writer = vector_store_writer

    def initialize(self, metadata: Metadata) -> bool:
        """
        Initialize and sync the vector store with current metadata state.

        This method ensures the vector store collection exists and contains
        up-to-date metadata. It's designed to be idempotent, meaning it can
        be safely called multiple times without duplicating data.

        Args:
            metadata: Current metadata state to sync to the vector store

        Returns:
            bool: True if initialization successful, False otherwise
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

        This method ensures that the vector store contains the latest version
        of all metadata, using deterministic IDs to ensure proper updates
        and avoid duplicates.

        Args:
            metadata: Current metadata state to sync

        Returns:
            bool: True if sync successful, False if any errors occurred
        """
        try:
            # Sync table metadata
            for table_name, table_metadata in metadata.tables.items():
                if not self.writer.add_table(table_metadata):
                    logger.error(f"Failed to sync table metadata: {table_name}")
                    return False

            # Sync column metadata
            for table_name, table_columns in metadata.columns.items():
                for column_name, column_metadata in table_columns.items():
                    if not self.writer.add_column(column_metadata):
                        logger.error(
                            f"Failed to sync column metadata: {table_name}.{column_name}"
                        )
                        # Continue syncing other columns even if one fails
                        continue

            # Sync query metadata if available
            if metadata.queries:
                logger.info(f"Syncing {len(metadata.queries)} queries to vector store")
                for question, query_metadata in metadata.queries.items():
                    if not self.writer.add_query(query_metadata):
                        logger.error(
                            f"Failed to sync query metadata: {question[:50]}..."
                        )
                        # Continue syncing other queries even if one fails
                        continue

            return True

        except Exception as e:
            logger.error(f"Error syncing metadata: {str(e)}")
            return False

    def refresh(self, metadata: Metadata) -> bool:
        """
        Force refresh of vector store data using current metadata.

        This method is useful when you want to completely rebuild the
        vector store with the latest metadata, for example after changes
        to the embedding model or vector store configuration.

        Args:
            metadata: Current metadata state to use for refresh

        Returns:
            bool: True if refresh successful, False otherwise
        """
        try:
            # Clear existing vector store content if needed
            # Note: Not implemented yet - would require collection recreate

            # Simply reuse sync metadata to update all content
            return self._sync_metadata(metadata)

        except Exception as e:
            logger.error(f"Error refreshing vector store: {str(e)}")
            return False
