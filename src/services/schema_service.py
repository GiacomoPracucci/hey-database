from src.models.metadata import Metadata
import logging

logger = logging.getLogger("hey-database")


class SchemaService:
    def __init__(self, metadata: Metadata):
        self.metadata = metadata

    def get_tables_metadata(self):
        if not self.metadata.tables:
            logger.error("Tables Metadata not initialized")
            return {}
        return self.metadata.tables

    def get_columns_metadata(self):
        if not self.metadata.columns:
            logger.error("Columns Metadata not initialized")
            return {}
        return self.metadata.columns
