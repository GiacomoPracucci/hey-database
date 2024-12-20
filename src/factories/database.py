import logging
from typing import Optional

from src.config.models.db import DatabaseConfig
from src.config.models.cache import CacheConfig
from src.llm_handler.base_llm_handler import LLMHandler
from src.schema_metadata.enhancing_strategy import MetadataEnhancementStrategy

from src.connettori.postgres import PostgresManager
from src.connettori.mysql import MySQLManager
from src.connettori.snowflake import SnowflakeManager
from src.connettori.vertica import VerticaManager

from src.schema_metadata.postgres_metadata_retriever import PostgresMetadataRetriever
from src.schema_metadata.mysql_metadata_retriever import MySQLMetadataRetriever
from src.schema_metadata.snowflake_metadata_retriever import SnowflakeMetadataRetriever
from src.schema_metadata.vertica_metadata_retriever import VerticaMetadataRetriever



logger = logging.getLogger('hey-database')

class DatabaseFactory:
    """Factory per la creazione dei componenti database"""
    
    @staticmethod
    def create_connector(config: DatabaseConfig):
        """Crea il connettore database appropriato"""
        db_types = {
            'postgres': PostgresManager,
            'mysql': MySQLManager,
            'snowflake': SnowflakeManager,
            'vertica': VerticaManager
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
    def create_metadata_retriever(config: DatabaseConfig,
                                  db,
                                  llm_handler: LLMHandler,
                                  enhancement_strategy: MetadataEnhancementStrategy,
                                  cache_config: Optional[CacheConfig] = None):
        """Crea il metadata retriever appropriato

        Args:
            config: Configurazione del database
            db: Istanza del database connector
            llm_handler: Handler per il modello di linguaggio
            enhancement_strategy: Strategia per l'enhancement dei metadati
            cache_config: Configurazione opzionale della cache
        """
        retriever_types = {
            'postgres': PostgresMetadataRetriever,
            'mysql': MySQLMetadataRetriever,
            'snowflake': SnowflakeMetadataRetriever,
            'vertica': VerticaMetadataRetriever
        }
        
        if config.type not in retriever_types:
            raise ValueError(f"Metadata retriever for {config.type} not supported")
            
        retriever_class = retriever_types[config.type]

        # determina la directory della cache se il caching è abilitato
        cache_dir = None
        if cache_config and cache_config.enabled:
            cache_dir = cache_config.directory
            logger.debug(f"Metadata caching enabled. Using directory: {cache_dir}")

        return retriever_class(
            db.engine,
            llm_handler=llm_handler,
            enhancement_strategy=enhancement_strategy,
            schema=config.schema,
            cache_dir=cache_dir
        )