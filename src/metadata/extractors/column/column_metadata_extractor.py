from src.models.metadata import ColumnMetadata
from typing import List
from abc import ABC, abstractmethod

from src.connectors.connector import DatabaseConnector
from sqlalchemy import inspect
from sqlalchemy.engine import Inspector


class ColumnMetadataExtractor(ABC):
    """Abstract base class for extracting column metadata from database tables"""

    def __init__(self, db: DatabaseConnector, schema: str):
        self.engine = db.engine
        self.inspector: Inspector = inspect(db.engine)
        self.schema = schema

    def extract_metadata(self, table_name: str) -> List[ColumnMetadata]:
        """
        Retrieves column metadata for a given table.

        Args:
            table_name: Name of the table

        Returns:
            List[ColumnMetadata]: List of column metadata objects
        """
        columns = []
        for col in self.inspector.get_columns(table_name, schema=self.schema):
            column_info = {
                "name": col["name"],
                "table": table_name,
                "type": str(col["type"]),
                "nullable": col["nullable"],
            }

            if self.metadata_config.retrieve_distinct_values:
                column_info["distinct_values"] = self._get_distinct_values(
                    table_name,
                    col["name"],
                    max_values=self.metadata_config.max_distinct_values,
                )

            column = ColumnMetadata(
                name=col["name"],
                table=table_name,
                data_type=str(col["type"]),
                nullable=col["nullable"],
                is_primary_key=False,
                is_foreign_key=False,
                distinct_values=column_info["distinct_values"],
            )
            columns.append(column)

        return columns

    @abstractmethod
    def _get_distinct_values(
        self, table_name: str, column_name: str, max_values: int
    ) -> List[str]:
        """
        Retrieves distinct values for a given column.

        Args:
            table_name: Name of the table
            column_name: Name of the column
            max_values: Maximum number of distinct values to retrieve

        Returns:
            List[str]: List of distinct values
        """
        pass
