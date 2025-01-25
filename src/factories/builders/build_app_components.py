import logging
from src.models.app import AppConfig
from src.factories.database import DatabaseFactory
from src.factories.vector_store import VectorStoreFactory
from src.models.app import AppComponents
from src.factories.llm import LLMFactory
from src.factories.cache import CacheFactory
from src.metadata.enhancement_strategy import MetadataEnhancementStrategy

logger = logging.getLogger("hey-database")


class VectorStoreBasedStrategy(MetadataEnhancementStrategy):
    """Strategy che determina se fare enhancement dei metadati basandosi sullo stato del vector store"""

    def __init__(self, vector_store):
        self.vector_store = vector_store

    def should_enhance(self) -> bool:
        """Determina se i metadati devono essere arricchiti.
        Li arricchisce solo se il vector store non esiste già"""
        if not self.vector_store.collection_exists():
            return True
        return (
            self.vector_store.client.count(self.vector_store.collection_name).count == 0
        )


class DefaultEnhancementStrategy(MetadataEnhancementStrategy):
    """Strategy di default quando non c'è un vector store"""

    def should_enhance(self) -> bool:
        """Senza vector store, non facciamo l'enhancement"""
        return False


class AppComponentsBuilder:
    def __init__(self, app_config: AppConfig):
        self.config = app_config
        self.db = None
        self.vector_store = None
        self.metadata_retriever = None
        self.sql_llm = None
        self.cache = None

    def build_database(self):
        """Costruisce e verifica la connessione database"""
        self.db = DatabaseFactory.create_connector(self.config.database)
        if not self.db.connect():
            raise RuntimeError("Failed to connect to database")
        return self

    def build_vector_store(self):
        """Costruisce e inizializza il vector store se abilitato"""
        if self.config.vector_store and self.config.vector_store.enabled:
            logger.info("Vector store enabled, initializing...")
            self.vector_store = VectorStoreFactory.create(self.config.vector_store)
            if not self.vector_store.initialize():
                raise RuntimeError("Failed to initialize vector store")
            logger.info("Vector store initialized successfully")
        return self

    def build_sql_llm(self):
        """Costruisce l'handler LLM"""
        self.llm = LLMFactory.create_handler(self.config.llm)
        return self

    def build_metadata_extractor(self):
        """Costruisce i componenti per i metadati
        Enhancement strategy decide se fare enhancement o meno, con la seguente logica:
        - Se è abilitato il vector store, fa enhancement solo se il vector store non esiste
        - Altrimenti, non fa enhancement, percchè la description ci serve principalmente per semantic search dallo store
        """
        if not self.llm:
            raise RuntimeError("LLM handler must be built before metadata components")

        # determina la strategia di enhancement appropriata
        enhancement_strategy = (
            VectorStoreBasedStrategy(self.vector_store)
            if self.vector_store
            else DefaultEnhancementStrategy()
        )

        self.metadata_retriever = DatabaseFactory.create_metadata_retriever(
            self.config.database,
            self.db,
            self.llm,
            enhancement_strategy,
            self.config.metadata,
            self.config.cache,
        )

        return self

    def build_cache(self):
        """Costruisce il componente per la cache"""
        self.cache = CacheFactory.create_cache(self.config.cache)
        return self

    def build(self) -> AppComponents:
        """Costruisce e restituisce l'app inizializzata"""

        self.build_database()
        self.build_vector_store()
        self.build_sql_llm()
        self.build_metadata_extractor()
        self.build_cache()

        # se abbiamo un vector store, lo popoliamo in automatico con i metadati estratti
        if self.vector_store:
            if not self.vector_store.populate_store_with_metadata(
                self.metadata_retriever.tables  # TODO questa cosa qui non funziona piu e va fixata
            ):
                raise RuntimeError("Failed to populate vector store with metadata")

        return AppComponents(
            db=self.db,
            vector_store=self.vector_store,
            sql_llm=self.llm,
            cache=self.cache,
            metadata_extractor=self.metadata_retriever,
        )
