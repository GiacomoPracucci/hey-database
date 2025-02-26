from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime


@dataclass
class MetadataConfig:
    """
    Configuration for metadata retrieval and processing.

    This class defines configuration parameters that control how metadata is
    extracted and processed from the database.

    Attributes:
        retrieve_distinct_values: Whether to extract distinct values for columns
        max_distinct_values: Maximum number of distinct values to retrieve per column
    """

    retrieve_distinct_values: bool = True
    max_distinct_values: int = 100


@dataclass
class BaseTableMetadata:
    """
    Base metadata inferred from database schema.

    Contains fundamental information about a database table retrieved directly
    from the database schema, without any AI enhancements.

    Attributes:
        name: Table name
        columns: List of column names in the table
        primary_keys: List of primary key columns
        foreign_keys: List of foreign key relationships
        row_count: Number of rows in the table
    """

    name: str
    columns: List[str]
    primary_keys: List[str]
    foreign_keys: List[Dict[str, str]]
    row_count: int


@dataclass
class TableMetadata:
    """
    Complete table metadata including both base schema information and AI-enhanced data.

    This class combines all metadata about a database table in a flat structure
    for easier access and manipulation.

    Attributes:
        name: Table name
        columns: List of column names in the table
        primary_keys: List of primary key columns
        foreign_keys: List of foreign key relationships
        row_count: Number of rows in the table
        description: AI-generated description
        keywords: Extracted keywords for semantic search
        importance_score: Calculated importance score
        type: Document type identifier for vector store (default: "table")
    """

    # Base metadata fields
    name: str
    columns: List[str]
    primary_keys: List[str]
    foreign_keys: List[Dict[str, str]]
    row_count: int

    # Enhanced metadata fields
    description: str
    keywords: List[str]
    importance_score: float
    type: str = "table"

    @classmethod
    def from_dict(cls, data: Dict) -> "TableMetadata":
        """
        Creates a TableMetadata instance from a dictionary.

        This method is used when loading serialized metadata from cache.

        Args:
            data: Dictionary containing the serialized metadata

        Returns:
            TableMetadata instance populated with the deserialized data
        """
        return cls(
            # Base metadata fields
            name=data["name"],
            columns=data["columns"],
            primary_keys=data["primary_keys"],
            foreign_keys=data["foreign_keys"],
            row_count=data["row_count"],
            # Enhanced metadata fields
            description=data["description"],
            keywords=data["keywords"],
            importance_score=data["importance_score"],
            type=data.get("type", "table"),  # Support legacy data without type field
        )

    @classmethod
    def from_base_metadata(
        cls,
        base: BaseTableMetadata,
        description: str,
        keywords: List[str],
        importance_score: float,
    ) -> "TableMetadata":
        """
        Creates a TableMetadata instance from a BaseTableMetadata and enhanced fields.

        This factory method simplifies the transition from base metadata to complete metadata.

        Args:
            base: Base table metadata extracted from database schema
            description: AI-generated description
            keywords: Extracted keywords for semantic search
            importance_score: Calculated importance score

        Returns:
            TableMetadata instance with fields from both sources
        """
        return cls(
            name=base.name,
            columns=base.columns,
            primary_keys=base.primary_keys,
            foreign_keys=base.foreign_keys,
            row_count=base.row_count,
            description=description,
            keywords=keywords,
            importance_score=importance_score,
        )


@dataclass
class TableRelationship:
    """
    Represents a relationship (incoming or outgoing) between two tables.

    Contains information about how tables are related through foreign keys,
    including the direction of the relationship and the columns involved.

    Attributes:
        related_table: Name of the related table
        direction: Relationship direction ("incoming" or "outgoing")
        local_columns: Columns in the current table involved in the relationship
        remote_columns: Columns in the related table involved in the relationship
    """

    related_table: str
    direction: str
    local_columns: List[str]
    remote_columns: List[str]


@dataclass
class BaseColumnMetadata:
    """
    Base metadata for a database column.

    Contains fundamental information about a database column retrieved directly
    from the database schema, without any AI enhancements.

    Attributes:
        name: Column name
        table: Name of the table containing this column
        data_type: Database data type of the column
        nullable: Whether the column can contain NULL values
        is_primary_key: Whether the column is part of a primary key
        is_foreign_key: Whether the column is part of a foreign key
        distinct_values: Sample of distinct values in the column
        relationships: Foreign key relationships involving this column
    """

    name: str
    table: str
    data_type: str
    nullable: bool
    is_primary_key: bool
    is_foreign_key: bool
    distinct_values: List[str] = field(default_factory=list)
    relationships: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class ColumnMetadata:
    """
    Complete column metadata including both base schema information and AI-enhanced data.

    This class combines all metadata about a database column in a flat structure
    for easier access and manipulation.

    Attributes:
        name: Column name
        table: Name of the table containing this column
        data_type: Database data type of the column
        nullable: Whether the column can contain NULL values
        is_primary_key: Whether the column is part of a primary key
        is_foreign_key: Whether the column is part of a foreign key
        distinct_values: Sample of distinct values in the column
        relationships: Foreign key relationships involving this column
        ai_name: AI-generated alternative name for improved readability
        description: AI-generated description of the column's purpose
        keywords: Extracted keywords for semantic search
        type: Document type identifier for vector store (default: "column")
    """

    # Base metadata fields
    name: str
    table: str
    data_type: str
    nullable: bool
    is_primary_key: bool
    is_foreign_key: bool
    distinct_values: List[str] = field(default_factory=list)
    relationships: List[Dict[str, str]] = field(default_factory=list)

    # Enhanced metadata fields
    ai_name: str
    description: str
    keywords: List[str]
    type: str = "column"

    @classmethod
    def from_dict(cls, data: Dict) -> "ColumnMetadata":
        """
        Creates a ColumnMetadata instance from a dictionary.

        This method is used when loading serialized metadata from cache.

        Args:
            data: Dictionary containing the serialized metadata

        Returns:
            ColumnMetadata instance populated with the deserialized data
        """
        return cls(
            # Base metadata fields
            name=data["name"],
            table=data["table"],
            data_type=data["data_type"],
            nullable=data["nullable"],
            is_primary_key=data["is_primary_key"],
            is_foreign_key=data["is_foreign_key"],
            distinct_values=data["distinct_values"],
            relationships=[],  # Relationships are not serialized in the cache
            # Enhanced metadata fields
            ai_name=data["ai_name"],
            description=data["description"],
            keywords=data["keywords"],
            type=data.get("type", "column"),  # Support legacy data without type field
        )

    @classmethod
    def from_base_metadata(
        cls,
        base: BaseColumnMetadata,
        ai_name: str,
        description: str,
        keywords: List[str],
    ) -> "ColumnMetadata":
        """
        Creates a ColumnMetadata instance from a BaseColumnMetadata and enhanced fields.

        This factory method simplifies the transition from base metadata to complete metadata.

        Args:
            base: Base column metadata extracted from database schema
            ai_name: AI-generated alternative name for the column
            description: AI-generated description
            keywords: Extracted keywords for semantic search

        Returns:
            ColumnMetadata instance with fields from both sources
        """
        return cls(
            name=base.name,
            table=base.table,
            data_type=base.data_type,
            nullable=base.nullable,
            is_primary_key=base.is_primary_key,
            is_foreign_key=base.is_foreign_key,
            distinct_values=base.distinct_values,
            relationships=base.relationships,
            ai_name=ai_name,
            description=description,
            keywords=keywords,
        )


@dataclass
class QueryMetadata:
    """
    Metadata for stored SQL queries and their natural language questions.

    Contains information about user questions, their SQL translations, and
    other metadata useful for vector storage and retrieval.

    Attributes:
        question: Natural language question asked by the user
        sql_query: SQL query that answers the question
        explanation: Explanation of how the SQL query works
        positive_votes: Number of positive user feedback received
        timestamp: When the query was first created or last updated
        type: Document type identifier for vector store (default: "query")
    """

    question: str
    sql_query: str
    explanation: str
    positive_votes: int = 0
    type: str = "query"

    @classmethod
    def from_dict(cls, data: Dict) -> "QueryMetadata":
        """
        Creates a QueryMetadata instance from a dictionary.

        This method is used when loading serialized metadata from cache.

        Args:
            data: Dictionary containing the serialized metadata

        Returns:
            QueryMetadata instance populated with the deserialized data
        """
        return cls(
            question=data["question"],
            sql_query=data["sql_query"],
            explanation=data["explanation"],
            positive_votes=data.get("positive_votes", 0),
            timestamp=datetime.fromisoformat(data["timestamp"])
            if "timestamp" in data
            else datetime.now(),
            type=data.get("type", "query"),  # Support legacy data without type field
        )


@dataclass
class Metadata:
    """
    Represents the current state of database metadata.

    Acts as an immutable container for all metadata information, including
    tables, columns, and queries. This class is the central data structure
    used throughout the application for metadata operations.

    Attributes:
        tables: Dictionary mapping table names to their enhanced metadata
        columns: Nested dictionary mapping table names to column names to metadata
        queries: Dictionary mapping question text to query metadata
    """

    tables: Dict[str, TableMetadata]
    columns: Dict[str, Dict[str, ColumnMetadata]]
    queries: Dict[str, QueryMetadata] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict) -> "Metadata":
        """
        Builds a Metadata object from a dictionary.

        This method is used when metadata is loaded from the cache.

        Args:
            data: Dictionary containing the serialized metadata structure

        Returns:
            Metadata instance populated with the deserialized data
        """
        tables = {
            name: TableMetadata.from_dict(table_data)
            for name, table_data in data["tables"].items()
        }

        columns = {
            table_name: {
                col_name: ColumnMetadata.from_dict(col_data)
                for col_name, col_data in table_cols.items()
            }
            for table_name, table_cols in data["columns"].items()
        }

        queries = {}
        if "queries" in data:
            queries = {
                query_data["question"]: QueryMetadata.from_dict(query_data)
                for query_data in data["queries"].values()
            }

        return cls(tables=tables, columns=columns, queries=queries)
