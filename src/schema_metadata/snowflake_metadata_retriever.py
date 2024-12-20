from typing import Dict, List
from sqlalchemy import text
import logging
from src.schema_metadata.base_metadata_retriever import DatabaseMetadataRetriever

logger = logging.getLogger('hey-database')

class SnowflakeMetadataRetriever(DatabaseMetadataRetriever):
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
            result = connection.execute(query, {
                "schema": self.schema.upper(),  # Snowflake usa maiuscole di default
                "table": table_name.upper()
            })
            return result.scalar() or 0

    def get_table_definition(self, table_name: str) -> str:
        """Recupera il DDL di una tabella usando funzioni di sistema Snowflake.

        Args:
            table_name: Nome della tabella

        Returns:
            str: DDL della tabella
        """
        try:
            query = text("SELECT GET_DDL('TABLE', :table_ref)")
            table_ref = f"{self.schema}.{table_name}".upper()

            with self.engine.connect() as conn:
                result = conn.execute(query, {"table_ref": table_ref})
                return result.scalar() or ""

        except Exception as e:
            logger.error(f"Errore nel recupero del DDL per {table_name}: {str(e)}")
            return ""

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
                result = connection.execute(query, {
                    "schema": self.schema.upper(),
                    "table": table_name.upper(),
                    "rows": max_rows
                })

                columns = result.keys()
                return [dict(zip(columns, row)) for row in result]

        except Exception as e:
            logger.error(f"Errore nel recupero dei dati di esempio per {table_name}: {str(e)}")
            return []

    def _get_column_distinct_values(self, table_name: str, column_name: str, max_values: int = 100) -> List[str]:
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
                LIMIT :max_values
            """)

            with self.engine.connect() as conn:
                result = conn.execute(query, {"max_values": max_values})
                return [str(row[0]) for row in result]

        except Exception as e:
            logger.warning(f"Failed to get distinct values for {table_name}.{column_name}: {str(e)}")
            return []