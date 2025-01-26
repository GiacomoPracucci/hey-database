import logging

from src.config.models.db import DatabaseConfig

from src.config.models.metadata import MetadataConfig
from src.llm_handler.llm_handler import LLMHandler

from src.connectors.connector import DatabaseConnector

from src.metadata.extractors.table.table_metadata_extractor import (
    TableMetadataExtractor,
)
from src.metadata.extractors.table.postgres_table_metadata_extractor import (
    PostgresTableMetadataRetriever,
)
from src.metadata.extractors.table.mysql_table_metadata_extractor import (
    MySQLTableMetadataRetriever,
)
from src.metadata.extractors.table.snowflake_table_metadata_extractor import (
    SnowflakeTableMetadataRetriever,
)
from src.metadata.extractors.table.vertica_table_metadata_extractor import (
    VerticaTableMetadataRetriever,
)

from src.metadata.extractors.column.postgres_column_metadata_extractor import (
    PostgresColumnMetadataRetriever,
)
from src.metadata.extractors.column.mysql_column_metadata_extractor import (
    MySQLColumnMetadataRetriever,
)
from src.metadata.extractors.column.snowflake_column_metadata_extractor import (
    SnowflakeColumnMetadataRetriever,
)
from src.metadata.extractors.column.vertica_column_metadata_extractor import (
    VerticaColumnMetadataRetriever,
)

from src.metadata.enhancers.table_metadata_enhancer import TableMetadataEnhancer
from src.metadata.enhancers.column_metadata_enhancer import ColumnMetadataEnhancer


logger = logging.getLogger("hey-database")


class MetadataFactory:
    """Factory for creating metadata components"""

    @staticmethod
    def create_table_metadata_extractor(
        config: DatabaseConfig,  # DB config cause the extractor type depends on the DB type
        db: DatabaseConnector,
    ) -> TableMetadataExtractor:
        extractor_types = {
            "postgres": PostgresTableMetadataRetriever,
            "mysql": MySQLTableMetadataRetriever,
            "snowflake": SnowflakeTableMetadataRetriever,
            "vertica": VerticaTableMetadataRetriever,
        }

        if config.type not in extractor_types:
            raise ValueError(f"Metadata retriever for {config.type} not supported")

        extractor_class = extractor_types[config.type]

        return extractor_class(db=db, schema=config.schema)

    @staticmethod
    def create_table_metadata_enhancer(
        llm_handler: LLMHandler,
    ) -> TableMetadataEnhancer:
        return TableMetadataEnhancer(llm_handler=llm_handler)

    @staticmethod
    def create_column_metadata_extractor(
        config: DatabaseConfig,  # DB config cause the extractor type depends on the DB type
        db: DatabaseConnector,
    ):
        extractor_types = {
            "postgres": PostgresColumnMetadataRetriever,
            "mysql": MySQLColumnMetadataRetriever,
            "snowflake": SnowflakeColumnMetadataRetriever,
            "vertica": VerticaColumnMetadataRetriever,
        }

        if config.type not in extractor_types:
            raise ValueError(f"Metadata retriever for {config.type} not supported")

        extractor_class = extractor_types[config.type]

        return extractor_class(db=db, schema=config.schema)

    @staticmethod
    def create_column_metadata_enhancer(
        llm_handler: LLMHandler,
    ) -> ColumnMetadataEnhancer:
        return ColumnMetadataEnhancer(llm_handler=llm_handler)
