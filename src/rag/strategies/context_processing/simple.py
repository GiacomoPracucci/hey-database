import logging
from typing import Dict, Any, List

from src.rag.models import RAGContext
from src.rag.strategies.strategies import ContextProcessingStrategy
from src.models.vector_store import (
    TableSearchResult,
    ColumnSearchResult,
    QuerySearchResult,
)

logger = logging.getLogger("hey-database")


class SimpleContextProcessor(ContextProcessingStrategy):
    """
    A basic context processing strategy that formats retrieved metadata into readable text.

    This strategy takes the retrieved tables, columns, and queries from the RAG context
    and formats them into a structured text representation that can be included in
    the prompt to the LLM.
    """

    def __init__(
        self,
        include_table_descriptions: bool = True,
        include_column_descriptions: bool = True,
        include_sample_queries: bool = True,
        max_tables: int = 5,
        max_columns: int = 10,
        max_queries: int = 2,
    ):
        """
        Initialize the context processor with formatting options.

        Args:
            include_table_descriptions: Whether to include table descriptions (default: True)
            include_column_descriptions: Whether to include column descriptions (default: True)
            include_sample_queries: Whether to include sample queries (default: True)
            max_tables: Maximum number of tables to include in context (default: 5)
            max_columns: Maximum number of columns to include in context (default: 10)
            max_queries: Maximum number of queries to include in context (default: 2)
        """
        self.include_table_descriptions = include_table_descriptions
        self.include_column_descriptions = include_column_descriptions
        self.include_sample_queries = include_sample_queries
        self.max_tables = max_tables
        self.max_columns = max_columns
        self.max_queries = max_queries

    def execute(self, context: RAGContext) -> RAGContext:
        """
        Process the retrieved context and format it for inclusion in the prompt.

        This method generates a formatted string representation of the retrieved
        tables, columns, and queries, and sets it as the processed_context in
        the RAG context.

        Args:
            context: The RAG context containing retrieved information

        Returns:
            The updated RAG context with processed_context set
        """
        logger.debug("Processing retrieved context")
        context.add_metadata("context_processing_strategy", "simple")

        tables_section = self._format_tables(
            context.retrieved_tables[: self.max_tables]
        )

        columns_section = self._format_columns(
            context.retrieved_columns[: self.max_columns]
        )

        queries_section = self._format_queries(
            context.retrieved_queries[: self.max_queries]
        )

        # Combine sections into processed context
        sections = []

        if tables_section:
            sections.append("RELEVANT TABLES:\n" + tables_section)

        if columns_section:
            sections.append("RELEVANT COLUMNS:\n" + columns_section)

        if queries_section:
            sections.append("SIMILAR QUERIES:\n" + queries_section)

        if sections:
            context.processed_context = "\n\n".join(sections)
            logger.debug("Context processing completed successfully")
        else:
            context.processed_context = "No relevant schema information found."
            logger.warning("No context was generated - no relevant information found")

        return context

    def _format_tables(self, tables: List[TableSearchResult]) -> str:
        """
        Format table information into a readable string.

        Args:
            tables: List of relevant tables

        Returns:
            Formatted string with table information
        """
        if not tables:
            return ""

        formatted_tables = []

        for table in tables:
            table_info = [f"Table: {table.name}"]

            # Add primary keys if available
            if table.primary_keys:
                primary_keys_str = ", ".join(table.primary_keys)
                table_info.append(f"Primary Keys: {primary_keys_str}")

            # Add description if enabled and available
            if self.include_table_descriptions and table.description:
                table_info.append(f"Description: {table.description}")

            # Add columns
            columns_str = ", ".join(table.columns)
            table_info.append(f"Columns: {columns_str}")

            formatted_tables.append("\n".join(table_info))

        return "\n\n".join(formatted_tables)

    def _format_columns(self, columns: List[ColumnSearchResult]) -> str:
        """
        Format column information into a readable string.

        Args:
            columns: List of relevant columns

        Returns:
            Formatted string with column information
        """
        if not columns:
            return ""

        formatted_columns = []

        for column in columns:
            column_info = [f"Column: {column.table}.{column.name}"]

            column_info.append(f"Type: {column.data_type}")

            # Add flags for primary/foreign keys
            flags = []
            if column.is_primary_key:
                flags.append("Primary Key")
            if column.is_foreign_key:
                flags.append("Foreign Key")
            if column.nullable:
                flags.append("Nullable")

            if flags:
                column_info.append(f"Attributes: {', '.join(flags)}")

            # Add description if enabled and available
            if self.include_column_descriptions and column.description:
                column_info.append(f"Description: {column.description}")

            formatted_columns.append("\n".join(column_info))

        return "\n\n".join(formatted_columns)

    def _format_queries(self, queries: List[QuerySearchResult]) -> str:
        """
        Format previous query information into a readable string.

        Args:
            queries: List of relevant previous queries

        Returns:
            Formatted string with query information
        """
        if not queries or not self.include_sample_queries:
            return ""

        formatted_queries = []

        for query in queries:
            query_info = [f"Question: {query.question}", f"SQL: {query.sql_query}"]

            # Add explanation if available
            if query.explanation:
                query_info.append(f"Explanation: {query.explanation}")

            formatted_queries.append("\n".join(query_info))

        return "\n\n".join(formatted_queries)

    @classmethod
    def from_config(
        cls, config: Dict[str, Any], **dependencies
    ) -> "SimpleContextProcessor":
        """
        Create a SimpleContextProcessor from a configuration dictionary.

        Args:
            config: Configuration dictionary with processor parameters
            **dependencies: Additional dependencies (not used by this strategy)

        Returns:
            An initialized SimpleContextProcessor
        """
        from src.rag.utils import get_config_value

        return cls(
            include_table_descriptions=get_config_value(
                config, "include_table_descriptions", True, value_type=bool
            ),
            include_column_descriptions=get_config_value(
                config, "include_column_descriptions", True, value_type=bool
            ),
            include_sample_queries=get_config_value(
                config, "include_sample_queries", True, value_type=bool
            ),
            max_tables=get_config_value(config, "max_tables", 5, value_type=int),
            max_columns=get_config_value(config, "max_columns", 10, value_type=int),
            max_queries=get_config_value(config, "max_queries", 2, value_type=int),
        )
