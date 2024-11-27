import logging

from src.config.models.app import AppConfig
from src.factories.database import DatabaseFactory
from src.factories.llm import LLMFactory
from src.factories.vector_store import VectorStoreFactory
from src.schema_metadata.enhancer import MetadataEnhancer
from src.llm_input.prompt_generator import PromptGenerator
from src.web.chat_service import ChatService

logger = logging.getLogger('hey-database')


class ChatServiceBuilder:
    """Builder per la creazione del ChatService"""
    
    def __init__(self, app_config: AppConfig):
        self.config = app_config
        self.db = None
        self.llm = None
        self.metadata_retriever = None
        self.metadata_enhancer = None
        self.vector_store = None
        self.prompt_generator = None
        
    def build_database(self) -> 'ChatServiceBuilder':
        """Costruisce e verifica la connessione database"""
        self.db = DatabaseFactory.create_connector(self.config.database)
        if not self.db.connect():
            raise RuntimeError("Failed to connect to database")
        return self
        
    def build_llm(self) -> 'ChatServiceBuilder':
        """Costruisce l'handler LLM"""
        self.llm = LLMFactory.create_handler(self.config.llm)
        return self
        
    def build_metadata_components(self) -> 'ChatServiceBuilder':
        """Costruisce i componenti per i metadata"""
        self.metadata_retriever = DatabaseFactory.create_metadata_retriever(
            self.config.database, 
            self.db
        )
        self.metadata_enhancer = MetadataEnhancer(self.llm)
        return self
        
    def build_vector_store(self) -> 'ChatServiceBuilder':
        """Costruisce e inizializza il vector store se abilitato"""
        if self.config.vector_store and self.config.vector_store.enabled:
            logger.info("Vector store enabled, initializing...")
            
            self.vector_store = VectorStoreFactory.create(self.config.vector_store)
            
            if not self.vector_store.collection_exists():
                logger.info("Vector store does not exist, creating enhanced metadata...")
                enhanced_metadata = self.metadata_enhancer.enhance_all_metadata(
                    self.metadata_retriever.get_all_tables_metadata()
                )
                if not self.vector_store.initialize(enhanced_metadata):
                    raise RuntimeError("Failed to initialize vector store with metadata")
            else:
                logger.info("Vector store exists, skipping metadata enhancement")
                if not self.vector_store.initialize():
                    raise RuntimeError("Failed to initialize existing vector store")
                    
        return self
        
    def build_prompt_generator(self) -> 'ChatServiceBuilder':
        """Costruisce il generatore di prompt"""
        self.prompt_generator = PromptGenerator(
            metadata_retriever=self.metadata_retriever,
            schema_name=self.config.database.schema,
            prompt_config=self.config.prompt,
            language=self.config.llm.language
        )
        return self
        
    def build(self) -> ChatService:
        """Costruisce e restituisce il ChatService completo"""
        if not all([self.db, self.llm, self.metadata_retriever, self.prompt_generator]):
            raise RuntimeError("Not all required components have been built")
            
        return ChatService(
            db=self.db,
            llm_manager=self.llm,
            metadata_retriever=self.metadata_retriever,
            prompt_generator=self.prompt_generator,
            vector_store=self.vector_store
        )