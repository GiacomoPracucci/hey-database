from typing import List, Any, Dict
from sqlalchemy import text
from collections import defaultdict
from src.schema_metadata.extractors.table.table_metadata_extractor import (
    TableMetadataExtractor,
)
from src.models.metadata import TableRelationship
import logging

logger = logging.getLogger("hey-database")


class VerticaTableMetadataExtractor(TableMetadataExtractor):
    """Implementazione Vertica del retriever di metadati"""

    def _get_row_count(self, table_name: str) -> int:
        """Implementazione Vertica del conteggio righe"""
        query = text(f"SELECT COUNT(*) FROM {self.schema}.{table_name}")
        with self.engine.connect() as connection:
            return connection.execute(query).scalar() or 0

    def _get_foreign_keys_relationships(self, table_name: str) -> List[Dict[str, Any]]:
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
            return [
                {
                    "constrained_columns": fk["constrained_columns"],
                    "referred_table": fk["referred_table"],
                    "referred_columns": fk["referred_columns"],
                }
                for fk in fk_map.values()
                if fk["referred_table"]
            ]

        except Exception as e:
            logger.error(
                f"Errore nel recupero delle foreign keys per {table_name}: {str(e)}"
            )
            return []

    def _get_available_tables(self) -> set:
        """
        Recupera l'elenco delle tabelle disponibili nello schema.

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

    def _get_table_fk_constraints(
        self, table_name: str, available_tables: set
    ) -> Dict[str, Dict[str, Any]]:
        """
        Recupera i vincoli di foreign key per una tabella.

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

        fk_map = defaultdict(
            lambda: {
                "constrained_columns": [],
                "referred_columns": [],
                "referred_table": "",
                "referred_schema": "",
            }
        )

        with self.engine.connect() as conn:
            result = conn.execute(query, {"schema": self.schema, "table": table_name})

            for row in result:
                if row.reference_table_name in available_tables:
                    fk = fk_map[row.constraint_name]
                    fk["constrained_columns"].append(row.column_name)
                    fk["referred_columns"].append(row.reference_column_name)
                    fk["referred_table"] = row.reference_table_name
                    fk["referred_schema"] = row.reference_table_schema

        return fk_map

    def _get_table_relationships(self, table_name: str) -> List[TableRelationship]:
        """Recupera tutte le relazioni bidirezionali per una tabella Vertica.
        Interroga v_catalog.foreign_keys per trovare sia le relazioni in cui la tabella
        è source (outgoing) che quelle in cui è target (incoming).

        Args:
            table_name: Nome della tabella di cui recuperare le relazioni

        Returns:
            List[TableRelationship]: Lista delle relazioni bidirezionali
        """
        try:
            # query che recupera sia le FK outgoing che quelle incoming
            query = text("""
                -- Relazioni outgoing (tabella è source)
                SELECT 
                    'outgoing' as direction,
                    reference_table_name as related_table,
                    column_name as local_column,
                    reference_column_name as remote_column,
                    constraint_name
                FROM v_catalog.foreign_keys 
                WHERE table_schema = :schema
                AND table_name = :table
                
                UNION ALL
                
                -- Relazioni incoming (tabella è target)
                SELECT 
                    'incoming' as direction,
                    table_name as related_table,
                    reference_column_name as local_column,
                    column_name as remote_column,
                    constraint_name
                FROM v_catalog.foreign_keys 
                WHERE reference_table_schema = :schema
                AND reference_table_name = :table
                
                ORDER BY constraint_name, direction
            """)

            relationships = []
            current_constraint = None
            current_relationship = None

            with self.engine.connect() as conn:
                result = conn.execute(
                    query, {"schema": self.schema, "table": table_name}
                )

                for row in result:
                    # se cambia il constraint name, è una nuova relazione
                    if current_constraint != row.constraint_name:
                        # salva la relazione precedente se esiste
                        if current_relationship is not None:
                            relationships.append(current_relationship)

                        # inizia una nuova relazione
                        current_relationship = TableRelationship(
                            related_table=row.related_table,
                            direction=row.direction,
                            local_columns=[row.local_column],
                            remote_columns=[row.remote_column],
                        )
                        current_constraint = row.constraint_name
                    else:
                        # aggiunge colonne alla relazione corrente
                        current_relationship.local_columns.append(row.local_column)
                        current_relationship.remote_columns.append(row.remote_column)

                # aggiunge l'ultima relazione se esiste
                if current_relationship is not None:
                    relationships.append(current_relationship)

            return relationships

        except Exception as e:
            logger.error(
                f"Errore nel recupero delle relazioni per {table_name}: {str(e)}"
            )
            return []
