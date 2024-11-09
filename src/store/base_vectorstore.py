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
    def add_entry(self, question: str, sql_query: str) -> bool:
        """Aggiunge una nuova entry nel vector store"""
        pass
    
    @abstractmethod
    def search_similar_questions(self, question: str, limit: int = 3) -> List[SearchResult]:
        """Cerca domande simili nel vectorstore"""
        pass
    
    @abstractmethod
    def increment_votes(self, question: str) -> bool:
        """Incrementa il contatore dei voti positivi per una query"""
        pass
    
    @abstractmethod
    def update_last_used(self, question: str) -> bool:
        """Aggiorna il timestamp di ultimo utilizzo"""
        pass