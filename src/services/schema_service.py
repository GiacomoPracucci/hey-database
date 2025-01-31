from src.metadata.metadata_startup import MetadataManager
import logging

logger = logging.getLogger("hey-database")


class SchemaService:
    def __init__(self, metadata_manager: MetadataManager):
        self.metadata_manager = metadata_manager

    def get_tables_metadata(self):
        if not self.metadata_manager.state:
            logger.error("Metadata not initialized")
            return {}
        return self.metadata_manager.state.tables
