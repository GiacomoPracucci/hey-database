from src.models.metadata import ColumnMetadata
from typing import List
from abc import ABC, abstractmethod

from src.connettori.connector import DatabaseConnector
from sqlalchemy import inspect
from sqlalchemy.engine import Inspector


class ColumnMetadataExtractor(ABC):
    def __init__(self, db: DatabaseConnector):
        self.engine = db.engine
        self.inspector: Inspector = inspect(db.engine)
        self.schema = db.schema

    def extract_metadata(self, table_name: str) -> List[ColumnMetadata]:
        """Recupera i metadati delle colonne per una tabella.
        Args:
            table_name: Nome della tabella
        Returns:
            List[Dict[str, Any]]: Lista dei metadati delle colonne
        """
        columns = []
        for col in self.inspector.get_columns(table_name, schema=self.schema):
            column_info = {
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col["nullable"],
            }

            if self.metadata_config.retrieve_distinct_values:
                column_info["distinct_values"] = self._get_distinct_values(
                    table_name,
                    col["name"],
                    max_values=self.metadata_config.max_distinct_values,
                )

            columns.append(column_info)
        return columns

    @abstractmethod
    def _get_distinct_values(
        self, table_name: str, column_name: str, max_values: int
    ) -> List[str]:
        """Recupera i valori distinti per una colonna.
        Args:
            table_name: Nome della tabella
            column_name: Nome della colonna
            max_values: Numero massimo di valori distinti da recuperare
        Returns:
            List[str]: Lista dei valori distinti
        """
        pass
