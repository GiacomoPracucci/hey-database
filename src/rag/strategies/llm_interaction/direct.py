import logging
from typing import Dict, Any, Optional

from src.rag.models import RAGContext
from src.rag.strategies import LLMInteractionStrategy
from src.llm_handler.llm_handler import LLMHandler

logger = logging.getLogger("hey-database")


class DirectLLMInteractionStrategy(LLMInteractionStrategy):
    """
    A strategy for direct interaction with an LLM.

    This strategy sends the prompt directly to the LLM and receives the response
    without any special handling or intermediate steps.
    """

    def __init__(
        self,
        llm_handler: LLMHandler,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2000,
    ):
        """
        Initialize the LLM interaction strategy.

        Args:
            llm_handler: Handler for interacting with the LLM
            system_prompt: Optional system prompt to set the LLM's behavior
            temperature: Temperature setting for the LLM (0-1)
            max_tokens: Maximum number of tokens in the response
        """
        self.llm_handler = llm_handler
        self.system_prompt = (
            system_prompt
            or "You are an SQL expert assistant that helps users query databases."
        )
        self.temperature = temperature
        self.max_tokens = max_tokens

    def execute(self, context: RAGContext) -> RAGContext:
        """
        Execute the strategy by sending the prompt to the LLM and getting the response.

        Args:
            context: The RAG context containing the final_prompt

        Returns:
            The updated RAG context with llm_response set
        """
        logger.debug("Sending prompt to LLM")
        context.add_metadata("llm_interaction_strategy", "direct")
        context.add_metadata("llm_temperature", self.temperature)

        if not context.final_prompt:
            error_msg = "No prompt available for LLM"
            logger.error(error_msg)
            context.add_metadata("llm_error", error_msg)
            return context

        try:
            # Send the prompt to the LLM and get the response
            response = self.llm_handler.get_completion(
                prompt=context.final_prompt,
                system_prompt=self.system_prompt,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            if response:
                context.llm_response = response
                logger.debug("Received response from LLM")
            else:
                error_msg = "Received empty response from LLM"
                logger.error(error_msg)
                context.add_metadata("llm_error", error_msg)

            return context

        except Exception as e:
            error_msg = f"Error during LLM interaction: {str(e)}"
            logger.exception(error_msg)
            context.add_metadata("llm_error", error_msg)
            return context

    @classmethod
    def from_config(
        cls, config: Dict[str, Any], llm_handler: Optional[LLMHandler] = None
    ) -> "DirectLLMInteractionStrategy":
        """
        Create a DirectLLMInteractionStrategy from a configuration dictionary.

        Args:
            config: Configuration dictionary with strategy parameters
            llm_handler: LLMHandler instance (required if not in config)

        Returns:
            An initialized DirectLLMInteractionStrategy

        Raises:
            ValueError: If LLMHandler is not provided
        """
        if llm_handler is None and "llm_handler" not in config:
            raise ValueError("LLM handler is required")

        return cls(
            llm_handler=llm_handler or config["llm_handler"],
            system_prompt=config.get("system_prompt"),
            temperature=config.get("temperature", 0.1),
            max_tokens=config.get("max_tokens", 2000),
        )
