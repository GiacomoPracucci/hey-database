from abc import ABC, abstractmethod
from typing import Optional, Tuple
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

class DatabaseConnector(ABC):
    """Interfaccia base per i connettori database"""
    
    @abstractmethod
    def connect(self) -> bool:
        """Stabilisce la connessione al database
        Returns:
            bool: True se la connessione ha successo, False altrimenti
        """
        pass
    
    def execute_query(self, query: str) -> Optional[Tuple]:
        """ Esegue una query SQL e restituisce i risultati.
        Args:
            query (str): Query SQL da eseguire
        Returns:
            Optional[Tuple]: Tupla (column_names, data) o None se si verifica un errore
        """   
        try:
            if not self.engine:
                if not self.connect():
                    return None
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                return result.keys()._keys, result.fetchall()
        
        except SQLAlchemyError as e:
            print(f"Errore nell'esecuzione della query: {str(e)}")
            return None     
    
    def close(self) -> None:
        """Chiude la connessione al DB"""
        if self.engine:
            self.engine.dispose()