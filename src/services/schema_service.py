from src.metadata.metadata_startup import MetadataManager
import logging

logger = logging.getLogger("hey-database")


class SchemaService:
    def __init__(self, metadata_manager: MetadataManager):
        self.metadata_manager = metadata_manager
        self.tables_metadata = metadata_manager.metadata.tables
        self.columns_metadata = metadata_manager.metadata.columns

    def get_tables_metadata(self):
        if not self.metadata_manager.metadata:
            logger.error("Tables Metadata not initialized")
            return {}
        return self.tables_metadata

    def get_columns_metadata(self):
        if not self.metadata_manager.metadata.columns:
            logger.error("Columns Metadata not initialized")
            return {}
        return self.columns_metadata
