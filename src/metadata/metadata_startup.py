from typing import Optional
from datetime import datetime
import logging

from src.metadata.extractors.table.table_metadata_extractor import (
    TableMetadataExtractor,
)
from src.metadata.extractors.column.column_metadata_extractor import (
    ColumnMetadataExtractor,
)
from src.metadata.enhancers.table_metadata_enhancer import TableMetadataEnhancer
from src.metadata.enhancers.column_metadata_enhancer import ColumnMetadataEnhancer
from src.cache.metadata_cache import MetadataCache
from src.models.metadata import MetadataState

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

    def extract_and_enrich_metadata(self) -> MetadataState:
        """
        Core metadata processing:
        1. Extract base metadata from database
        2. Enhance it with LLM-generated descriptions

        Returns:
            MetadataState: Processed metadata state
        """
        tables_metadata = {}
        columns_metadata = {}

        table_list = self.table_extractor.get_tables()

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

        return MetadataState(
            tables=tables_metadata, columns=columns_metadata, last_update=datetime.now()
        )


class MetadataCacheHandler:
    """Handler responsible for cache operations and validation."""

    def __init__(self, cache: MetadataCache):
        self.cache = cache

    def get_cached_metadata(self) -> Optional[MetadataState]:
        """Get metadata from cache if valid"""
        try:
            cached_data = self.cache.get()
            if not cached_data:
                return None

            return MetadataState(
                tables=cached_data.get("tables", {}),
                columns=cached_data.get("columns", {}),
                last_update=cached_data.get("last_update", datetime.now()),
            )
        except Exception as e:
            logger.error(f"Error reading from cache: {str(e)}")
            return None

    def save_metadata(self, state: MetadataState) -> bool:
        """Save metadata to cache"""
        try:
            cache_data = {
                "tables": state.tables,
                "columns": state.columns,
                "last_update": state.last_update,
            }
            return self.cache.set(cache_data)
        except Exception as e:
            logger.error(f"Error saving to cache: {str(e)}")
            return False

    def invalidate(self):
        """Invalidate current cache"""
        self.cache.invalidate()


class MetadataManager:
    """
    Service responsible for orchestrating the metadata initialization process.
    Decides whether to use cache or trigger fresh metadata processing.
    """

    def __init__(
        self,
        metadata_service: MetadataProcessor,
        cache_handler: MetadataCacheHandler,
    ):
        self.metadata_processor = metadata_service
        self.cache_handler = cache_handler
        self._current_state: Optional[MetadataState] = None

    @property
    def state(self) -> Optional[MetadataState]:
        """Access current metadata state"""
        return self._current_state

    def initialize_metadata(self, force_refresh: bool = False) -> bool:
        """
        Initialize metadata system by either:
        1. Loading from cache if available and valid
        2. Processing fresh metadata if needed
        """
        try:
            if not force_refresh:
                # 1. Check if there is a valid cache
                cached_state = self.cache_handler.get_cached_metadata()
                if cached_state:
                    self._current_state = cached_state
                    logger.info("Found valid cached metadata.")
                    return True

            # 2. No valid cache, process fresh metadata
            logger.info(
                "No valid cache found, initializing metadata extraction and enrichment process."
            )
            self._current_state = self.metadata_processor.extract_and_enrich_metadata()

            # 3. Save new metadata to cache
            if self._current_state:
                self.cache_manager.save_metadata(self._current_state)
                return True

            return False

        except Exception as e:
            logger.exception(f"Error during metadata initialization: {str(e)}")
            return False

    def force_refresh(self) -> bool:
        """Force fresh metadata processing"""
        return self.initialize_metadata(force_refresh=True)
