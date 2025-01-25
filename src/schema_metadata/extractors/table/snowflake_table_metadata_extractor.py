from typing import Dict, List
from sqlalchemy import text
import logging
from src.schema_metadata.extractors.table.table_metadata_extractor import (
    TableMetadataExtractor,
)

logger = logging.getLogger("hey-database")


class SnowflakeTableMetadataRetriever(TableMetadataExtractor):
    """Implementazione Snowflake del retriever di metadati"""

    def _get_row_count(self, table_name: str) -> int:
        """Implementazione Snowflake del conteggio righe.

        In Snowflake, possiamo usare la vista INFORMATION_SCHEMA.TABLES
        che mantiene statistiche aggiornate sulle tabelle.

        Args:
            table_name: Nome della tabella

        Returns:
            int: Numero di righe nella tabella
        """
        query = text("""
            SELECT ROW_COUNT 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = :schema 
            AND TABLE_NAME = :table
        """)

        with self.engine.connect() as connection:
            result = connection.execute(
                query,
                {
                    "schema": self.schema.upper(),  # Snowflake usa maiuscole di default
                    "table": table_name.upper(),
                },
            )
            return result.scalar() or 0

    def get_sample_data(self, table_name: str, max_rows: int = 3) -> List[Dict]:
        """Override del metodo base per gestire le maiuscole in Snowflake.

        Args:
            table_name: Nome della tabella
            max_rows: Numero massimo di righe da recuperare

        Returns:
            List[Dict]: Lista di dizionari contenenti i dati di esempio
        """
        try:
            with self.engine.connect() as connection:
                query = text("""
                    SELECT * 
                    FROM :schema.:table 
                    SAMPLE (:rows ROWS)
                """)
                result = connection.execute(
                    query,
                    {
                        "schema": self.schema.upper(),
                        "table": table_name.upper(),
                        "rows": max_rows,
                    },
                )

                columns = result.keys()
                return [dict(zip(columns, row)) for row in result]

        except Exception as e:
            logger.error(
                f"Errore nel recupero dei dati di esempio per {table_name}: {str(e)}"
            )
            return []
