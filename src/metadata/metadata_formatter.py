from typing import Dict, Any, List, Tuple
from datetime import datetime

from src.models.metadata import (
    MetadataState,
    EnhancedTableMetadata,
    EnhancedColumnMetadata,
)
from src.models.vector_store import TablePayload
from src.models.metadata import TableMetadata, ColumnMetadata

import logging

logger = logging.getLogger("hey-database")


class MetadataFormatter:
    """
    Utility class responsible for transforming metadata between different formats.
    Provides methods to format metadata for different use cases:
    - Nested format for schema visualization and backwards compatibility
    - Cache format for storage
    - Vector store format for semantic search
    """

    @staticmethod
    def to_nested_format(state: MetadataState) -> Dict[str, Dict[str, Any]]:
        """
        Converts flat metadata state to nested format where column metadata
        is nested inside their respective tables. Used for schema visualization
        and backwards compatibility.

        Args:
            state: Current metadata state with separate table and column metadata

        Returns:
            Dict with tables as keys and nested metadata (including columns) as values
        """
        nested_tables = {}

        for table_name, table in state.tables.items():
            # Create nested table structure
            nested_table = {
                "name": table.base_metadata.name,
                "description": table.description,
                "keywords": table.keywords,
                "importance_score": table.importance_score,
                "primary_keys": table.base_metadata.primary_keys,
                "foreign_keys": table.base_metadata.foreign_keys,
                "row_count": table.base_metadata.row_count,
                "columns": {},
            }

            # Add column metadata if available for this table
            if table_name in state.columns:
                nested_table["columns"] = {
                    col_name: {
                        "name": col.base_metadata.name,
                        "description": col.description,
                        "data_type": col.base_metadata.data_type,
                        "nullable": col.base_metadata.nullable,
                        "is_primary_key": col.base_metadata.is_primary_key,
                        "is_foreign_key": col.base_metadata.is_foreign_key,
                        "keywords": col.keywords,
                        "ai_name": col.ai_name,
                        "distinct_values": col.base_metadata.distinct_values,
                    }
                    for col_name, col in state.columns[table_name].items()
                }

            nested_tables[table_name] = nested_table

        return nested_tables

    @staticmethod
    def to_cache_format(state: MetadataState) -> Dict[str, Any]:
        """
        Prepares metadata for cache storage. The cache format maintains
        the separation between tables and columns but serializes all
        dataclass instances to plain dictionaries.

        Args:
            state: Current metadata state

        Returns:
            Dict containing serialized tables, columns and last update timestamp
        """
        # Serialize table metadata
        tables_dict = {}
        for table_name, table in state.tables.items():
            tables_dict[table_name] = {
                "base_metadata": {
                    "name": table.base_metadata.name,
                    "columns": table.base_metadata.columns,
                    "primary_keys": table.base_metadata.primary_keys,
                    "foreign_keys": table.base_metadata.foreign_keys,
                    "row_count": table.base_metadata.row_count,
                },
                "description": table.description,
                "keywords": table.keywords,
                "importance_score": table.importance_score,
            }

        # Serialize column metadata
        columns_dict = {}
        for table_name, columns in state.columns.items():
            columns_dict[table_name] = {}
            for col_name, col in columns.items():
                columns_dict[table_name][col_name] = {
                    "base_metadata": {
                        "name": col.base_metadata.name,
                        "table": col.base_metadata.table,
                        "data_type": col.base_metadata.data_type,
                        "nullable": col.base_metadata.nullable,
                        "is_primary_key": col.base_metadata.is_primary_key,
                        "is_foreign_key": col.base_metadata.is_foreign_key,
                        "distinct_values": col.base_metadata.distinct_values,
                        "relationships": col.base_metadata.relationships,
                    },
                    "ai_name": col.ai_name,
                    "description": col.description,
                    "keywords": col.keywords,
                }

        return {
            "tables": tables_dict,
            "columns": columns_dict,
            "last_update": state.last_update.isoformat(),
        }

    @staticmethod
    def from_cache_format(cache_data: Dict[str, Any]) -> MetadataState:
        """
        Reconstructs MetadataState from cached data.

        Args:
            cache_data: Dictionary containing cached metadata

        Returns:
            Reconstructed MetadataState object
        """
        # Reconstruct table metadata
        tables = {}
        for table_name, table_data in cache_data["tables"].items():
            base_data = table_data["base_metadata"]
            tables[table_name] = EnhancedTableMetadata(
                base_metadata=TableMetadata(
                    name=base_data["name"],
                    columns=base_data["columns"],
                    primary_keys=base_data["primary_keys"],
                    foreign_keys=base_data["foreign_keys"],
                    row_count=base_data["row_count"],
                ),
                description=table_data["description"],
                keywords=table_data["keywords"],
                importance_score=table_data["importance_score"],
            )

        # Reconstruct column metadata
        columns = {}
        for table_name, table_columns in cache_data["columns"].items():
            columns[table_name] = {}
            for col_name, col_data in table_columns.items():
                base_data = col_data["base_metadata"]
                columns[table_name][col_name] = EnhancedColumnMetadata(
                    base_metadata=ColumnMetadata(
                        name=base_data["name"],
                        table=base_data["table"],
                        data_type=base_data["data_type"],
                        nullable=base_data["nullable"],
                        is_primary_key=base_data["is_primary_key"],
                        is_foreign_key=base_data["is_foreign_key"],
                        distinct_values=base_data["distinct_values"],
                        relationships=base_data["relationships"],
                    ),
                    ai_name=col_data["ai_name"],
                    description=col_data["description"],
                    keywords=col_data["keywords"],
                )

        return MetadataState(
            tables=tables,
            columns=columns,
            last_update=datetime.fromisoformat(cache_data["last_update"]),
        )

    @staticmethod
    def to_vector_store_format(
        state: MetadataState,
    ) -> Tuple[List[TablePayload], List[Dict[str, Any]]]:
        """
        Prepares metadata for vector store population.
        Creates separate payloads for tables and columns to avoid redundancy.

        Args:
            state: Current metadata state

        Returns:
            Tuple containing:
            - List of TablePayload objects for tables
            - List of column metadata dictionaries
        """
        # Prepare table payloads
        table_payloads = []
        for table_name, table in state.tables.items():
            payload = TablePayload(
                type="table",
                table_name=table.base_metadata.name,
                description=table.description,
                keywords=table.keywords,
                # Only include minimal column information needed for queries
                columns=[{"name": col} for col in table.base_metadata.columns],
                primary_keys=table.base_metadata.primary_keys,
                foreign_keys=table.base_metadata.foreign_keys,
                row_count=table.base_metadata.row_count,
                importance_score=table.importance_score,
            )
            table_payloads.append(payload)

        # Prepare column payloads
        column_payloads = []
        for table_name, columns in state.columns.items():
            for col_name, col in columns.items():
                payload = {
                    "type": "column",
                    "table_name": table_name,
                    "column_name": col_name,
                    "description": col.description,
                    "keywords": col.keywords,
                    "data_type": col.base_metadata.data_type,
                    "is_primary_key": col.base_metadata.is_primary_key,
                    "is_foreign_key": col.base_metadata.is_foreign_key,
                    "ai_name": col.ai_name,
                }
                column_payloads.append(payload)

        return table_payloads, column_payloads
