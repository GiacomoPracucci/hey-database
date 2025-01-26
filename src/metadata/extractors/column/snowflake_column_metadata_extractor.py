from typing import List, Optional
from sqlalchemy import text
import logging
from src.metadata.extractors.columns.column_metadata_extractor import (
    ColumnMetadataExtractor,
)

logger = logging.getLogger("hey-database")


class SnowflakeColumnMetadataExtractor(ColumnMetadataExtractor):
    """Implementazione Snowflake del retriever di metadati"""

    def _get_distinct_values(
        self, table_name: str, column_name: str, max_values: Optional[int] = None
    ) -> List[str]:
        """Implementazione Snowflake per il recupero dei valori distinti.

        Args:
            table_name: Nome della tabella
            column_name: Nome della colonna
            max_values: Numero massimo di valori distinti da recuperare

        Returns:
            List[str]: Lista dei valori distinti come stringhe
        """
        try:
            query = text(f"""
                SELECT DISTINCT TO_VARCHAR({column_name})
                FROM {self.schema.upper()}.{table_name.upper()} 
                SAMPLE (1000 ROWS)
                WHERE {column_name} IS NOT NULL
                {f"LIMIT :max_values" if max_values is not None else ""}
            """)

            with self.engine.connect() as conn:
                result = conn.execute(query, {"max_values": max_values})
                return [str(row[0]) for row in result]

        except Exception as e:
            logger.warning(
                f"Failed to get distinct values for {table_name}.{column_name}: {str(e)}"
            )
            return []
