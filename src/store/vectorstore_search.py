from abc import ABC, abstractmethod
from typing import List, TypeVar

from src.models.vector_store import (
    TableSearchResult,
    ColumnSearchResult,
    QuerySearchResult,
)

from src.models.metadata import TableMetadata, ColumnMetadata

# Generic type for search results
T = TypeVar("T")


class StoreSearch(ABC):
    """
    Abstract base class defining the interface for vector store search operations.
    This class provides methods for searching and retrieving similar items
    (tables, columns, queries) from a vector database.
    """

    @abstractmethod
    def _search_points_by_type(
        self, vector: List[float], type_value: str, limit: int
    ) -> List[T]:
        """
        Abstract method to search points in the vector store by their type.

        Args:
            vector: The query vector to search against
            type_value: The type of points to search for (table, column, query)
            limit: Maximum number of results to return

        Returns:
            List of search results specific to the vector store implementation
        """
        pass

    @abstractmethod
    def search_tables(self, question: str, limit: int = 3) -> List[TableSearchResult]:
        """
        Search for tables that are semantically similar to the input question.

        Args:
            question: The user's question or search query
            limit: Maximum number of results to return (default: 3)

        Returns:
            List of TableSearchResult containing similar tables and their metadata
        """
        pass

    @abstractmethod
    def search_columns(self, question: str, limit: int = 5) -> List[ColumnSearchResult]:
        """
        Search for columns that are semantically similar to the input question.

        Args:
            question: The user's question or search query
            limit: Maximum number of results to return (default: 5)

        Returns:
            List of ColumnSearchResult containing similar columns and their metadata
        """
        pass

    @abstractmethod
    def search_queries(self, question: str, limit: int = 3) -> List[QuerySearchResult]:
        """
        Search for previously asked queries that are semantically similar to the input question.

        Args:
            question: The user's question or search query
            limit: Maximum number of results to return (default: 3)

        Returns:
            List of QuerySearchResult containing similar queries and their metadata
        """
        pass

    @staticmethod
    def _convert_to_table_result(hit) -> TableSearchResult:
        """
        Convert a raw search hit to a TableSearchResult object.

        Args:
            hit: Raw search result from the vector store

        Returns:
            TableSearchResult object containing formatted table metadata
        """
        return TableSearchResult(
            id=hit.id,
            table_name=hit.payload["table_name"],
            metadata=TableMetadata(**hit.payload),
            relevance_score=hit.score,
        )

    @staticmethod
    def _convert_to_column_result(hit) -> ColumnSearchResult:
        """
        Convert a raw search hit to a ColumnSearchResult object.

        Args:
            hit: Raw search result from the vector store

        Returns:
            ColumnSearchResult object containing formatted column metadata
        """
        return ColumnSearchResult(
            id=hit.id,
            column_name=hit.payload["column_name"],
            column_name_alias=hit.payload["column_name_alias"],
            table_name=hit.payload["table_name"],
            metadata=ColumnMetadata(**hit.payload),
            relevance_score=hit.score,
        )

    @staticmethod
    def _convert_to_query_result(hit) -> QuerySearchResult:
        """
        Convert a raw search hit to a QuerySearchResult object.

        Args:
            hit: Raw search result from the vector store

        Returns:
            QuerySearchResult object containing formatted query metadata
        """
        return QuerySearchResult(
            id=hit.id,
            question=hit.payload["question"],
            sql_query=hit.payload["sql_query"],
            explanation=hit.payload["explanation"],
            score=hit.score,
            positive_votes=hit.payload["positive_votes"],
        )
