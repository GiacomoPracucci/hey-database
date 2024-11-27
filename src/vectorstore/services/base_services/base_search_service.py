from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass

from src.embedding.base_embedding_model import EmbeddingModel
from src.vectorstore.base.base_vectorstore_client import BaseVectorStoreClient
from src.vectorstore.services.base_services.base_metadata_service import TablePayload

@dataclass
class QueryPayload:
    """Payload per le query nel vector store"""
    question: str
    sql_query: str
    explanation: str
    positive_votes: int
    type: str = "query"  # discriminator per distinguere i tipi di documento

@dataclass
class SearchResult:
    """Risultato generico di una ricerca"""
    payload: Dict
    score: float

@dataclass
class TableSearchResult:
    """Risultato della ricerca di tabelle"""
    table_name: str
    metadata: TablePayload
    score: float

@dataclass
class QuerySearchResult:
    """Risultato della ricerca di query"""
    question: str
    sql_query: str
    explanation: str
    score: float
    positive_votes: int

class BaseSearchService(ABC):
    """Interfaccia base per le operazioni di ricerca nel vector store"""
    
    def __init__(self, 
                 client: BaseVectorStoreClient,
                 embedding_model: EmbeddingModel):
        self.client = client
        self.embedding_model = embedding_model
    
    @abstractmethod
    def search_similar_tables(self, 
                            question: str, 
                            limit: int = 3) -> List[TableSearchResult]:
        """Cerca tabelle simili alla domanda dell'utente
        
        Args:
            question: Domanda dell'utente
            limit: Numero massimo di risultati
            
        Returns:
            List[TableSearchResult]: Lista di tabelle rilevanti
        """
        pass
    
    @abstractmethod
    def search_similar_queries(self, 
                             question: str, 
                             limit: int = 3) -> List[QuerySearchResult]:
        """Cerca query simili alla domanda dell'utente
        
        Args:
            question: Domanda dell'utente
            limit: Numero massimo di risultati
            
        Returns:
            List[QuerySearchResult]: Lista di query rilevanti
        """
        pass
    
    @abstractmethod
    def find_exact_query_match(self, question: str) -> Optional[QuerySearchResult]:
        """Cerca una corrispondenza esatta per una domanda
        
        Args:
            question: Domanda dell'utente
            
        Returns:
            Optional[QuerySearchResult]: Query corrispondente se trovata
        """
        pass
