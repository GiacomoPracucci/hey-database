from snowflake import connector
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from typing import Optional
from src.connettori.base_connector import DatabaseConnector

class SnowflakeManager(DatabaseConnector):
    """Classe per gestire la connessione e le query a Snowflake"""
    
    def __init__(self,
                account: str,
                warehouse: str,
                database: str,
                schema: str,
                user: str,
                password: str,
                role: str = None
                ) -> None:
        """ Inizializza il connettore Snowflake
        
        Args:
            account (str): Account Snowflake (es: "xy12345.eu-central-1")
            warehouse (str): Nome del warehouse
            database (str): Nome del database
            schema (str): Nome dello schema
            user (str): Nome utente
            password (str): Password
            role (str, optional): Ruolo da utilizzare 
        """
        
        self.connection_params = {
            "account": account,
            "warehouse": warehouse,
            "database": database,
            "schema": schema,
            "user": user,
            "password": password,
            "role": role
        }
        self.engine = None

    def connect(self) -> bool:
        """Stabilisce la connessione a Snowflake"""
        try:
            connection_url = URL(
                account=self.connection_params["account"],
                user=self.connection_params["user"],
                password=self.connection_params["password"],
                database=self.connection_params["database"],
                schema=self.connection_params["schema"],
                warehouse=self.connection_params["warehouse"],
                role=self.connection_params["role"]
            )
            
            self.engine = create_engine(connection_url)
            
            with self.engine.connect():
                return True
        
        except SQLAlchemyError as e:
            print(f"Errore di connessione: {str(e)}")
            return False
        
    def execute_query(self, query: str) -> Optional[pd.DataFrame]:
        """Esegue una query SQL su snowflake e restituisce i risultati come DataFrame."""
        
        try:
            if not self.engine:
                if not self.connect():
                    return None
            
            return pd.read_sql_query(query, self.engine)
        
        except SQLAlchemyError as e:
            print(f"Errore nell'esecuzione della query su Snowflake: {str(e)}")
            return None
        
    
    def close(self) -> None:
        """Chiude la connessione al DB snowflake"""
        if self.engine:
            self.engine.dispose()