import logging

from src.models.db import DatabaseConfig

from src.connectors.postgres import PostgresManager
from src.connectors.mysql import MySQLManager
from src.connectors.snowflake import SnowflakeManager
from src.connectors.vertica import VerticaManager


logger = logging.getLogger("hey-database")


class DatabaseFactory:
    """Factory per la creazione dei componenti database"""

    @staticmethod
    def create_connector(config: DatabaseConfig):
        """Crea il connettore database appropriato"""
        db_types = {
            "postgres": PostgresManager,
            "mysql": MySQLManager,
            "snowflake": SnowflakeManager,
            "vertica": VerticaManager,
        }

        if config.type not in db_types:
            raise ValueError(f"Database type {config.type} not supported")

        db_class = db_types[config.type]

        if config.type == "snowflake":
            return db_class(
                account=config.account,
                warehouse=config.warehouse,
                database=config.database,
                schema=config.schema,
                user=config.user,
                password=config.password,
                role=config.role,
            )
        else:
            return db_class(
                host=config.host,
                port=config.port,
                database=config.database,
                user=config.user,
                password=config.password,
            )
