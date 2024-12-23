from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from src.connettori.connector import DatabaseConnector

class VerticaManager(DatabaseConnector):
    """Classe per gestire la connessione e le query al database Vertica"""

    def __init__(self,
                 host: str = "localhost",
                 port: str = "5433",
                 database: str = "vertica",
                 user: str = "dbadmin",
                 password: str = None) -> None:
        """Inizializza il connettore Vertica

        Args:
            host (str): Host del database
            port (str): Porta del database (default Vertica: 5433)
            database (str): Nome del database
            user (str): Nome utente
            password (str): Password
        """
        self.connection_string = f"vertica+vertica_python://{user}:{password}@{host}:{port}/{database}"
        self.engine = None

    def connect(self) -> bool:
        """Stabilisce la connessione al database.

        Returns:
            bool: True se la connessione ha successo, False altrimenti

        Note:
            Vertica ha alcune particolarità:
            - Supporta il bilanciamento del carico tra i nodi
            - Permette di etichettare le sessioni per il monitoraggio
            - Ha timeouts configurabili per le connessioni
        """
        try:
            self.engine = create_engine(self.connection_string)

            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                return True

        except SQLAlchemyError as e:
            print(f"Errore di connessione a Vertica: {str(e)}")
            return False