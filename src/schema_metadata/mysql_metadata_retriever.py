from typing import List, Any
from sqlalchemy import text
from src.schema_metadata.base_metadata_retriever import DatabaseMetadataRetriever

class MySQLMetadataRetriever(DatabaseMetadataRetriever):
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
            result = connection.execute(query, {"schema": self.schema, "table": table_name})
            return result.scalar() or 0

    def get_table_definition(self, table_name: str) -> str:
        """Recupera il DDL di una tabella usando funzioni di sistema MySQL."""
        try:
            query = text("SHOW CREATE TABLE :schema.:table")

            with self.engine.connect() as conn:
                result = conn.execute(query, {
                    "schema": self.schema,
                    "table": table_name
                })
                return result.fetchone()[1]

        except Exception as e:
            logger.error(f"Errore nel recupero del DDL per {table_name}: {str(e)}")
            return ""

    def _get_column_distinct_values(self, table_name: str, column_name: str, max_values: int = 100) -> List[str]:
        """Implementazione MySQL per il recupero dei valori distinti.

        Args:
            table_name: Nome della tabella
            column_name: Nome della colonna
            max_values: Numero massimo di valori distinti da recuperare

        Returns:
            List[str]: Lista dei valori distinti come stringhe
        """
        try:
            query = text(f"""
                SELECT DISTINCT CAST({column_name} AS CHAR)
                FROM {self.schema}.{table_name}
                WHERE {column_name} IS NOT NULL
                LIMIT :max_values
            """)

            with self.engine.connect() as conn:
                result = conn.execute(query, {"max_values": max_values})
                return [str(row[0]) for row in result]

        except Exception as e:
            logger.warning(f"Failed to get distinct values for {table_name}.{column_name}: {str(e)}")
            return []