from typing import List
from sqlalchemy import text
from src.metadata.extractors.table.table_metadata_extractor import (
    TableMetadataExtractor,
)
from src.models.metadata import TableRelationship
import logging

logger = logging.getLogger("hey-database")


class PostgresTableMetadataExtractor(TableMetadataExtractor):
    """Implementazione PostgreSQL del retriever di metadati"""

    def _get_row_count(self, table_name: str) -> int:
        """Implementazione PostgreSQL del conteggio righe"""
        query = text(f"SELECT COUNT(*) FROM {self.schema}.{table_name}")
        with self.engine.connect() as connection:
            return connection.execute(query).scalar() or 0

    def _get_table_relationships(self, table_name: str) -> List[TableRelationship]:
        """Recupera tutte le relazioni bidirezionali per una tabella PostgreSQL.
        Interroga information_schema e pg_constraint per trovare sia le relazioni
        in cui la tabella è source (outgoing) che quelle in cui è target (incoming).

        Args:
            table_name: Nome della tabella di cui recuperare le relazioni

        Returns:
            List[TableRelationship]: Lista delle relazioni bidirezionali
        """
        try:
            query = text("""
                WITH fk_info AS (
                    -- Relazioni outgoing (tabella è source)
                    SELECT
                        'outgoing' as direction,
                        confrelid::regclass::text as related_table,
                        a.attname as local_column,
                        af.attname as remote_column,
                        c.conname as constraint_name
                    FROM pg_constraint c
                    JOIN pg_attribute a ON a.attnum = ANY(c.conkey) AND a.attrelid = c.conrelid
                    JOIN pg_attribute af ON af.attnum = ANY(c.confkey) AND af.attrelid = c.confrelid
                    WHERE c.contype = 'f' 
                    AND c.conrelid = (SELECT oid FROM pg_class WHERE relname = :table_name AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = :schema))
                    UNION ALL
                    -- Relazioni incoming (tabella è target)
                    SELECT
                        'incoming' as direction,
                        c.conrelid::regclass::text as related_table,
                        af.attname as local_column,
                        a.attname as remote_column,
                        c.conname as constraint_name
                    FROM pg_constraint c
                    JOIN pg_attribute a ON a.attnum = ANY(c.conkey) AND a.attrelid = c.conrelid
                    JOIN pg_attribute af ON af.attnum = ANY(c.confkey) AND af.attrelid = c.confrelid
                    WHERE c.contype = 'f'
                    AND c.confrelid = (SELECT oid FROM pg_class WHERE relname = :table_name AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = :schema))
                )
                SELECT *
                FROM fk_info
                WHERE related_table NOT LIKE 'pg_%'
                    AND related_table NOT LIKE 'information_schema.%'
                ORDER BY constraint_name, direction;
            """)

            relationships = []
            current_constraint = None
            current_relationship = None

            # Passiamo il fully qualified name come parametro
            with self.engine.connect() as conn:
                result = conn.execute(
                    query, {"table_name": table_name, "schema": self.schema}
                )

                for row in result:
                    # Estrae solo il nome della tabella dal fully qualified name (es: da "schema.tabella" prende "tabella")
                    related_table = row.related_table.split(".")[-1]

                    if current_constraint != row.constraint_name:
                        if current_relationship is not None:
                            relationships.append(current_relationship)

                        current_relationship = TableRelationship(
                            related_table=related_table,
                            direction=row.direction,
                            local_columns=[row.local_column],
                            remote_columns=[row.remote_column],
                        )
                        current_constraint = row.constraint_name
                    else:
                        current_relationship.local_columns.append(row.local_column)
                        current_relationship.remote_columns.append(row.remote_column)

                if current_relationship is not None:
                    relationships.append(current_relationship)

            return relationships

        except Exception as e:
            logger.error(
                f"Errore nel recupero delle relazioni per {table_name}: {str(e)}"
            )
            return []
