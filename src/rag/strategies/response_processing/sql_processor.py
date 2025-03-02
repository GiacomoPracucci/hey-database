import logging
import re
from typing import Dict, Any, List, Optional, Tuple

from src.rag.models import RAGContext, RAGResponse
from src.rag.strategies.strategies import ResponseProcessingStrategy
from src.connectors.connector import DatabaseConnector

logger = logging.getLogger("hey-database")


class SQLResponseProcessor(ResponseProcessingStrategy):
    """
    A response processing strategy for extracting SQL queries from LLM responses,
    executing them, and formatting the results.

    This strategy parses the LLM response to extract the SQL query, executes it
    against the database, and formats the results into a structured response.
    """

    def __init__(
        self,
        db: DatabaseConnector,
        max_preview_rows: int = 10,
        execute_query: bool = True,
    ):
        """
        Initialize the SQL response processor.

        Args:
            db: Database connector for executing queries
            max_preview_rows: Maximum number of rows to include in preview (default: 10)
            execute_query: Whether to execute extracted queries (default: True)
        """
        self.db = db
        self.max_preview_rows = max_preview_rows
        self.execute_query = execute_query

    def execute(self, context: RAGContext) -> RAGResponse:
        """
        Process the LLM response to extract and execute SQL queries.

        Args:
            context: The RAG context containing the llm_response

        Returns:
            A structured RAGResponse with query, explanation, and results
        """
        logger.debug("Processing LLM response")

        # Initialize response with default values
        response = RAGResponse(
            success=False,
            original_question=context.original_query,
        )

        # Add metadata about the strategy used
        response.metadata["response_processing_strategy"] = "sql_processor"

        # Handle case where LLM response is missing
        if not context.llm_response:
            logger.error("No LLM response to process")
            response.error = "No response received from the language model"
            return response

        # Extract SQL query and explanation from LLM response
        sql_query, explanation = self._extract_sql_and_explanation(context.llm_response)

        if not sql_query:
            logger.error("No SQL query found in LLM response")
            response.error = "Could not extract a valid SQL query from the response"
            response.explanation = (
                context.llm_response
            )  # Use full response as explanation
            return response

        # Set the query and explanation in the response
        response.query = sql_query
        response.explanation = explanation if explanation else "No explanation provided"

        # Check if we should execute the query
        if not self.execute_query:
            logger.debug("Query execution disabled, returning without results")
            response.success = True
            return response

        # Execute the query and get results
        logger.debug(f"Executing SQL query: {sql_query}")
        query_result = self._execute_query(sql_query)

        if query_result is None:
            logger.error("Query execution failed")
            response.error = "Failed to execute the SQL query"
            response.success = False
            return response

        # Unpack query results
        columns, rows = query_result

        # Convert results to list of dictionaries for JSON serialization
        results = [dict(zip(columns, row)) for row in rows]

        # Limit the number of rows for preview
        preview = (
            results[: self.max_preview_rows]
            if len(results) > self.max_preview_rows
            else results
        )

        # Set the results in the response
        response.results = results
        response.preview = preview
        response.success = True

        logger.debug(f"Successfully processed response with {len(results)} result rows")

        # Check if this was retrieved from vector store
        if context.metadata.get("exact_match_found"):
            response.from_vector_store = True

        return response

    def _extract_sql_and_explanation(
        self, text: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract SQL query and explanation from LLM response text.

        Attempts to parse the response as JSON first, falling back to regex-based
        extraction if JSON parsing fails.

        Args:
            text: LLM response text

        Returns:
            Tuple containing (sql_query, explanation), either can be None if not found
        """
        import json

        # First, try to parse as JSON
        try:
            # Clean up the text to extract JSON if it's wrapped in markdown
            cleaned_text = text.strip()

            # Handle markdown code blocks
            if "```json" in cleaned_text:
                cleaned_text = cleaned_text.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned_text:
                # Might be a code block without language specification
                cleaned_text = cleaned_text.split("```")[1].split("```")[0].strip()

            # Parse the JSON
            response_json = json.loads(cleaned_text)

            # Extract query and explanation
            if isinstance(response_json, dict):
                sql_query = response_json.get("query")
                explanation = response_json.get("explanation")

                if sql_query:
                    logger.debug("Successfully extracted SQL query from JSON response")
                    return sql_query, explanation

        except (json.JSONDecodeError, IndexError) as e:
            logger.warning(
                f"Failed to parse response as JSON: {str(e)}. Falling back to regex."
            )

        # If JSON parsing failed, fall back to regex-based extraction
        logger.debug("Using regex fallback to extract SQL query")

        # Look for SQL code blocks with markdown backticks
        sql_match = re.search(r"```sql\s*([\s\S]*?)\s*```", text, re.IGNORECASE)

        if not sql_match:
            # Try to find code blocks without specifying sql
            sql_match = re.search(r"```\s*([\s\S]*?)\s*```", text)

        if not sql_match:
            # Look for SQL keywords as a last resort
            # This is more error-prone but better than nothing
            sql_pattern = r"(?:SELECT|INSERT|UPDATE|DELETE)[\s\S]*?;"
            sql_match = re.search(sql_pattern, text, re.IGNORECASE)

        # Extract SQL query if found
        sql_query = sql_match.group(1).strip() if sql_match else None

        # If we found the query with the last resort method, we need to get the full match
        if sql_match and not sql_query:
            sql_query = sql_match.group(0).strip()

        # Extract explanation (everything before the SQL query)
        explanation = None
        if sql_match:
            explanation_text = text[: sql_match.start()].strip()
            if explanation_text:
                explanation = explanation_text

        return sql_query, explanation

    def _execute_query(self, query: str) -> Optional[Tuple[List[str], List[Tuple]]]:
        """
        Execute a SQL query and return the results.

        Args:
            query: SQL query to execute

        Returns:
            Tuple of (column_names, rows) or None if execution fails
        """
        try:
            return self.db.execute_query(query)
        except Exception as e:
            logger.exception(f"Error executing query: {str(e)}")
            return None

    @classmethod
    def from_config(
        cls, config: Dict[str, Any], **dependencies
    ) -> "SQLResponseProcessor":
        """
        Create a SQLResponseProcessor from a configuration dictionary.

        Args:
            config: Configuration dictionary with processor parameters
            **dependencies: Additional dependencies, must include db_connector or db

        Returns:
            An initialized SQLResponseProcessor

        Raises:
            ValueError: If database connector is not provided
        """
        from src.rag.utils import get_config_value

        # Check for required dependencies - support both 'db_connector' and 'db' for flexibility
        db_connector = dependencies.get("db_connector") or dependencies.get("db")
        if db_connector is None:
            raise ValueError(
                "Database connector dependency is required for SQLResponseProcessor"
            )

        return cls(
            db=db_connector,
            max_preview_rows=get_config_value(
                config, "max_preview_rows", 10, value_type=int
            ),
            execute_query=get_config_value(
                config, "execute_query", True, value_type=bool
            ),
        )
