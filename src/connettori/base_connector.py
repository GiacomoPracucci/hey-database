from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd

class DatabaseConnector(ABC):
    """Interfaccia base per i connettori database"""
    
    @abstractmethod
    def connect(self) -> bool:
        """Stabilisce la connessione al database
        Returns:
            bool: True se la connessione ha successo, False altrimenti
        """
        pass
    
    @abstractmethod
    def execute_query(self, query: str) -> Optional[pd.DataFrame]:
        """Esegue una query SQL e restituisce i risultati come DataFrame
        
        Args:
            query (str): Query SQL da eseguire
            
        Returns:
            Optional[pd.DataFrame]: DataFrame con i risultati della query, None se si verifica un errore
        """
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Chiude la connessione al database"""
        pass