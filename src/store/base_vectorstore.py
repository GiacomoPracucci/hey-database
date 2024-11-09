from abc import ABC, abstractmethod
from typing import List, Optional
from src.config.models import SearchResult

class VectorStore(ABC):
    """Interfaccia base per i vectorstore"""
    
    @abstractmethod 
    def initialize(self) -> bool:
        """Inizializza la connessione e crea la collection se necessario"""
        pass
    
    @abstractmethod
    def handle_positive_feedback(self) -> bool: 
        """ Gestisce il feedback positivo dell'utente per una coppia domanda-risposta.
        Se la coppia esiste, incrementa il contatore. Se non esiste, crea una nuova entry."""
    pass
        
    @abstractmethod
    def add_entry(self, question: str, sql_query: str) -> bool:
        """Aggiunge una nuova entry nel vector store"""
        pass
    
    @abstractmethod
    def search_similar_questions(self, question: str, limit: int = 3) -> List[SearchResult]:
        """Cerca domande simili nel vectorstore"""
        pass
