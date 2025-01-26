import logging
from src.models.app import AppConfig
from src.factories.database import DatabaseFactory
from src.factories.metadata import MetadataFactory
from src.factories.vector_store import VectorStoreFactory
from src.models.app import AppComponents
from src.factories.llm import LLMFactory
from src.factories.cache import CacheFactory

logger = logging.getLogger("hey-database")


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
        logger.info("Vector store enabled, initializing client...")
        self.vector_store = VectorStoreFactory.create(self.config.vector_store)
        return self

    def build_sql_llm(self):
        """Costruisce l'handler LLM"""
        self.llm = LLMFactory.create_handler(self.config.llm)
        return self

    def build_table_metadata_extractor(self):
        """Builds the table metadata extractor"""
        if not self.db:
            raise RuntimeError("Cannot build metadata extractor without DB connection")

        self.table_metadata_extractor = MetadataFactory.create_table_metadata_extractor(
            config=self.config.database,  # DB config cause the extractor type depends on the DB type
            db=self.db,
        )
        return self

    def build_column_metadata_extractor(self):
        """Builds the column metadata extractor"""
        if not self.db:
            raise RuntimeError("Cannot build metadata extractor without DB connection")

        self.column_metadata_extractor = MetadataFactory.create_column_metadata_extractor(
            config=self.config.database,  # DB config cause the extractor type depends on the DB type
            db=self.db,
        )
        return self

    def build_table_metadata_enhancer(self):
        """Builds the table metadata enhancer"""
        if not self.llm:
            raise RuntimeError("Cannot build metadata enhancer without LLM handler")
        self.table_metadata_enhancer = MetadataFactory.create_table_metadata_enhancer(
            llm_handler=self.llm
        )
        return self

    def build_column_metadata_enhancer(self):
        """Builds the column metadata enhancer"""
        if not self.llm:
            raise RuntimeError("Cannot build metadata enhancer without LLM handler")
        self.column_metadata_enhancer = MetadataFactory.create_column_metadata_enhancer(
            llm_handler=self.llm
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
        self.build_table_metadata_extractor()
        self.build_column_metadata_extractor()
        self.build_table_metadata_enhancer()
        self.build_column_metadata_enhancer()
        self.build_cache()

        return AppComponents(
            db=self.db,
            vector_store=self.vector_store,
            sql_llm=self.llm,
            cache=self.cache,
            table_metadata_extractor=self.table_metadata_extractor,
            column_metadata_extractor=self.column_metadata_extractor,
            table_metadata_enhancer=self.table_metadata_enhancer,
            column_metadata_enhancer=self.column_metadata,
        )
