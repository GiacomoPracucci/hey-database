from typing import Optional

from src.rag.recipe import RAGRecipe
from src.rag.strategies.strategies import (
    QueryUnderstandingStrategy,
    RetrievalStrategy,
    ContextProcessingStrategy,
    PromptBuildingStrategy,
    LLMInteractionStrategy,
    ResponseProcessingStrategy,
)


class RAGRecipeBuilder:
    """
    Builder class for creating RAGRecipe instances using a fluent interface.

    This builder allows for the step-by-step construction of a RAGRecipe,
    with validation performed when the recipe is built to ensure all
    required components are present.
    """

    def __init__(self, name: str, description: str):
        """
        Initialize a new RAGRecipeBuilder.

        Args:
            name: Unique name for the recipe
            description: Human-readable description of the recipe
        """
        self.name = name
        self.description = description
        self._query_understanding: Optional[QueryUnderstandingStrategy] = None
        self._retrieval: Optional[RetrievalStrategy] = None
        self._context_processing: Optional[ContextProcessingStrategy] = None
        self._prompt_building: Optional[PromptBuildingStrategy] = None
        self._llm_interaction: Optional[LLMInteractionStrategy] = None
        self._response_processing: Optional[ResponseProcessingStrategy] = None

    def with_query_understanding(
        self, strategy: QueryUnderstandingStrategy
    ) -> "RAGRecipeBuilder":
        """
        Set the query understanding strategy.

        Args:
            strategy: The query understanding strategy to use

        Returns:
            self: Builder instance for method chaining
        """
        self._query_understanding = strategy
        return self

    def with_retrieval(self, strategy: RetrievalStrategy) -> "RAGRecipeBuilder":
        """
        Set the retrieval strategy.

        Args:
            strategy: The retrieval strategy to use

        Returns:
            self: Builder instance for method chaining
        """
        self._retrieval = strategy
        return self

    def with_context_processing(
        self, strategy: ContextProcessingStrategy
    ) -> "RAGRecipeBuilder":
        """
        Set the context processing strategy.

        Args:
            strategy: The context processing strategy to use

        Returns:
            self: Builder instance for method chaining
        """
        self._context_processing = strategy
        return self

    def with_prompt_building(
        self, strategy: PromptBuildingStrategy
    ) -> "RAGRecipeBuilder":
        """
        Set the prompt building strategy.

        Args:
            strategy: The prompt building strategy to use

        Returns:
            self: Builder instance for method chaining
        """
        self._prompt_building = strategy
        return self

    def with_llm_interaction(
        self, strategy: LLMInteractionStrategy
    ) -> "RAGRecipeBuilder":
        """
        Set the LLM interaction strategy.

        Args:
            strategy: The LLM interaction strategy to use

        Returns:
            self: Builder instance for method chaining
        """
        self._llm_interaction = strategy
        return self

    def with_response_processing(
        self, strategy: ResponseProcessingStrategy
    ) -> "RAGRecipeBuilder":
        """
        Set the response processing strategy.

        Args:
            strategy: The response processing strategy to use

        Returns:
            self: Builder instance for method chaining
        """
        self._response_processing = strategy
        return self

    def build(self) -> RAGRecipe:
        """
        Build and validate the RAGRecipe.

        Returns:
            RAGRecipe: The constructed recipe

        Raises:
            ValueError: If any required strategy is missing
        """
        # Validate that all required strategies are set
        if self._query_understanding is None:
            raise ValueError("Query understanding strategy is required")
        if self._retrieval is None:
            raise ValueError("Retrieval strategy is required")
        if self._context_processing is None:
            raise ValueError("Context processing strategy is required")
        if self._prompt_building is None:
            raise ValueError("Prompt building strategy is required")
        if self._llm_interaction is None:
            raise ValueError("LLM interaction strategy is required")
        if self._response_processing is None:
            raise ValueError("Response processing strategy is required")

        # Create and return the recipe
        return RAGRecipe(
            name=self.name,
            description=self.description,
            query_understanding=self._query_understanding,
            retrieval=self._retrieval,
            context_processing=self._context_processing,
            prompt_building=self._prompt_building,
            llm_interaction=self._llm_interaction,
            response_processing=self._response_processing,
        )
