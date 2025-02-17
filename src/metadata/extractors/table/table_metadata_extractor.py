from src.models.metadata import BaseTableMetadata
from typing import List, Any, Dict
from abc import ABC, abstractmethod

from src.connectors.connector import DatabaseConnector
from sqlalchemy import inspect, text
from sqlalchemy.engine import Inspector

import logging

logger = logging.getLogger("hey-database")


class TableMetadataExtractor(ABC):
    """Abstract base class for extracting table metadata from database tables"""

    def __init__(self, db: DatabaseConnector, schema: str):
        self.engine = db.engine
        self.inspector: Inspector = inspect(db.engine)
        self.schema = schema

    def get_tables(self) -> List[str]:
        """
        Get list of tables in the schema.

        Returns:
            List[str]: List of table names in the schema
        """
        try:
            return self.inspector.get_table_names(schema=self.schema)
        except Exception as e:
            logger.error(f"Error getting tables for schema {self.schema}: {str(e)}")
            return []

    def extract_metadata(self, table_name: str) -> BaseTableMetadata:
        """
        Extracts base metadata for a table.

        Args:
            table_name: Name of the table

        Returns:
            TableMetadata: Base metadata of the table
        """

        # 1. Extract column information
        columns = self._get_columns(table_name)

        # 2. Extract primary key information
        primary_keys = self._get_primary_keys(table_name)

        # 3. Extract foreign key information
        foreign_keys = self._get_foreign_keys_relationships(table_name)

        # 4. Get table row count
        row_count = self._get_row_count(table_name)

        return BaseTableMetadata(
            name=table_name,
            columns=columns,
            primary_keys=primary_keys,
            foreign_keys=foreign_keys,
            row_count=row_count,
        )

    def _get_columns(self, table_name: str) -> List[str]:
        """
        Retrieves the list of columns for a table.

        Args:
            table_name: Name of the table

        Returns:
            List[str]: List of column names
        """
        columns = []
        for col in self.inspector.get_columns(table_name, schema=self.schema):
            columns.append(col["name"])
        return columns

    def _get_primary_keys(self, table_name: str) -> List[str]:
        """
        Retrieves primary keys for a table

        Args:
            table_name: Name of the table

        Returns:
            List[str]: List of primary key column names
        """
        pk_info = self.inspector.get_pk_constraint(table_name, schema=self.schema)
        return pk_info["constrained_columns"] if pk_info else []

    def _get_foreign_keys_relationships(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Retrieves foreign key metadata for a table

        Args:
            table_name: Name of the table

        Returns:
            List[Dict[str, Any]]: List of foreign key relationships
        """
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
        """Retrieves the row count for a table (database-specific implementation)"""
        pass

    def get_sample_data(self, table_name: str, max_rows: int = 3) -> List[Dict]:
        """Retrieves sample data from a table

        Args:
            table_name: Name of the table
            max_rows: Maximum number of rows to retrieve (default: 3)

        Returns:
            List[Dict]: List of sample rows as dictionaries
        """
        try:
            with self.engine.connect() as connection:
                query = text(
                    f"SELECT * FROM {self.schema}.{table_name} LIMIT {max_rows}"
                )
                result = connection.execute(query)

                columns = result.keys()
                return [dict(zip(columns, row)) for row in result]

        except Exception as e:
            logger.error(f"Error retrieving sample data for {table_name}: {str(e)}")
            return []
