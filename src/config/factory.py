from typing import Dict, Type
from src.connettori.postgres import PostgresManager
from src.connettori.mysql import MySQLManager
from src.connettori.snowflake import SnowflakeManager
from src.dbcontext.postgres_metadata_retriever import PostgresMetadataRetriever
from src.dbcontext.mysql_metadata_retriever import MySQLMetadataRetriever
from src.dbcontext.snowflake_metadata_retriever import SnowflakeMetadataRetriever
from src.openai_.openai_handler import OpenAIHandler
from src.ollama_.ollama_handler import OllamaHandler
from src.llm_input.prompt_generator import PromptGenerator
from src.store.qdrant_store import QdrantStore
from src.web.chat_service import ChatService

class ServiceFactory:
    """ Factory class responsible for creating and configuring all major components of the application.
    It implements the Factory pattern to handle the creation of complex objects while keeping the code modular and testable.
    """
    
    @staticmethod
    def create_db_connector(config):
        """ Creates and configures the appropriate connector for the database specified in the configuration.
        This method implements a differentiated connection strategy for different types of databases,
        handling the configuration specifics of each (e.g., additional parameters for Snowflake).
        
        Args:
            config: Database configuration containing connection type and parameters
            
        Returns:
            A configured instance of the appropriate database connector
        
        Raises:
            ValueError: If the specified database type is not supported   
        """
        
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
        """ Creates the appropriate metadata retriever for the specified database.
        The retriever is responsible for extracting the database schema information
        (tables, columns, relationships) needed to generate accurate SQL queries.
        
        Args:
            config: Database configuration
            db: Instance of the database connector that has already been initialized

        Returns:
            A configured instance of the appropriate metadata retriever

        Raises:
            ValueError: If the database type does not have a supported retriever
        """
        
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
        """ Creates and configures the appropriate handler for the specified language model provider.
        Manages configuration for both cloud (OpenAI) and local (Ollama) models, setting the appropriate default parameters when needed.
        
        Args:
            config: Configuration of the language model

        Returns:
            A configured instance of the appropriate LLM handler

        Raises:
            ValueError: If the type of LLM is not supported or necessary parameters are missing
        """
        
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
    def create_vector_store(config):
        """Crea e configura il vector store appropriato.
        
        Args:
            config: Configurazione del vector store
            
        Returns:
            VectorStore: Istanza configurata del vector store o None se non supportato
        """
        if config.type == 'qdrant':
            # se è specificato un path, usiamo lo storage locale
            if config.path:
                store = QdrantStore(
                    path=config.path,
                    collection_name=config.collection_name
                )
            # altrimenti usiamo l'URL del server
            elif config.url:
                store = QdrantStore(
                    url=config.url,
                    collection_name=config.collection_name,
                    api_key=config.api_key
                )
            else:
                raise ValueError("Neither path nor url specified for Qdrant")
                
            if store.initialize():
                return store
            raise RuntimeError("Failed to initialize vector store")
                
        
    @staticmethod
    def create_chat_service(app_config):
        """ Main method that orchestrates the creation and initialization of all components required
        for the chat service. This is the main entry point for application configuration.
        
        The method follows these critical steps:
        1. Creates and verifies the database connection
        2. Initialize the language model
        3. Configures metadata retriever for database introspection
        4. Prepares the prompt generator that will combine metadata with user requests
        5. Assembles all components into a working chat service
        
        Args:
            app_config: Complete application configuration (database, LLM, prompts)

        Returns:
            A fully configured instance of ChatService ready to process requests

        Raises:
            RuntimeError: If the connection to the database fails
            ValueError: If the configuration is invalid or necessary components are missing
        """
        
        db = ServiceFactory.create_db_connector(app_config.database)
        if not db.connect():
            raise RuntimeError("Failed to connect to database")
        
        llm = ServiceFactory.create_llm_handler(app_config.llm)
        metadata_retriever = ServiceFactory.create_metadata_retriever(app_config.database, db)
        
        prompt_generator = PromptGenerator(
            metadata_retriever=metadata_retriever,
            schema_name=app_config.database.schema,
            prompt_config=app_config.prompt
        )        
        
        return ChatService(db, llm, metadata_retriever, prompt_generator)