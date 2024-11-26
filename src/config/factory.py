from typing import Dict, Type
from src.embedding.huggingface_embedding import HuggingFaceEmbedding
from src.embedding.openai_embedding import OpenAIEmbedding
       
from src.connettori.postgres import PostgresManager
from src.connettori.mysql import MySQLManager
from src.connettori.snowflake import SnowflakeManager
from src.schema_metadata.postgres_metadata_retriever import PostgresMetadataRetriever
from src.schema_metadata.mysql_metadata_retriever import MySQLMetadataRetriever
from src.schema_metadata.snowflake_metadata_retriever import SnowflakeMetadataRetriever
from src.schema_metadata.enhancer import MetadataEnhancer
from src.llm_handler.base_llm_handler import LLMHandler
from src.llm_handler.openai_handler import OpenAIHandler
from src.llm_handler.ollama_handler import OllamaHandler
from src.llm_handler.anthropic_handler import AnthropicHandler
from src.llm_input.prompt_generator import PromptGenerator
from src.store.qdrant_vectorstore import QdrantStore
from src.web.chat_service import ChatService
from src.embedding.base_embedding_model import EmbeddingModel

import logging
logger = logging.getLogger('hey-database')

class ServiceFactory:
    """ Factory class responsible for creating and configuring all major components of the application.
    It implements the Factory pattern to handle the creation of complex objects while keeping the code modular and testable.
    """

    @staticmethod
    def create_chat_service(app_config):
        """ Main method that orchestrates the creation and initialization of all components required
        for the chat service. This is the main entry point for application configuration.
        
        La sequenza di inizializzazione è:
        1. Crea connessione DB e verifica
        2. Crea LLM handler
        3. Crea metadata retriever e enhancer
        4. Se il vector store è abilitato:
           - Lo crea
           - Genera i metadati enhanced
           - Inizializza lo store con i metadati
        5. Crea il prompt generator
        6. Assembla il chat service
        
        Args:
            app_config: Complete application configuration (database, LLM, prompts)

        Returns:
            A fully configured instance of ChatService ready to process requests

        Raises:
            RuntimeError: If the connection to the database fails
            ValueError: If the configuration is invalid or necessary components are missing
        """
        
        # 1. Connessione al DB 
        db = ServiceFactory.create_db_connector(app_config.database)
        if not db.connect():
            raise RuntimeError("Failed to connect to database")
        
        # 2. LLM handler
        llm = ServiceFactory.create_llm_handler(app_config.llm)
        
        # 3. Metadata Components
        metadata_retriever = ServiceFactory.create_metadata_retriever(app_config.database, db)
        metadata_enhancer = ServiceFactory.create_metadata_enhancer(llm)
        
        # 4. Vector Store (se abilitato)
        vector_store = None
        enhanced_metadata = None
        
        if app_config.vector_store and app_config.vector_store.enabled:
            logger.info("Vector store enabled, initializing...")
            
            vector_store = ServiceFactory.create_vector_store(app_config.vector_store)
            
            # generazione dei metadati enhanced per autopopolamento dello store
            logger.debug("Generating enhanced metadata...")
            base_metadata = metadata_retriever.get_all_tables_metadata()
            enhanced_metadata = metadata_enhancer.enhance_all_metadata(base_metadata)
            
            # inizializziamo lo store con i metadati
            logger.debug("Initializing vector store with metadata...")
            if not vector_store.initialize(enhanced_metadata):
                raise RuntimeError("Failed to initialize vector store with metadata")
            
            logger.info("Vector store initialization completed")
            
        # 5. Prompt Generator
        prompt_generator = PromptGenerator(
            metadata_retriever=metadata_retriever,
            schema_name=app_config.database.schema,
            prompt_config=app_config.prompt,
            language=app_config.llm.language
        )        
        
        # 6. Chat Service
        return ChatService(
            db=db,
            llm_manager=llm, 
            metadata_retriever=metadata_retriever,
            prompt_generator=prompt_generator,
            vector_store=vector_store
        )
    
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
    def create_metadata_enhancer(llm_handler: LLMHandler) -> MetadataEnhancer:
        return MetadataEnhancer(llm_handler)
        
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
        
        try:
            if config.type == 'openai':
                if not config.api_key:
                    raise ValueError("OpenAI API key is required")
                handler = OpenAIHandler(
                    api_key=config.api_key,
                    chat_model=config.model or "gpt-4o"
                )
                logger.debug("Successfully created OpenAI handler")
                return handler
            elif config.type == 'anthropic':
                if not config.api_key:
                    raise ValueError("Anthropic API key is required")
                handler = AnthropicHandler(
                    api_key=config.api_key,
                    chat_model=config.model or "claude-3-5-sonnet-latest"
                )
                logger.debug("Successfully created Anthropic handler")
                return handler
            elif config.type == 'ollama':
                handler = OllamaHandler(
                    base_url=config.base_url or "http://localhost:11434",
                    model=config.model or "llama3.1"
                )
                logger.debug("Successfully created Ollama handler") 
                return handler
        except Exception as e:
            logger.exception(f"Error creating LLM handler: {e}")
            raise
        
    @staticmethod
    def create_vector_store(config):
        """Crea e configura il vector store appropriato.
        
        Args:
            config: Configurazione del vector store
            
        Returns:
            VectorStore: Istanza configurata del vector store o None se non supportato
        """
        if config.type == 'qdrant':
            # modello di embedding in base alla configurazione
            embedding_model = ServiceFactory.create_embedding_model(config.embedding)
            
            # se è specificato un path, usiamo lo storage locale
            if config.path:
                return QdrantStore(
                    path=config.path,
                    collection_name=config.collection_name,
                    embedding_model=embedding_model
                )
            # altrimenti usiamo l'URL del server
            elif config.url:
                return QdrantStore(
                    url=config.url,
                    collection_name=config.collection_name,
                    api_key=config.api_key,
                    embedding_model=embedding_model
                )
            else:
                raise ValueError("Neither path nor url specified for Qdrant")
        
        raise ValueError(f"Vector store type {config.type} not supported")

    @staticmethod
    def create_embedding_model(config: EmbeddingModel):
        """Creates the appropriate embedding model based on configuration
        
        Args:
            config: Embedding model configuration
            
        Returns:
            BaseEmbeddingModel: Configured embedding model instance
            
        Raises:
            ValueError: If the embedding type is not supported
        """
        if config.type == 'huggingface':
            return HuggingFaceEmbedding(model_name=config.model_name)
        elif config.type == 'openai':
            if not config.api_key:
                raise ValueError("OpenAI API key is required for OpenAI embeddings")
            return OpenAIEmbedding(api_key=config.api_key, model=config.model_name)
        else:
            raise ValueError(f"Embedding type {config.type} not supported")
        
