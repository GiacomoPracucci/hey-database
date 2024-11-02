from typing import Dict, Type
from src.connettori.postgres import PostgresManager
from src.connettori.mysql import MySQLManager
from src.connettori.snowflake import SnowflakeManager
from src.dbcontext.postgres_metadata_retriever import PostgresMetadataRetriever
from src.dbcontext.mysql_metadata_retriever import MySQLMetadataRetriever
from src.dbcontext.snowflake_metadata_retriever import SnowflakeMetadataRetriever
from src.openai_.openai_handler import OpenAIHandler
from src.ollama_.ollama_handler import OllamaHandler
from src.web.chat_service import ChatService

class ServiceFactory:
    
    @staticmethod
    def create_db_connector(config):
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
    def create_metadata_retriever(config, db):
        retriever_types = {
            'postgres': PostgresMetadataRetriever,
            'mysql': MySQLMetadataRetriever,
            'snowflake': SnowflakeMetadataRetriever
        }
        
        if config.type not in retriever_types:
            raise ValueError(f"Metadata retriever for {config.type} not supported")
        
        retriever_class = retriever_types[config.type]
        return retriever_class(db.engine, schema=config.schema)
    
    @staticmethod
    def create_llm_handler(config):
        if config.type == 'openai':
            if not config.api_key:
                raise ValueError("OpenAI API key is required")
            return OpenAIHandler(
                api_key=config.api_key,
                chat_model=config.model or "gpt-4o"
            )    
        elif config.type == 'ollama':
            return OllamaHandler(
                base_url=config.base_url or "http://localhost:11434",
                model=config.model or "llama2"
            )
        else:
            raise ValueError(f"LLM type {config.type} not supported")
        
    @staticmethod
    def create_chat_service(app_config):
        
        db = ServiceFactory.create_db_connector(app_config.database)
        if not db.connect():
            raise RuntimeError("Failed to connect to database")
        
        llm = ServiceFactory.create_llm_handler(app_config.llm)
        metadata_retriever = ServiceFactory.create_metadata_retriever(app_config.database, db)
        
        return ChatService(db, llm, metadata_retriever)