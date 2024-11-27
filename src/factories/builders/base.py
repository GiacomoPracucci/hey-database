from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T')

class ServiceBuilder(ABC, Generic[T]):
    """Base builder interface for all service builders"""
    
    @abstractmethod
    def build_database(self) -> 'ServiceBuilder':
        pass
        
    @abstractmethod
    def build_llm(self) -> 'ServiceBuilder':
        pass
        
    @abstractmethod
    def build(self) -> T:
        pass