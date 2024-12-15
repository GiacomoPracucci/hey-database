import logging
from src.config.models.app import AppConfig
from src.factories.database import DatabaseFactory
from src.factories.llm import LLMFactory
from src.factories.vector_store import VectorStoreFactory
from src.agents.sql_agent import SQLAgent
from src.factories.builders.base import AgentBuilder
from src.agents.metadata_enhancer_agent import MetadataAgent

logger = logging.getLogger('hey-database')

class SQLAgentBuilder(AgentBuilder[SQLAgent]):
    """Builder per la creazione dell'SQLAgent"""

    def __init__(self, app_config: AppConfig):
        self.config = app_config
        self.db = None
        self.llm = None
        self.metadata_retriever = None
        self.metadata_enhancer_agent = None
        self.vector_store = None

    def build_database(self) -> 'SQLAgentBuilder':
        """Costruisce e verifica la connessione database"""
        self.db = DatabaseFactory.create_connector(self.config.database)
        if not self.db.connect():
            raise RuntimeError("Failed to connect to database")
        return self

    def build_llm(self) -> 'SQLAgentBuilder':
        """Costruisce l'handler LLM"""
        self.llm = LLMFactory.create_handler(self.config.llm)
        return self

    def build_metadata_components(self) -> 'SQLAgentBuilder':
        """Costruisce i componenti per i metadata"""
        # crea metadata retriever
        self.metadata_retriever = DatabaseFactory.create_metadata_retriever(
            self.config.database,
            self.db,
            self.config.cache
        )
        # agente per l'enhancement dei metadati
        self.metadata_enhancer_agent = MetadataAgent(llm_handler=self.llm)

        return self

    def build_vector_store(self) -> 'SQLAgentBuilder':
        """Costruisce e inizializza il vector store se abilitato"""
        if self.config.vector_store and self.config.vector_store.enabled:
            logger.info("Vector store enabled, initializing...")

            self.vector_store = VectorStoreFactory.create(self.config.vector_store)

            if not self.vector_store.collection_exists():
                logger.info("Vector store does not exist, creating enhanced metadata...")
                # usa l'agente interno per l'enhancement
                metadata_response = self.metadata_enhancer_agent.run(
                    self.metadata_retriever.get_all_tables_metadata()
                )
                if not metadata_response.success:
                    raise RuntimeError("Failed to enhance metadata")

                if not self.vector_store.initialize(metadata_response.enhanced_metadata):
                    raise RuntimeError("Failed to initialize vector store with metadata")
            else:
                logger.info("Vector store exists, skipping metadata enhancement")
                if not self.vector_store.initialize():
                    raise RuntimeError("Failed to initialize existing vector store")

        return self

    def build(self) -> SQLAgent:
        """Costruisce e restituisce l'SQLAgent"""
        if not all([self.db, self.llm, self.metadata_retriever]):
            raise RuntimeError("Not all required components have been built")

        return SQLAgent(
            db=self.db,
            llm_manager=self.llm,
            metadata_retriever=self.metadata_retriever,
            schema_name=self.config.database.schema,
            prompt_config=self.config.prompt,
            vector_store=self.vector_store,
            language=self.config.llm.language
        )