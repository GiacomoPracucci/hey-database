from abc import ABC, abstractmethod
from typing import Optional, List, Generic, TypeVar
from dataclasses import dataclass

# type variable for point payload
T = TypeVar('T')

@dataclass
class VectorPoint(Generic[T]):
    """Rappresenta un punto nel vector store"""
    id: str
    vector: List[float]
    payload: T

class BaseVectorStoreClient(ABC):
    """Client base per le operazioni CRUD con il vector store"""
    
    @abstractmethod
    def connect(self) -> bool:
        """Stabilisce la connessione con il backend"""
        pass
    
    @abstractmethod
    def create_collection(self, 
                         collection_name: str,
                         vector_size: int) -> bool:
        """Crea una nuova collection nel vector store
        
        Args:
            collection_name: Nome della collection
            vector_size: Dimensione dei vettori
        """
        pass
    
    @abstractmethod
    def collection_exists(self, collection_name: str) -> bool:
        """Verifica se una collection esiste"""
        pass
    
    @abstractmethod
    def add_points(self, 
                  collection_name: str,
                  points: List[VectorPoint]) -> bool:
        """Aggiunge punti alla collection
        
        Args:
            collection_name: Nome della collection
            points: Lista di punti da aggiungere
        """
        pass

    @abstractmethod
    def get_points(self,
                  collection_name: str,
                  point_ids: List[str]) -> List[VectorPoint]:
        """Recupera punti specifici dalla collection
        
        Args:
            collection_name: Nome della collection
            point_ids: Lista di ID dei punti da recuperare
        """
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Chiude la connessione con il backend"""
        pass
