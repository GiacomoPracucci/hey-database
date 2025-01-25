from sqlalchemy import text
from src.schema_metadata.extractors.table.table_metadata_extractor import (
    TableMetadataExtractor,
)

import logging

logger = logging.getLogger("hey-database")


class MySQLTableMetadataExtractor(TableMetadataExtractor):
    """Implementazione MySQL del retriever di metadati"""

    def _get_row_count(self, table_name: str) -> int:
        """Implementazione MySQL del conteggio righe"""
        query = text("""
            SELECT TABLE_ROWS 
            FROM information_schema.tables 
            WHERE table_schema = :schema 
            AND table_name = :table
        """)
        with self.engine.connect() as connection:
            result = connection.execute(
                query, {"schema": self.schema, "table": table_name}
            )
            return result.scalar() or 0
