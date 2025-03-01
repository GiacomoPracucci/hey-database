import logging
from typing import Dict, Any, Optional

from src.rag.models import RAGContext
from src.rag.strategies import RetrievalStrategy
from src.store.vectorstore_search import StoreSearch

logger = logging.getLogger("hey-database")


class CosineSimRetrievalStrategy(RetrievalStrategy):
    """
    A retrieval strategy that uses cosine similarity to find relevant information.

    This strategy queries the vector store to find tables, columns, and previous queries
    that are semantically similar to the input query, using cosine similarity as the
    measure of relevance.
    """

    def __init__(
        self,
        vector_store_search: StoreSearch,
        tables_limit: int = 3,
        columns_limit: int = 5,
        queries_limit: int = 3,
        use_exact_match: bool = True,
    ):
        """
        Initialize the retrieval strategy.

        Args:
            vector_store_search: Component for searching the vector store
            tables_limit: Maximum number of tables to retrieve (default: 3)
            columns_limit: Maximum number of columns to retrieve (default: 5)
            queries_limit: Maximum number of previous queries to retrieve (default: 3)
            use_exact_match: Whether to check for exact matches in query store (default: True)
        """
        self.vector_store_search = vector_store_search
        self.tables_limit = tables_limit
        self.columns_limit = columns_limit
        self.queries_limit = queries_limit
        self.use_exact_match = use_exact_match

    def execute(self, context: RAGContext) -> RAGContext:
        """
        Execute the retrieval strategy on the current context.

        This method queries the vector store for tables, columns, and previous queries
        that are relevant to the processed query, and adds them to the context.

        Args:
            context: The RAG context containing the processed query

        Returns:
            The updated RAG context with retrieved information
        """
        # Use the processed query if available, otherwise use the original query
        query = context.processed_query or context.original_query

        # Add metadata to track the retrieval process
        context.add_metadata("retrieval_strategy", "cosine_similarity")
        context.add_metadata("tables_limit", self.tables_limit)
        context.add_metadata("columns_limit", self.columns_limit)
        context.add_metadata("queries_limit", self.queries_limit)

        try:
            # Check for exact match in previous queries if enabled
            exact_match = None
            if self.use_exact_match and hasattr(
                self.vector_store_search, "find_exact_match"
            ):
                logger.debug(f"Checking for exact match for query: {query}")
                exact_match = self.vector_store_search.find_exact_match(query)
                if exact_match:
                    logger.info(f"Found exact match for query: {query}")
                    context.add_metadata("exact_match_found", True)
                    context.retrieved_queries = [exact_match]
                    return context

            # If no exact match or exact matching is disabled, perform semantic search
            logger.debug(f"Retrieving relevant tables for query: {query}")
            context.retrieved_tables = self.vector_store_search.search_tables(
                question=query, limit=self.tables_limit
            )
            context.add_metadata("tables_retrieved", len(context.retrieved_tables))

            logger.debug(f"Retrieving relevant columns for query: {query}")
            context.retrieved_columns = self.vector_store_search.search_columns(
                question=query, limit=self.columns_limit
            )
            context.add_metadata("columns_retrieved", len(context.retrieved_columns))

            logger.debug(f"Retrieving relevant queries for query: {query}")
            context.retrieved_queries = self.vector_store_search.search_queries(
                question=query, limit=self.queries_limit
            )
            context.add_metadata("queries_retrieved", len(context.retrieved_queries))

            return context

        except Exception as e:
            logger.exception(f"Error during retrieval: {str(e)}")
            context.add_metadata("retrieval_error", str(e))
            # Return the context even if retrieval fails, to allow the pipeline to continue
            return context

    @classmethod
    def from_config(
        cls, config: Dict[str, Any], vector_store_search: Optional[StoreSearch] = None
    ) -> "CosineSimRetrievalStrategy":
        """
        Create a CosineSimRetrievalStrategy from a configuration dictionary.

        Args:
            config: Configuration dictionary with strategy parameters
            vector_store_search: Vector store search component (required if not in config)

        Returns:
            An initialized CosineSimRetrievalStrategy

        Raises:
            ValueError: If required parameters are missing or invalid
        """
        if vector_store_search is None and "vector_store_search" not in config:
            raise ValueError("Vector store search component is required")

        return cls(
            vector_store_search=vector_store_search or config["vector_store_search"],
            tables_limit=config.get("tables_limit", 3),
            columns_limit=config.get("columns_limit", 5),
            queries_limit=config.get("queries_limit", 3),
            use_exact_match=config.get("use_exact_match", True),
        )
