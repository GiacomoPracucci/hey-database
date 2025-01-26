from src.metadata.metadata_retriever import MetadataRetriever
import logging

logger = logging.getLogger("hey-database")


class SchemaService:
    def __init__(self, tables):
        self.tables = tables

    def get_tables_metadata(self):
        return self.tables
