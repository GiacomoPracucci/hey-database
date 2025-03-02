import logging
from typing import Dict, Any

from src.rag.models import RAGContext, RAGResponse
from src.rag.strategies.strategies import (
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
    def from_config(cls, config: Dict[str, Any], strategy_factory=None) -> "RAGRecipe":
        """
        Create a RAGRecipe from a configuration dictionary.

        This factory method dynamically instantiates strategies based
        on the configuration, allowing recipes to be defined in
        configuration files.

        Args:
            config: Configuration dictionary defining the recipe
            strategy_factory: Optional factory function for creating strategy instances
                             If not provided, assumes strategy instances are directly in config

        Returns:
            RAGRecipe: Initialized recipe with all strategies

        Raises:
            ValueError: If configuration is invalid
            ImportError: If a strategy class cannot be imported
        """
        # Extract basic recipe information
        name = config.get("name")
        if not name:
            raise ValueError("Recipe configuration must include a 'name'")

        description = config.get("description", f"Recipe: {name}")

        # Validate that we have all required strategy sections
        required_strategies = [
            "query_understanding",
            "retrieval",
            "context_processing",
            "prompt_building",
            "llm_interaction",
            "response_processing",
        ]

        for strategy_type in required_strategies:
            if strategy_type not in config:
                raise ValueError(
                    f"Recipe configuration must include a '{strategy_type}' section"
                )

        # Create strategies based on configuration
        strategies = {}

        if strategy_factory:
            # If a strategy factory is provided, use it to create strategy instances
            for strategy_type in required_strategies:
                strategy_config = config[strategy_type]
                strategies[strategy_type] = strategy_factory(
                    strategy_type, strategy_config
                )
        else:
            # Otherwise, assume strategy instances are directly provided in the config
            for strategy_type in required_strategies:
                strategy = config.get(strategy_type)
                if not strategy:
                    raise ValueError(
                        f"Missing {strategy_type} strategy in recipe configuration"
                    )
                strategies[strategy_type] = strategy

        # Create and return the recipe
        return cls(
            name=name,
            description=description,
            query_understanding=strategies["query_understanding"],
            retrieval=strategies["retrieval"],
            context_processing=strategies["context_processing"],
            prompt_building=strategies["prompt_building"],
            llm_interaction=strategies["llm_interaction"],
            response_processing=strategies["response_processing"],
        )
