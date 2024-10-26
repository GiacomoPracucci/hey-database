from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from typing import Optional

class DatabaseManager:
    """ Classe per gestire la connessione e le query al database PostgreSQL"""
    
    def __init__(self,
                 host: str = "localhost",
                 port: str = "5432",
                 database: str = "postgres",
                 user: str = "postgres",
                 password: str = "admin"
                 ) -> None:
        
        self.connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        self.engine = None
        self.session_maker = None
    
    def connect(self) -> bool:
        """Stabilisce la connessione al database.
        
        Returns:
            bool: True se la connessione ha successo, False altrimenti"""
        
        try:
            self.engine = create_engine(self.connection_string)
            self.session_maker = sessionmaker(bind=self.engine)
            with self.engine.connect(): # verifica la connessione
                return True
            
        except SQLAlchemyError as e:
            print(f"Errore di connessione: {str(e)}")
            return False
    
    def execute_query(self, query: str) -> Optional[pd.DataFrame]:
        """ Esegue una query SQL e restituisce i risultati come DataFrame.
        
        Args:
            query (str): Query SQL da eseguire
            
        Returns:
            Optional[pd.DataFrame]: DataFrame con i risultati della query, None se si verifica un errore """   
        
        try:
            if not self.engine:
                if not self.connect():
                    return None
            
            return pd.read_sql_query(query, self.engine)
        
        except SQLAlchemyError as e:
            print(f"Errore nell'esecuzione della query: {str(e)}")
            return None     
    
    def close(self):
        """Chiude la connessione al database"""
        if self.engine:
            self.engine.dispose()