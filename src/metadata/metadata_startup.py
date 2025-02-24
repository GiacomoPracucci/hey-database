from typing import Optional
import logging

from src.metadata.extractors.table.table_metadata_extractor import (
    TableMetadataExtractor,
)
from src.metadata.extractors.column.column_metadata_extractor import (
    ColumnMetadataExtractor,
)
from src.metadata.enhancers.table_metadata_enhancer import TableMetadataEnhancer
from src.metadata.enhancers.column_metadata_enhancer import ColumnMetadataEnhancer
from src.metadata.metadata_cache import MetadataCache
from src.models.metadata import Metadata

logger = logging.getLogger("hey-database")


class MetadataProcessor:
    """Processor responsible for extracting and enriching metadata."""

    def __init__(
        self,
        table_extractor: TableMetadataExtractor,
        column_extractor: ColumnMetadataExtractor,
        table_enhancer: TableMetadataEnhancer,
        column_enhancer: ColumnMetadataEnhancer,
    ):
        self.table_extractor = table_extractor
        self.column_extractor = column_extractor
        self.table_enhancer = table_enhancer
        self.column_enhancer = column_enhancer

    def extract_and_enrich_metadata(self) -> Metadata:
        """
        Core metadata processing:
        1. Extract base metadata from database
        2. Enhance it with LLM-generated descriptions

        Returns:
            MetadataState: Processed metadata state
        """
        tables_metadata = {}
        columns_metadata = {}

        table_list = self.table_extractor.get_tables_names()

        for table_name in table_list:
            logger.debug(f"Processing table: {table_name}")

            # Extract and enhance table metadata
            base_table_metadata = self.table_extractor.extract_metadata(table_name)
            enhanced_table_metadata = self.table_enhancer.enhance(base_table_metadata)
            tables_metadata[table_name] = enhanced_table_metadata

            # Extract and enhance column metadata
            columns_metadata[table_name] = {}
            base_columns_metadata = self.column_extractor.extract_metadata(table_name)

            for col_metadata in base_columns_metadata:
                enhanced_col_metadata = self.column_enhancer.enhance(col_metadata)
                columns_metadata[table_name][col_metadata.name] = enhanced_col_metadata

        return Metadata(tables=tables_metadata, columns=columns_metadata)


class MetadataStartup:
    """
    Service responsible for orchestrating the metadata initialization process.
    Decides whether to use cache or trigger fresh metadata processing.
    """

    def __init__(
        self,
        metadata_service: MetadataProcessor,
        cache_handler: MetadataCache,
    ):
        self.metadata_processor = metadata_service
        self.cache_handler = cache_handler

    def initialize_metadata(self, force_refresh: bool = False) -> Optional[Metadata]:
        """
        Initialize metadata system by either:
        1. Loading from cache if available and valid
        2. Processing fresh metadata if needed
        """
        try:
            if not force_refresh:
                # 1. Check if there is a valid cache
                cached_metadata = self.cache_handler.get()
                if cached_metadata:
                    self.metadata = cached_metadata
                    logger.info("Found valid cached metadata.")
                    return cached_metadata

            # 2. No valid cache, process fresh metadata
            logger.info(
                "No valid cache found, initializing metadata extraction and enrichment process."
            )
            metadata = self.metadata_processor.extract_and_enrich_metadata()

            logger.info("Metadata processing completed successfully.")

            # 3. Save new metadata to cache
            if metadata:
                self.cache_handler.set(metadata)

            return metadata

        except Exception as e:
            logger.exception(f"Error during metadata initialization: {str(e)}")
            return False

    def force_refresh(self) -> bool:
        """Force fresh metadata processing"""
        return self.initialize_metadata(force_refresh=True)
