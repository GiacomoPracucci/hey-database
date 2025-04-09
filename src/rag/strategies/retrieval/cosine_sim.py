import logging
from typing import Dict, Any, List

from src.rag.models import RAGContext
from src.rag.strategies.strategies import RetrievalStrategy
from src.store.vectorstore_search import StoreSearch

from src.models.vector_store import (
    ColumnSearchResult,
)

logger = logging.getLogger("hey-database")


class CosineSimRetrieval(RetrievalStrategy):
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
            # --- Step 1: Retrieve Relevant Tables ---
            logger.debug(f"Retrieving relevant tables for query: {query}")
            context.retrieved_tables = self.vector_store_search.search_tables(
                question=query, limit=self.tables_limit
            )
            context.add_metadata("tables_retrieved", len(context.retrieved_tables))
            logger.info(f"Retrieved {len(context.retrieved_tables)} relevant tables.")

            # --- Step 2: Retrieve Relevant Columns PER TABLE ---
            all_relevant_columns: List[ColumnSearchResult] = [] 
            if context.retrieved_tables:
                logger.debug(f"Retrieving top 5 relevant columns for each retrieved table...")
                for table_result in context.retrieved_tables:
                    if table_result and table_result.name:
                        logger.debug(f"Searching columns in table '{table_result.name}' relevant to query: {query}")
                        columns_for_this_table = self.vector_store_search.search_relevant_columns_in_table(
                            question=query,
                            table_name=table_result.name,
                            limit=5
                        )
                        logger.debug(f"Found {len(columns_for_this_table)} relevant columns in table '{table_result.name}'.")
                        all_relevant_columns.extend(columns_for_this_table)
                    else:
                        logger.warning("Skipping column search for a table_result with missing name.")
            
            context.retrieved_columns = all_relevant_columns
            context.add_metadata("columns_retrieved", len(context.retrieved_columns))
            logger.info(f"Retrieved a total of {len(context.retrieved_columns)} relevant columns across all relevant tables.")
            
            # --- Step 3: Retrieve Relevant Queries ---
            logger.debug(f"Retrieving relevant queries for query: {query}")
            context.retrieved_queries = self.vector_store_search.search_queries(
                question=query, limit=self.queries_limit
            )
            context.add_metadata("queries_retrieved", len(context.retrieved_queries))
            logger.info(f"Retrieved {len(context.retrieved_queries)} similar queries.")

            return context

        except Exception as e:
            logger.exception(f"Error during retrieval: {str(e)}")
            context.add_metadata("retrieval_error", str(e))
            # Return the context even if retrieval fails, to allow the pipeline to continue
            return context

    @classmethod
    def from_config(
        cls, config: Dict[str, Any], **dependencies
    ) -> "CosineSimRetrieval":
        """
        Create a CosineSimRetrievalStrategy from a configuration dictionary.

        Args:
            config: Configuration dictionary with strategy parameters
            **dependencies: Additional dependencies, must include vector_store_search

        Returns:
            An initialized CosineSimRetrievalStrategy

        Raises:
            ValueError: If required parameters are missing or invalid
        """
        from src.rag.utils import get_config_value

        # Check for required dependencies
        vector_store_search = dependencies.get("vector_store_search")
        if vector_store_search is None:
            raise ValueError(
                "vector_store_search dependency is required for CosineSimRetrievalStrategy"
            )

        # Parse configuration with defaults
        tables_limit = get_config_value(config, "tables_limit", 3, value_type=int)
        columns_limit = get_config_value(config, "columns_limit", 5, value_type=int)
        queries_limit = get_config_value(config, "queries_limit", 3, value_type=int)
        use_exact_match = get_config_value(
            config, "use_exact_match", True, value_type=bool
        )

        return cls(
            vector_store_search=vector_store_search,
            tables_limit=tables_limit,
            columns_limit=columns_limit,
            queries_limit=queries_limit,
            use_exact_match=use_exact_match,
        )
