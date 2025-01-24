from src.schema_metadata.metadata_retriever import MetadataRetriever
import logging

logger = logging.getLogger("hey-database")


class SchemaService:
    def __init__(self, metadata_extractor: MetadataRetriever):
        self.metadata_extractor = metadata_extractor

    def get_tables_metadata(self):
        return self.metadata_extractor.get_all_tables_metadata()
