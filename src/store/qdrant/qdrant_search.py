from typing import List
from qdrant_client.http import models

from src.models.vector_store import (
    DocumentType,
    TableSearchResult,
    ColumnSearchResult,
    QuerySearchResult,
)
from src.store.qdrant.qdrant_client import QdrantStore
from src.store.vectorstore_search import StoreSearch

import logging

logger = logging.getLogger("hey-database")


class QdrantSearch(StoreSearch):
    """
    Qdrant-specific implementation of vector store search operations.

    This class provides methods for performing semantic searches against a Qdrant
    vector database, allowing retrieval of tables, columns, and queries that are
    semantically similar to a user's natural language question.

    Attributes:
        vector_store: Instance of QdrantStore for interacting with Qdrant
    """

    def __init__(self, vector_store: QdrantStore):
        """
        Initialize the Qdrant search component.

        Args:
            vector_store: Initialized QdrantStore instance for vectorstore operations
        """
        self.vector_store = vector_store

    def _search_points_by_type(
        self, vector: List[float], type_value: DocumentType, limit: int, extra_filters: List[models.Condition] = None
    ):
        """
        Search for points in Qdrant by document type and optional additional filters.

        Performs a vector search against the Qdrant database with filters
        to return only documents of the specified type and matching other conditions.

        Args:
            vector: Query vector for semantic search
            type_value: Type of documents to search for (table, column, query)
            limit: Maximum number of results to return
            extra_filters: Optional list of additional Qdrant filter conditions to apply.

        Returns:
            List of search results from Qdrant
        """
        # Base filter to search documents by type (table, column, query)
        must_conditions = [
            models.FieldCondition(
                key="type", match=models.MatchValue(value=str(type_value))
            )
        ]

        # Add any extra filters provided
        if extra_filters:
            must_conditions.extend(extra_filters)

        return self.vector_store.client.search(
            collection_name=self.vector_store.collection_name,
            query_vector=vector,
            query_filter=models.Filter(must=must_conditions),
            limit=limit,
        )

    def search_tables(self, question: str, limit: int = 3) -> List[TableSearchResult]:
        """
        Find tables that are semantically relevant to the user's question.

        Generates an embedding for the question and searches for similar
        table documents in the vector database.

        Args:
            question: User's natural language question
            limit: Maximum number of tables to return (default: 3)

        Returns:
            List of TableSearchResult containing relevant tables
        """
        try:
            vector = self.vector_store.embedding_model.encode(question)

            search_result = self._search_points_by_type(
                vector=vector, type_value=DocumentType.TABLE, limit=limit
            )
            logger.info(f"Table search results count: {len(search_result)}")
            return [self._convert_to_table_result(hit) for hit in search_result]

        except Exception as e:
            logger.error(f"Error searching for tables: {str(e)}")
            return []

    def _convert_to_table_result(self, hit) -> TableSearchResult:
        """
        Convert a Qdrant search hit to a TableSearchResult object.

        Maps the raw search result to the application's data model.

        Args:
            hit: Raw search result from Qdrant

        Returns:
            TableSearchResult with structured table metadata
        """
        return TableSearchResult(
            id=hit.id,
            similarity_score=hit.score,
            name=hit.payload.get("name"),
            columns=hit.payload.get("columns", []),
            primary_keys=hit.payload.get("primary_keys", []),
            foreign_keys=hit.payload.get("foreign_keys", []),
            row_count=hit.payload.get("row_count", 0),
            description=hit.payload.get("description", ""),
            keywords=hit.payload.get("keywords", []),
            importance_score=hit.payload.get("importance_score", 0.0),
        )

    def search_columns(self, question: str, limit: int = 5) -> List[ColumnSearchResult]:
        """
        Find columns that are semantically relevant to the user's question.

        Generates an embedding for the question and searches for similar
        column documents in the vector database.

        Args:
            question: User's natural language question
            limit: Maximum number of columns to return (default: 5)

        Returns:
            List of ColumnSearchResult containing relevant columns
        """
        try:
            vector = self.vector_store.embedding_model.encode(question)
            search_result = self._search_points_by_type(
                vector=vector, type_value=DocumentType.COLUMN, limit=limit
            )
            logger.info(f"Column search results count: {len(search_result)}")
            return [self._convert_to_column_result(hit) for hit in search_result]

        except Exception as e:
            logger.error(f"Error searching for columns: {str(e)}")
            return []
        
    def search_relevant_columns_in_table(
        self, question: str, table_name: str, limit: int = 5
    ) -> List[ColumnSearchResult]:
        """
        Find columns within a specific table that are semantically relevant to the user's question.

        Generates an embedding for the question and searches for similar column
        documents in the vector database, filtered to only include columns
        belonging to the specified table. This implements the idea of first
        finding relevant tables and then finding the most relevant columns *within*
        those tables based on the original question.

        Args:
            question: User's natural language question.
            table_name: The name of the specific table to search within.
            limit: Maximum number of relevant columns to return from the specified table (default: 5).

        Returns:
            List of ColumnSearchResult containing relevant columns from the specified table,
            ordered by relevance to the question. Returns an empty list if an error occurs
            or no relevant columns are found.
        """
        try:
            vector = self.vector_store.embedding_model.encode(question)

            # Filter condition to match the specific table name
            table_filter = models.FieldCondition(
                key="table",
                match=models.MatchValue(value=table_name),
            )

            # Perform the search with both type and table filters
            search_result = self._search_points_by_type(
                vector=vector,
                type_value=DocumentType.COLUMN,
                limit=limit,
                extra_filters=[table_filter], # Pass the table name filter
            )

            logger.info(
                f"Column search results count for table '{table_name}': {len(search_result)}"
            )

            return [self._convert_to_column_result(hit) for hit in search_result]

        except Exception as e:
            logger.error(
                f"Error searching for columns in table '{table_name}': {str(e)}",
                exc_info=True # Log traceback for better debugging
            )
            return []

    def _convert_to_column_result(self, hit) -> ColumnSearchResult:
        """
        Convert a Qdrant search hit to a ColumnSearchResult object.

        Maps the raw search result to the application's data model.

        Args:
            hit: Raw search result from Qdrant

        Returns:
            ColumnSearchResult with structured column metadata
        """
        return ColumnSearchResult(
            id=hit.id,
            similarity_score=hit.score,
            name=hit.payload.get("name"),
            table=hit.payload.get("table"),
            data_type=hit.payload.get("data_type", "unknown"),
            nullable=hit.payload.get("nullable", False),
            is_primary_key=hit.payload.get("is_primary_key", False),
            is_foreign_key=hit.payload.get("is_foreign_key", False),
            relationships=hit.payload.get("relationships", []),
            ai_name=hit.payload.get("ai_name", ""),
            description=hit.payload.get("description", ""),
            keywords=hit.payload.get("keywords", []),
        )

    def search_queries(self, question: str, limit: int = 3) -> List[QuerySearchResult]:
        """
        Find previously asked queries that are semantically similar to the user's question.

        Searches for previously stored queries that might answer the current question,
        potentially saving the need to generate a new SQL query.

        Args:
            question: User's natural language question
            limit: Maximum number of queries to return (default: 3)

        Returns:
            List of QuerySearchResult containing relevant queries
        """
        try:
            vector = self.vector_store.embedding_model.encode(question)
            search_result = self._search_points_by_type(
                vector=vector, type_value=DocumentType.QUERY, limit=limit
            )
            logger.info(f"Query search results count: {len(search_result)}")
            return [self._convert_to_query_result(hit) for hit in search_result]

        except Exception as e:
            logger.error(f"Error searching for queries: {str(e)}")
            return []

    def _convert_to_query_result(self, hit) -> QuerySearchResult:
        """
        Convert a Qdrant search hit to a QuerySearchResult object.

        Maps the raw search result to the application's data model.

        Args:
            hit: Raw search result from Qdrant

        Returns:
            QuerySearchResult with query details and score
        """
        return QuerySearchResult(
            id=hit.id,
            similarity_score=hit.score,
            question=hit.payload.get("question"),
            sql_query=hit.payload.get("sql_query"),
            explanation=hit.payload.get("explanation"),
            positive_votes=hit.payload.get("positive_votes", 0),
        )
