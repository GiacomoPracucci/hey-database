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
    """
    Processor responsible for extracting and enriching database metadata.

    This class orchestrates the entire metadata processing pipeline,
    from extracting raw schema information from the database to
    enriching it with AI-generated descriptions and analysis.

    The processor ensures all tables and columns are properly processed
    and combined into a unified metadata structure.
    """

    def __init__(
        self,
        table_extractor: TableMetadataExtractor,
        column_extractor: ColumnMetadataExtractor,
        table_enhancer: TableMetadataEnhancer,
        column_enhancer: ColumnMetadataEnhancer,
    ):
        """
        Initialize the metadata processor with all required components.

        Args:
            table_extractor: Component for extracting base table metadata
            column_extractor: Component for extracting base column metadata
            table_enhancer: Component for enriching table metadata
            column_enhancer: Component for enriching column metadata
        """
        self.table_extractor = table_extractor
        self.column_extractor = column_extractor
        self.table_enhancer = table_enhancer
        self.column_enhancer = column_enhancer

    def extract_and_enrich_metadata(self) -> Metadata:
        """
        Process metadata through the entire extraction and enrichment pipeline.

        This method orchestrates the complete metadata processing workflow:
        1. Extract table names from the database
        2. For each table, extract and enrich its metadata
        3. For each table's columns, extract and enrich their metadata
        4. Combine all enriched metadata into a unified structure

        Returns:
            Metadata: Complete processed metadata state
        """
        tables_metadata = {}
        columns_metadata = {}
        queries_metadata = {}  # Empty initially, will be populated by user feedback

        # Get list of all tables in the schema
        table_list = self.table_extractor.get_tables_names()

        for table_name in table_list:
            logger.debug(f"Processing table: {table_name}")

            # Extract base table metadata from database schema
            base_table_metadata = self.table_extractor.extract_metadata(table_name)

            # Enhance table metadata with AI-generated descriptions and analysis
            enhanced_table_metadata = self.table_enhancer.enhance(base_table_metadata)
            tables_metadata[table_name] = enhanced_table_metadata

            # Process columns for this table
            columns_metadata[table_name] = {}
            base_columns_metadata = self.column_extractor.extract_metadata(table_name)

            for col_metadata in base_columns_metadata:
                # Enhance column metadata with AI-generated descriptions and analysis
                enhanced_col_metadata = self.column_enhancer.enhance(col_metadata)
                columns_metadata[table_name][col_metadata.name] = enhanced_col_metadata

        # Combine all processed metadata into unified structure
        return Metadata(
            tables=tables_metadata, columns=columns_metadata, queries=queries_metadata
        )


class MetadataStartup:
    """
    Service responsible for orchestrating the metadata initialization process.

    This class manages the startup sequence for metadata, deciding whether
    to use cached metadata (if valid) or trigger a fresh extraction and
    enrichment process. It serves as the main entry point for initializing
    the system's metadata state.
    """

    def __init__(
        self,
        metadata_processor: MetadataProcessor,
        cache_handler: MetadataCache,
    ):
        """
        Initialize the metadata startup service.

        Args:
            metadata_processor: Component that handles metadata extraction and enrichment
            cache_handler: Component for caching and retrieving metadata
        """
        self.metadata_processor = metadata_processor
        self.cache_handler = cache_handler
        self.metadata = None  # Will hold the current metadata state

    def initialize_metadata(self, force_refresh: bool = False) -> Optional[Metadata]:
        """
        Initialize the system's metadata state.

        This method follows a decision tree to determine the metadata source:
        1. If force_refresh is True, always process fresh metadata
        2. Otherwise, try to load metadata from the cache
        3. If cache is missing or invalid, process fresh metadata
        4. Save newly processed metadata to cache for future use

        Args:
            force_refresh: If True, ignore cache and refresh metadata (default: False)

        Returns:
            Metadata: Initialized metadata state, or None if initialization failed
        """
        try:
            if not force_refresh:
                # 1. Check if there is a valid cache
                cached_metadata = self.cache_handler.get()
                if cached_metadata:
                    self.metadata = cached_metadata
                    logger.info("Found valid cached metadata.")
                    return cached_metadata

            # 2. No valid cache or forced refresh, process fresh metadata
            logger.info(
                "No valid cache found or refresh forced, initializing metadata extraction and enrichment process."
            )
            metadata = self.metadata_processor.extract_and_enrich_metadata()
            self.metadata = metadata

            logger.info("Metadata processing completed successfully.")

            # 3. Save new metadata to cache
            if metadata:
                self.cache_handler.set(metadata)

            return metadata

        except Exception as e:
            logger.exception(f"Error during metadata initialization: {str(e)}")
            return None  # Return None instead of False for type consistency

    def force_refresh(self) -> Optional[Metadata]:
        """
        Force a refresh of metadata regardless of cache state.

        This is a convenience method that calls initialize_metadata
        with force_refresh set to True.

        Returns:
            Metadata: Newly processed metadata, or None if refresh failed
        """
        return self.initialize_metadata(force_refresh=True)
