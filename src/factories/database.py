import logging

from src.config.models.db import DatabaseConfig

from src.connettori.postgres import PostgresManager
from src.connettori.mysql import MySQLManager
from src.connettori.snowflake import SnowflakeManager

from src.schema_metadata.postgres_metadata_retriever import PostgresMetadataRetriever
from src.schema_metadata.mysql_metadata_retriever import MySQLMetadataRetriever
from src.schema_metadata.snowflake_metadata_retriever import SnowflakeMetadataRetriever

logger = logging.getLogger('hey-database')

class DatabaseFactory:
    """Factory per la creazione dei componenti database"""
    
    @staticmethod
    def create_connector(config: DatabaseConfig):
        """Crea il connettore database appropriato"""
        db_types = {
            'postgres': PostgresManager,
            'mysql': MySQLManager,
            'snowflake': SnowflakeManager
        }
        
        if config.type not in db_types:
            raise ValueError(f"Database type {config.type} not supported")
            
        db_class = db_types[config.type]
        
        if config.type == 'snowflake':
            return db_class(
                account=config.account,
                warehouse=config.warehouse,
                database=config.database,
                schema=config.schema,
                user=config.user,
                password=config.password,
                role=config.role
            )
        else:
            return db_class(
                host=config.host,
                port=config.port,
                database=config.database,
                user=config.user,
                password=config.password
            )
    
    @staticmethod
    def create_metadata_retriever(config: DatabaseConfig, db):
        """Crea il metadata retriever appropriato"""
        retriever_types = {
            'postgres': PostgresMetadataRetriever,
            'mysql': MySQLMetadataRetriever,
            'snowflake': SnowflakeMetadataRetriever
        }
        
        if config.type not in retriever_types:
            raise ValueError(f"Metadata retriever for {config.type} not supported")
            
        retriever_class = retriever_types[config.type]
        return retriever_class(db.engine, schema=config.schema)