from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from src.connectors.connector import DatabaseConnector

import logging

logger = logging.getLogger("hey-database")


class PostgresManager(DatabaseConnector):
    """Classe per gestire la connessione e le query al database PostgreSQL"""

    def __init__(
        self,
        host: str = "localhost",
        port: str = "5432",
        database: str = "postgres",
        user: str = "postgres",
        password: str = None,
        schema: str = "northwind", 
    ) -> None:
        self.schema = schema
        self.connection_string = (
            f"postgresql://{user}:{password}@{host}:{port}/{database}"
        )
        self.engine = None
        self.connect()

    def connect(self) -> bool:
        """Stabilisce la connessione al database.
        Inizializza sia l'engine per query raw SQL che il session maker per operazioni ORM.
        Returns:
            bool: True se la connessione ha successo, False altrimenti"""

        try:
            self.engine = create_engine(self.connection_string)

            with self.engine.connect():
                logger.info("Connected to PostgreSQL database")
                return True

        except SQLAlchemyError as e:
            logger.error(f"Failed to connect to PostgreSQL database: {str(e)}")
            return False
