import logging
from src.store.vectorstore import VectorStore
from src.models.metadata import Metadata

logger = logging.getLogger("hey-database")


class VectorStoreStartup:
    """
    Manages vector store initialization and first population.
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
        Initialize vector store system.

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
            if not self.populate_store(metadata):
                raise RuntimeError("Failed to populate vector store with metadata")

            logger.info("Vector store initialization completed successfully")
            return True

        except Exception as e:
            logger.exception(f"Error during vector store initialization: {str(e)}")
            return False

    def populate_store(self, metadata: Metadata) -> bool:
        """
        Populate the vector store with metadata.

        Args:
            metadata (Metadata): metadata state to use for population
        Returns:
            bool: True se il popolamento ha successo o non era necessario
        """
        try:
            # popola solo se la collection è vuota
            if (
                self.vector_store.collection_exists()
                and self.vector_store.client.count(
                    self.vector_store.collection_name
                ).count
                > 0
            ):
                logger.info(
                    "Collection already populated, skipping metadata population"
                )
                return True

            logger.info("Populating collection with metadata")

            # Primo passo: aggiungi i documenti tabella
            for table_name, table_metadata in metadata.tables.items():
                if not self.vector_store.add_table(table_metadata):
                    logger.error(f"Failed to add metadata for table: {table_name}")
                    return False

            # Secondo passo: aggiungi tutti i documenti colonna
            for table_name, table_columns in metadata.columns.items():
                for column_name, column_metadata in table_columns.items():
                    logger.info(
                        f"Processing column metadata for {table_name}.{column_name}"
                    )
                    if not self.vector_store.add_column(column_metadata):
                        logger.error(
                            f"Failed to add column metadata for {table_name}.{column_name}"
                        )
                        continue

            logger.info(
                "Collection successfully populated with table and column metadata"
            )
            return True

        except Exception as e:
            logger.error(f"Error in metadata population: {str(e)}")
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
