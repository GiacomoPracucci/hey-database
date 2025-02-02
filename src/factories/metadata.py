import logging

from src.models.db import DatabaseConfig

from src.llm_handler.llm_handler import LLMHandler

from src.connectors.connector import DatabaseConnector

from src.metadata.extractors.table.table_metadata_extractor import (
    TableMetadataExtractor,
)
from src.metadata.extractors.table.postgres_table_metadata_extractor import (
    PostgresTableMetadataExtractor,
)
from src.metadata.extractors.table.mysql_table_metadata_extractor import (
    MySQLTableMetadataExtractor,
)
from src.metadata.extractors.table.snowflake_table_metadata_extractor import (
    SnowflakeTableMetadataExtractor,
)
from src.metadata.extractors.table.vertica_table_metadata_extractor import (
    VerticaTableMetadataExtractor,
)

from src.metadata.extractors.column.postgres_column_metadata_extractor import (
    PostgresColumnMetadataExtractor,
)
from src.metadata.extractors.column.mysql_column_metadata_extractor import (
    MySQLColumnMetadataExtractor,
)
from src.metadata.extractors.column.snowflake_column_metadata_extractor import (
    SnowflakeColumnMetadataExtractor,
)
from src.metadata.extractors.column.vertica_column_metadata_extractor import (
    VerticaColumnMetadataExtractor,
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
            "postgres": PostgresTableMetadataExtractor,
            "mysql": MySQLTableMetadataExtractor,
            "snowflake": SnowflakeTableMetadataExtractor,
            "vertica": VerticaTableMetadataExtractor,
        }

        if config.type not in extractor_types:
            raise ValueError(f"Metadata Extractor for {config.type} not supported")

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
            "postgres": PostgresColumnMetadataExtractor,
            "mysql": MySQLColumnMetadataExtractor,
            "snowflake": SnowflakeColumnMetadataExtractor,
            "vertica": VerticaColumnMetadataExtractor,
        }

        if config.type not in extractor_types:
            raise ValueError(f"Metadata Extractor for {config.type} not supported")

        extractor_class = extractor_types[config.type]

        return extractor_class(db=db, schema=config.schema)

    @staticmethod
    def create_column_metadata_enhancer(
        llm_handler: LLMHandler,
    ) -> ColumnMetadataEnhancer:
        return ColumnMetadataEnhancer(llm_handler=llm_handler)
