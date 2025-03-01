import logging
from typing import Dict, Any

from src.rag.models import RAGContext, RAGResponse
from src.rag.strategies import (
    QueryUnderstandingStrategy,
    RetrievalStrategy,
    ContextProcessingStrategy,
    PromptBuildingStrategy,
    LLMInteractionStrategy,
    ResponseProcessingStrategy,
)

logger = logging.getLogger("hey-database")


class RAGRecipe:
    """
    A Recipe that orchestrates the execution of RAG strategies.

    A RAGRecipe composes multiple strategies, each responsible for a specific
    phase of the RAG pipeline. When executed, the recipe passes a RAGContext
    through each strategy in sequence, ultimately producing a RAGResponse.
    """

    def __init__(
        self,
        name: str,
        description: str,
        query_understanding: QueryUnderstandingStrategy,
        retrieval: RetrievalStrategy,
        context_processing: ContextProcessingStrategy,
        prompt_building: PromptBuildingStrategy,
        llm_interaction: LLMInteractionStrategy,
        response_processing: ResponseProcessingStrategy,
    ):
        """
        Initialize a RAGRecipe with all required strategies.

        Args:
            name: Unique name of the recipe
            description: Human-readable description of the recipe
            query_understanding: Strategy for understanding the user query
            retrieval: Strategy for retrieving relevant information
            context_processing: Strategy for processing retrieved context
            prompt_building: Strategy for building the LLM prompt
            llm_interaction: Strategy for interacting with the LLM
            response_processing: Strategy for processing the LLM response
        """
        self.name = name
        self.description = description
        self.query_understanding = query_understanding
        self.retrieval = retrieval
        self.context_processing = context_processing
        self.prompt_building = prompt_building
        self.llm_interaction = llm_interaction
        self.response_processing = response_processing

    def execute(self, question: str) -> RAGResponse:
        """
        Execute the RAG pipeline with the given user question.

        This method orchestrates the execution of all strategies in sequence,
        passing the RAGContext from one to the next, and handling any errors
        that occur during execution.

        Args:
            question: The user's question

        Returns:
            RAGResponse: The response to the user's question
        """
        try:
            # Initialize context with original query
            context = RAGContext(original_query=question)
            logger.debug(f"Executing RAG recipe: {self.name}")

            # Execute each strategy in sequence
            logger.debug("Executing query understanding strategy")
            context = self.query_understanding.execute(context)

            logger.debug("Executing retrieval strategy")
            context = self.retrieval.execute(context)

            logger.debug("Executing context processing strategy")
            context = self.context_processing.execute(context)

            logger.debug("Executing prompt building strategy")
            context = self.prompt_building.execute(context)

            logger.debug("Executing LLM interaction strategy")
            context = self.llm_interaction.execute(context)

            logger.debug("Executing response processing strategy")
            response = self.response_processing.execute(context)

            # Add recipe metadata to response
            response.metadata["recipe_name"] = self.name

            logger.debug(f"RAG recipe {self.name} execution completed successfully")
            return response

        except Exception as e:
            logger.exception(f"Error executing RAG recipe {self.name}: {str(e)}")
            return RAGResponse(
                success=False,
                error=f"Error executing RAG pipeline: {str(e)}",
                original_question=question,
            )

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "RAGRecipe":
        """
        Create a RAGRecipe from a configuration dictionary.

        This factory method dynamically instantiates strategies based
        on the configuration, allowing recipes to be defined in
        configuration files.

        Args:
            config: Configuration dictionary defining the recipe

        Returns:
            RAGRecipe: Initialized recipe with all strategies

        Raises:
            ValueError: If configuration is invalid
            ImportError: If a strategy class cannot be imported
        """
        # This is a placeholder for now - we'll implement this later
        # when we have strategy implementations and a configuration system
        raise NotImplementedError("Recipe configuration loading not yet implemented")
