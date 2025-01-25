from src.models.metadata import TableMetadata
from typing import List, Any, Dict
from abc import ABC, abstractmethod

from src.connettori.connector import DatabaseConnector
from sqlalchemy import inspect, text
from sqlalchemy.engine import Inspector

import logging

logger = logging.getLogger("hey-database")


class TableMetadataExtractor(ABC):
    def __init__(self, db: DatabaseConnector):
        self.engine = db.engine
        self.inspector: Inspector = inspect(db.engine)
        self.schema = db.schema

    def extract_metadata(self, table_name: str) -> TableMetadata:
        """
        Estrae i metadati base di una tabella.

        Args:
            table_name: Nome della tabella
        Returns:
            TableMetadata: Metadati base della tabella
        """
        # 1. estrazione delle info sulle colonne
        columns = self._get_columns(table_name)

        # 2. estrazione delle info sulle pks
        primary_keys = self._get_primary_keys(table_name)

        # 3. estrazione delle info sulle fks
        foreign_keys = self._get_foreign_keys_relationships(table_name)

        # 4. row count della tabella
        row_count = self._get_row_count(table_name)

        return TableMetadata(
            name=table_name,
            columns=columns,
            primary_keys=primary_keys,
            foreign_keys=foreign_keys,
            row_count=row_count,
        )

    def _get_columns(self, table_name: str) -> List[str]:
        """Recupera la lista delle colonne per una tabella.
        Args:
            table_name: Nome della tabella
        Returns:
            List[Dict[str, Any]]: Lista dei metadati delle colonne
        """
        columns = []
        for col in self.inspector.get_columns(table_name, schema=self.schema):
            columns.append(col["name"])
        return columns

    def _get_primary_keys(self, table_name: str) -> List[str]:
        """Recupera i metadati delle chiavi primarie di una tabella"""
        pk_info = self.inspector.get_pk_constraint(table_name, schema=self.schema)
        return pk_info["constrained_columns"] if pk_info else []

    def _get_foreign_keys_relationships(self, table_name: str) -> List[Dict[str, Any]]:
        """Recupera i metadati delle chiavi esterne di una tabella"""
        foreign_keys = []
        for fk in self.inspector.get_foreign_keys(table_name, schema=self.schema):
            foreign_keys.append(
                {
                    "constrained_columns": fk["constrained_columns"],
                    "referred_table": fk["referred_table"],
                    "referred_columns": fk["referred_columns"],
                }
            )
        return foreign_keys

    @abstractmethod
    def _get_row_count(self, table_name: str) -> int:
        """Recupera il conteggio delle righe per una tabella (implementazione specifica per database)"""
        pass

    def get_sample_data(self, table_name: str, max_rows: int = 3) -> List[Dict]:
        """Recupera dati di esempio da una tabella"""
        try:
            with self.engine.connect() as connection:
                query = text(
                    f"SELECT * FROM {self.schema}.{table_name} LIMIT {max_rows}"
                )
                result = connection.execute(query)

                columns = result.keys()
                return [dict(zip(columns, row)) for row in result]

        except Exception as e:
            logger.error(
                f"Errore nel recupero dei dati di esempio per {table_name}: {str(e)}"
            )
            return []
