from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T')

class AgentBuilder(ABC, Generic[T]):
    """Base builder interface for all agent builders"""

    @abstractmethod
    def build_database(self) -> 'AgentBuilder':
        pass

    @abstractmethod
    def build_llm(self) -> 'AgentBuilder':
        pass

    @abstractmethod
    def build(self) -> T:
        pass
