import logging
from typing import Dict, Any, Optional, List

import concurrent.futures
import os

from src.rag.models import RAGContext
from src.rag.strategies.strategies import RetrievalStrategy
from src.store.vectorstore_search import StoreSearch

from src.models.vector_store import (
    ColumnSearchResult,
    QuerySearchResult,
    TableSearchResult,
)

logger = logging.getLogger("hey-database")


class CosineSimRetrieval(RetrievalStrategy):
    """
    Implements a multi-step retrieval strategy using semantic similarity (cosine similarity).

    This strategy aims to gather relevant context for a given user query by interacting
    with a vector store (`StoreSearch`) in a specific sequence:

    1.  **Exact Match Check (Optional):** If `use_exact_match` is enabled, it first
        attempts to find a previously stored query that exactly matches the input query.
        If found, the strategy retrieves this query and potentially its associated context
        (in the current implementation, it retrieves only the query) and terminates early,
        assuming the exact match is the best possible context.

    2.  **Table Retrieval:** If no exact match is found or the check is disabled,
        the strategy searches the vector store for the top `tables_limit` tables
        that are semantically most similar to the input query.

    3.  **Column Retrieval (Per Table):** For each relevant table identified in the
        previous step, the strategy performs a *separate* search within the vector store
        to find the top `columns_per_table_limit` columns belonging *specifically to that table*
        that are semantically most similar to the original input query. All columns found
        across the relevant tables are aggregated.

    4.  **Similar Query Retrieval:** Finally, the strategy searches the vector store
        for the top `queries_limit` previously stored queries that are semantically
        similar (but not necessarily identical) to the input query.

    The results (retrieved tables, aggregated relevant columns, and either the single
    exact-match query or multiple similar queries) are stored in the `RAGContext` object.
    This gathered information serves as context for subsequent steps in the RAG pipeline.

    The semantic similarity is typically determined by comparing vector embeddings
    using cosine similarity within the underlying `vector_store_search` implementation.
    """

    def __init__(
        self,
        vector_store_search: StoreSearch,
        tables_limit: int = 3,
        columns_per_table_limit: int = 5,
        queries_limit: int = 3,
        use_exact_match: bool = True,
        max_column_search_workers: int = 4,
    ):
        """
        Initialize the retrieval strategy.

        Args:
            vector_store_search: Component for searching the vector store
            tables_limit: Maximum number of tables to retrieve (default: 3)
            columns_per_table_limit: Maximum number of relevant columns to retrieve
                                     per relevant table (default: 5).
            queries_limit: Maximum number of previous queries to retrieve (default: 3)
            use_exact_match: Whether to check for exact matches in query store (default: True)
            max_column_search_workers: Maximum number of workers for parallel column search
        """
        self.vector_store_search = vector_store_search
        self.tables_limit = tables_limit
        self.columns_per_table_limit = columns_per_table_limit
        self.queries_limit = queries_limit
        self.use_exact_match = use_exact_match
        self.max_column_search_workers = max_column_search_workers

    def execute(self, context: RAGContext) -> RAGContext:
        """
        Execute the retrieval strategy on the current context using helper methods.

        Args:
            context: The RAG context containing the processed query.

        Returns:
            The updated RAG context with retrieved information or error metadata.
        """
        query = context.processed_query or context.original_query
        logger.info(f"Executing CosineSimRetrieval strategy for query: '{query[:100]}...'") # Log inizio

        # Add initial metadata
        context.add_metadata("retrieval_strategy", self.__class__.__name__)
        context.add_metadata("tables_limit", self.tables_limit)
        context.add_metadata("columns_per_table_limit", self.columns_per_table_limit)
        context.add_metadata("queries_limit", self.queries_limit)
        context.add_metadata("use_exact_match_setting", self.use_exact_match)

        try:
            # Step 0: Handle exact match if enabled
            if self._handle_exact_match(query, context):
                logger.info("Exact match found and handled. Skipping further retrieval steps.")
                return context # Early exit as exact match was found

            # If no exact match or disabled, perform semantic search steps
            # Step 1: Retrieve Relevant Tables
            self._retrieve_relevant_tables(query, context)

            # Step 2: Retrieve Relevant Columns PER TABLE
            self._retrieve_relevant_columns(query, context)

            # Step 3: Retrieve Relevant Queries (similar, not exact)
            self._retrieve_similar_queries(query, context)

            logger.info("CosineSimRetrieval strategy execution completed successfully.")
            return context

        except Exception as e:
            # Log con traceback completo grazie a logger.exception
            logger.exception(f"Critical error during CosineSimRetrieval execution: {str(e)}")
            context.add_metadata("retrieval_error", f"Critical error: {str(e)}")
            # Return the context even in case of critical error to allow
            # at the pipeline to handle the situation (maybe logging or failing)
            return context
        
    def _handle_exact_match(self, query: str, context: RAGContext) -> bool:
        """
        Checks for and handles an exact query match if enabled.

        Updates the context and returns True if an exact match is found and processed,
        indicating that the main execution flow should stop. Returns False otherwise.

        Args:
            query: The query string to match.
            context: The RAG context to update.

        Returns:
            True if an exact match was found and handled, False otherwise.
        """
        if not self.use_exact_match or not hasattr(
            self.vector_store_search, "find_exact_match"
        ):
            return False # Exact match disabled or not supported

        logger.debug(f"Checking for exact match for query: {query}")
        exact_match: Optional[QuerySearchResult] = self.vector_store_search.find_exact_match(query)

        if exact_match:
            logger.info(f"Found exact match for query: {query}")
            context.add_metadata("exact_match_found", True)
            context.retrieved_queries = [exact_match]
            return True
        else:
            logger.debug("No exact match found.")
            context.add_metadata("exact_match_found", False)
            return False
        
    def _retrieve_relevant_tables(self, query: str, context: RAGContext):
        """
        Retrieves relevant tables based on the query and updates the context.

        Args:
            query: The query string.
            context: The RAG context to update.
        """
        logger.debug(f"Retrieving relevant tables for query: {query}")
        context.retrieved_tables = self.vector_store_search.search_tables(
            question=query, limit=self.tables_limit
        )
        context.add_metadata("tables_retrieved", len(context.retrieved_tables))
        logger.info(f"Retrieved {len(context.retrieved_tables)} relevant tables.")

    
    def _search_columns_in_table_task(self, query: str, table_result: TableSearchResult) -> List[ColumnSearchResult]:
        """
        Task executed by a single thread to search for relevant columns in a specific table.

        Args:
            query: The query string.
            table_result: The table result to search in.

        Returns:
            A list of relevant columns found in the table.
        """
        if not table_result or not table_result.name:
            logger.warning("Skipping column search task for missing table data.")
            return []
        
        table_name = table_result.name
        logger.debug(f"Starting column search task for table '{table_name}'...")

        try:
            columns_for_this_table = self.vector_store_search.search_relevant_columns_in_table(
                question=query,
                table_name=table_name,
                limit=self.columns_per_table_limit
            )
            logger.debug(f"Completed column search task for table '{table_name}', found {len(columns_for_this_table)} columns.")
            return columns_for_this_table
        except Exception as e:
            logger.error(f"Column search task failed for table '{table_name}': {e}", exc_info=True)
            return [] # If for a table there is an error, we skip it and continue with the others

    def _retrieve_relevant_columns(self, query: str, context: RAGContext):
        """
        Retrieves relevant columns **concurrently** for each table present in the context.

        Args:
            query: The query string.
            context: The RAG context containing retrieved_tables and to be updated
                     with retrieved_columns.
        """
        all_relevant_columns: List[ColumnSearchResult] = []
        if not context.retrieved_tables:
            logger.info("No tables retrieved, skipping column search.")
            context.retrieved_columns = []
            context.add_metadata("columns_retrieved", 0)
            return
        
        valid_tables = [t for t in context.retrieved_tables if t and t.name]
        if not valid_tables:
             logger.warning("No valid tables with names found in context, skipping column search.")
             context.retrieved_columns = []
             context.add_metadata("columns_retrieved", 0)
             return

        logger.info(f"Starting concurrent column retrieval for {len(valid_tables)} tables using up to {self.max_column_search_workers} workers...")

        futures = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_column_search_workers) as executor:
            for table_result in valid_tables:
                # append in the list of futures the result of every search, executed in parallel
                futures.append(executor.submit(self._search_columns_in_table_task, query, table_result))

            for future in concurrent.futures.as_completed(futures):
                try:
                    # future in the result of a sigle search
                    # so, here we are getting the result of a single search
                    columns_list = future.result()
                    if columns_list: # if the list is not empty, we add it to the all_relevant_columns
                        all_relevant_columns.extend(columns_list)
                except Exception as e:
                    logger.error(f"Error retrieving result from a column search future: {e}", exc_info=True)

        context.retrieved_columns = all_relevant_columns
        context.add_metadata("columns_retrieved", len(context.retrieved_columns))
        logger.info(f"Finished concurrent column retrieval. Retrieved a total of {len(context.retrieved_columns)} relevant columns.")

    def _retrieve_similar_queries(self, query: str, context: RAGContext):
        """
        Retrieves similar queries based on the input query and updates the context.

        Args:
            query: The query string.
            context: The RAG context to update.
        """
        logger.debug(f"Retrieving relevant queries for query: {query}")
        context.retrieved_queries = self.vector_store_search.search_queries(
            question=query, limit=self.queries_limit
        )
        context.add_metadata("queries_retrieved", len(context.retrieved_queries))
        logger.info(f"Retrieved {len(context.retrieved_queries)} similar queries.")

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
        columns_per_table_limit = get_config_value(config, "columns_per_table_limit", 5, value_type=int)
        queries_limit = get_config_value(config, "queries_limit", 3, value_type=int)
        use_exact_match = get_config_value(config, "use_exact_match", True, value_type=bool)
        max_column_search_workers = get_config_value(config, "max_column_search_workers", 4, value_type=int)

        return cls(
            vector_store_search=vector_store_search,
            tables_limit=tables_limit,
            columns_per_table_limit=columns_per_table_limit,
            queries_limit=queries_limit,
            use_exact_match=use_exact_match,
            max_column_search_workers=max_column_search_workers,
        )
