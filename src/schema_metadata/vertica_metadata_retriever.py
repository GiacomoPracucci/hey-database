from typing import List, Any, Dict
from sqlalchemy import text
from collections import defaultdict
from src.schema_metadata.metadata_retriever import DatabaseMetadataRetriever
import logging

logger = logging.getLogger('hey-database')

class VerticaMetadataRetriever(DatabaseMetadataRetriever):
    """Implementazione Vertica del retriever di metadati"""

    def _get_row_count(self, table_name: str) -> int:
        """Implementazione Vertica del conteggio righe"""
        query = text(f"SELECT COUNT(*) FROM {self.schema}.{table_name}")
        with self.engine.connect() as connection:
            return connection.execute(query).scalar() or 0

    def _get_table_fk_metadata(self, table_name: str) -> List[Dict[str, Any]]:
        """Recupera i metadati delle foreign keys per una tabella Vertica.
        Args:
            table_name: Nome della tabella
        Returns:
            List[Dict[str, Any]]: Lista delle foreign keys
        """
        try:
            # recupera le tabelle disponibili
            available_tables = self._get_available_tables()
            # recupera le foreign keys
            fk_map = self._get_table_fk_constraints(table_name, available_tables)
            # formatta il risultato
            return [{
                "constrained_columns": fk["constrained_columns"],
                "referred_table": fk["referred_table"],
                "referred_columns": fk["referred_columns"]
            } for fk in fk_map.values() if fk["referred_table"]]

        except Exception as e:
            logger.error(f"Errore nel recupero delle foreign keys per {table_name}: {str(e)}")
            return []

    def _get_available_tables(self) -> set:
        """Recupera l'elenco delle tabelle disponibili nello schema.
        Returns:
            set: Set dei nomi delle tabelle disponibili
        """
        query = text("""
            SELECT DISTINCT table_name 
            FROM v_catalog.tables 
            WHERE table_schema = :schema
        """)
        with self.engine.connect() as conn:
            return {row[0] for row in conn.execute(query, {"schema": self.schema})}

    def _get_table_fk_constraints(self, table_name: str, available_tables: set) -> Dict[str, Dict[str, Any]]:
        """Recupera i vincoli di foreign key per una tabella.
        Args:
            table_name: Nome della tabella
            available_tables: Set delle tabelle disponibili
        Returns:
            Dict[str, Dict[str, Any]]: Mappa dei vincoli di foreign key
        """
        query = text("""
            SELECT 
                constraint_name,
                reference_table_schema,
                reference_table_name,
                reference_column_name,
                column_name
            FROM v_catalog.foreign_keys 
            WHERE table_schema = :schema
            AND table_name = :table
            AND reference_table_schema = :schema
            ORDER BY constraint_name, ordinal_position
        """)

        fk_map = defaultdict(lambda: {
            "constrained_columns": [],
            "referred_columns": [],
            "referred_table": "",
            "referred_schema": ""
        })

        with self.engine.connect() as conn:
            result = conn.execute(query, {
                "schema": self.schema,
                "table": table_name
            })

            for row in result:
                if row.reference_table_name in available_tables:
                    fk = fk_map[row.constraint_name]
                    fk["constrained_columns"].append(row.column_name)
                    fk["referred_columns"].append(row.reference_column_name)
                    fk["referred_table"] = row.reference_table_name
                    fk["referred_schema"] = row.reference_table_schema

        return fk_map

    def _get_column_distinct_values(self, table_name: str, column_name: str, max_values: int = 100) -> List[str]:
        """Recupera i valori distinti per una colonna.
        Args:
            table_name: Nome della tabella
            column_name: Nome della colonna
            max_values: Numero massimo di valori distinti da recuperare
        Returns:
            List[str]: Lista dei valori distinti come stringhe
        """
        try:
            query = text(f"""
                SELECT DISTINCT CAST({column_name} AS VARCHAR)
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

    def get_table_definition(self, table_name: str) -> str:
        """Recupera il DDL di una tabella usando EXPORT_TABLES di Vertica.

        Args:
            table_name: Nome della tabella

        Returns:
            str: DDL della tabella
        """
        try:
            query = text("SELECT EXPORT_TABLES('', :table_ref)")
            table_ref = f"{self.schema}.{table_name}"

            with self.engine.connect() as conn:
                result = conn.execute(query, {"table_ref": table_ref})
                return result.scalar() or ""

        except Exception as e:
            logger.error(f"Errore nel recupero del DDL per {table_name}: {str(e)}")
            return ""