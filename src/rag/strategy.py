from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, TypeVar

# Define generic type variables for input and output
I = TypeVar("I")  # Input type
O = TypeVar("O")  # Output type


class RAGStrategy(Generic[I, O], ABC):
    """
    Abstract base class defining the interface for all RAG strategies.

    This is the core interface that all specific strategy implementations
    must implement. Each strategy takes an input of type I and produces
    an output of type O. This generic approach allows for type-safe
    chaining of strategies in the RAG pipeline.

    Strategies are designed to be stateless and configurable, with all
    necessary configuration provided at initialization time.
    """

    @abstractmethod
    def execute(self, input_data: I) -> O:
        """
        Execute the strategy on the provided input data.

        Args:
            input_data: The input data to process, of generic type I

        Returns:
            The processed output data, of generic type O

        Raises:
            Exception: If execution fails
        """
        pass

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "RAGStrategy":
        """
        Create a strategy instance from a configuration dictionary.

        This is a factory method intended to be implemented by concrete
        strategy classes. It enables dynamic instantiation of strategies
        based on configuration.

        Args:
            config: Configuration dictionary with parameters for the strategy

        Returns:
            An initialized strategy instance

        Raises:
            ValueError: If configuration is invalid
        """
        raise NotImplementedError(f"from_config not implemented for {cls.__name__}")
