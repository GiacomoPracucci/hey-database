from abc import ABC, abstractmethod

from src.embedding.base_embedding_model import EmbeddingModel
from src.vectorstore.base.base_vectorstore_client import BaseVectorStoreClient, VectorPoint

class BaseFeedbackService(ABC):
    """Interfaccia base per la gestione del feedback nel vector store"""
    
    def __init__(self, 
                 client: BaseVectorStoreClient,
                 embedding_model: EmbeddingModel):
        self.client = client
        self.embedding_model = embedding_model
    
    @abstractmethod
    def handle_positive_feedback(self,
                               question: str,
                               sql_query: str,
                               explanation: str) -> bool:
        """Gestisce il feedback positivo per una query
        
        Args:
            question: Domanda originale dell'utente
            sql_query: Query SQL generata
            explanation: Spiegazione della query
            
        Returns:
            bool: True se il feedback è stato gestito con successo
        """
        pass
    
    @abstractmethod
    def create_query_point(self,
                          question: str,
                          sql_query: str,
                          explanation: str,
                          positive_votes: int = 1) -> VectorPoint:
        """Crea un punto vettoriale per una query
        
        Args:
            question: Domanda originale dell'utente
            sql_query: Query SQL generata
            explanation: Spiegazione della query
            positive_votes: Numero di voti positivi
            
        Returns:
            VectorPoint: Punto da inserire nel vector store
        """
        pass