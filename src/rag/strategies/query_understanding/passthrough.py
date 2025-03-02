from typing import Dict, Any

from src.rag.models import RAGContext
from src.rag.strategies.strategies import QueryUnderstandingStrategy


class PassthroughQueryUnderstandingStrategy(QueryUnderstandingStrategy):
    """
    A simple query understanding strategy that passes the query through unchanged.

    This strategy simply sets the processed_query to be the same as the original_query,
    without performing any analysis or transformation.
    """

    def execute(self, context: RAGContext) -> RAGContext:
        """
        Execute the strategy by setting processed_query to original_query.

        Args:
            context: The RAG context containing the original query

        Returns:
            The updated RAG context with processed_query set
        """
        # Simply copy the original query to processed_query
        context.processed_query = context.original_query

        # Add metadata about the strategy used
        context.add_metadata("query_understanding_strategy", "passthrough")

        return context

    @classmethod
    def from_config(
        cls, config: Dict[str, Any], **dependencies
    ) -> "PassthroughQueryUnderstandingStrategy":
        """
        Create a PassthroughQueryUnderstandingStrategy from a configuration dictionary.

        This strategy doesn't require any configuration, so this method simply
        returns a new instance regardless of the configuration provided.

        Args:
            config: Configuration dictionary (ignored)
            **dependencies: Additional dependencies (ignored for this strategy)

        Returns:
            A new PassthroughQueryUnderstandingStrategy instance
        """
        # This strategy has no configurable parameters
        return cls()
