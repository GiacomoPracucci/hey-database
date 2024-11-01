from typing import Optional
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from src.connettori.base_connector import DatabaseConnector

class MySQLManager(DatabaseConnector):
    """Classe per gestire la connessione e le query al database MySQL/MariaDB"""
    
    def __init__(self,
                 host: str = "localhost",
                 port: str = "3306",
                 database: str = "mysql",
                 user: str = "root",
                 password: str = None,
                 charset: str = "utf8mb4",
                 ssl_ca: str = None
                 ) -> None:
        """Inizializza il connettore MySQL
        
        Args:
            host (str): Host del database
            port (str): Porta del database (default MySQL: 3306)
            database (str): Nome del database
            user (str): Nome utente
            password (str): Password
            charset (str): Set di caratteri da utilizzare (default: utf8mb4)
            ssl_ca (str, optional): Percorso al certificato SSL CA per connessioni sicure
        """
        params = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password,
            "charset": charset
        }
        
        if ssl_ca:
            params["ssl_ca"] = ssl_ca
            
        self.connection_string = (
            f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
            f"?charset={charset}"
        )
        
        if ssl_ca:
            self.connection_string += f"&ssl_ca={ssl_ca}"
            
        self.engine = None
        
    def connect(self) -> bool:
        """Stabilisce la connessione al database.
        
        Returns:
            bool: True se la connessione ha successo, False altrimenti
        
        Note:
            MySQL ha alcune specificità nella gestione delle connessioni:
            - Timeout più aggressivi rispetto a PostgreSQL
            - Diversa gestione del pool di connessioni
            - Necessità di gestire la codifica caratteri
        """
        
        try:
            self.engine = create_engine(
                self.connection_string,
                pool_recycle=3600, # per evitare il classico "Gone Away" error di MySQL, ricicla connessioni dopo un'ora
                pool_pre_ping=True # verifica connessione prima dell'uso
            )
            
            with self.engine.connect() as conn:
                conn.execute(text("SET SESSION sql_mode='STRICT_TRANS_TABLES'")) # impedisce l'inserimento di valori non validi nelle colonne
                                                                                # se provi a inserire una stringa troppo lunga, MySQL darà errore invece di troncarla
                                                                               # se provi a inserire un valore non valido per una data, MySQL darà errore invece di inserire un valore "zero"
                conn.execute(text("SET SESSION time_zone='+00:00'"))
                
                return True
        
        except SQLAlchemyError as e:
            print(f"Errore di connessione MySQL: {str(e)}")
            return False

    def execute_query(self, query: str) -> Optional[pd.DataFrame]:
        """Esegue una query SQL e restituisce i risultati come DataFrame """    
        
        try:
            if not self.engine:
                if not self.connect():
                    return None
                
            return pd.read_sql_query(query, self.engine)
        
        except SQLAlchemyError as e:
            print(f"Errore nell'esecuzione della query MySQL: {str(e)}")
            return None
        
    def close(self) -> None:
        """Chiude la connessione al database"""
        if self.engine:
            self.engine.dispose()