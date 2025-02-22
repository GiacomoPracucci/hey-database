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
        self.vector_store_writer = None
        self.vector_store_searcher = None
        self.sql_llm = None
        self.cache = None
        self.table_metadata_extractor = None
        self.column_metadata_extractor = None
        self.table_metadata_enhancer = None
        self.column_metadata_enhancer = None

    def build_database(self):
        """Costruisce e verifica la connessione database"""
        self.db = DatabaseFactory.create_connector(self.config.database)
        return self

    def build_vector_store(self):
        """
        Build and initialize the vector store ecosystem including store, writer, and searcher.
        Returns the builder instance for method chaining.
        """
        logger.info("Initializing vector store components...")

        if not self.config.vector_store.enabled:
            logger.info("Vector store disabled, skipping initialization")
            return self

        try:
            # create all vector store components using unified factory
            vector_components = VectorStoreFactory.create(self.config.vector_store)

            # assign components to builder
            self.vector_store = vector_components.store
            self.vector_store_writer = vector_components.writer
            self.vector_store_searcher = vector_components.search

            logger.info("Vector store components initialized successfully")
            return self

        except Exception as e:
            logger.error(f"Failed to initialize vector store components: {str(e)}")
            raise

    def build_sql_llm(self):
        """Costruisce l'handler LLM"""
        self.llm = LLMFactory.create_handler(self.config.sql_llm)
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
        """Build and return the initialized application components"""

        self.build_database()
        self.build_vector_store()  # Now builds all vector store components
        self.build_sql_llm()
        self.build_cache()
        self.build_table_metadata_extractor()
        self.build_column_metadata_extractor()
        self.build_table_metadata_enhancer()
        self.build_column_metadata_enhancer()

        return AppComponents(
            db=self.db,
            vector_store=self.vector_store,
            vector_store_writer=self.vector_store_writer,
            vector_store_searcher=self.vector_store_searcher,
            sql_llm=self.llm,
            cache=self.cache,
            table_metadata_extractor=self.table_metadata_extractor,
            column_metadata_extractor=self.column_metadata_extractor,
            table_metadata_enhancer=self.table_metadata_enhancer,
            column_metadata_enhancer=self.column_metadata_enhancer,
        )
