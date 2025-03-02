import logging
from src.models.app import AppConfig, AppComponents
from src.factories.database import DatabaseFactory
from src.factories.metadata import MetadataFactory
from src.factories.vector_store import VectorStoreFactory
from src.factories.llm import LLMFactory
from src.factories.cache import CacheFactory
from src.rag.recipe_loader import RAGRecipeLoader

from src.rag.recipe_registry import RAGRecipeRegistry
from src.rag.recipe_builder import RAGRecipeBuilder
from src.rag.strategies import (
    PassthroughQueryUnderstandingStrategy,
    CosineSimRetrievalStrategy,
    SimpleContextProcessor,
    StandardPromptBuilder,
    DirectLLMInteractionStrategy,
    SQLResponseProcessor,
)

logger = logging.getLogger("hey-database")


class AppComponentsBuilder:
    """
    Builder class responsible for constructing and initializing all application components.

    This class manages the creation and configuration of various system components including:
    - Database connections
    - Vector store ecosystem (store, writer, searcher)
    - LLM handlers
    - Metadata extractors and enhancers
    - Caching system

    The builder ensures proper initialization order and dependency management
    between components, following the Builder pattern for complex object construction.
    """

    def __init__(self, app_config: AppConfig):
        """
        Initialize the builder with application configuration.

        Args:
            app_config: Configuration object containing all necessary settings
                      for component initialization
        """
        self.config = app_config

        # Database component
        self.db = None

        # Vector store components
        self.vector_store = None
        self.vector_store_writer = None
        self.vector_store_searcher = None

        # LLM component
        self.sql_llm = None

        # Cache component
        self.cache = None

        # Metadata components
        self.table_metadata_extractor = None
        self.column_metadata_extractor = None
        self.table_metadata_enhancer = None
        self.column_metadata_enhancer = None

        self.recipe_registry = None

    def build_database(self):
        """
        Build and verify database connection.

        Creates a database connector based on configuration and ensures
        the connection is working properly.

        Returns:
            self: Builder instance for method chaining

        Raises:
            RuntimeError: If database connection fails
        """
        self.db = DatabaseFactory.create_connector(self.config.database)
        return self

    def build_vector_store(self):
        """
        Build and initialize the vector store ecosystem.

        Creates and configures the vector store components including:
        - Main vector store
        - Vector store writer
        - Vector store searcher

        The method handles both enabled and disabled vector store scenarios.

        Returns:
            self: Builder instance for method chaining

        Raises:
            RuntimeError: If vector store initialization fails while enabled
        """
        logger.info("Initializing vector store components...")

        try:
            # Create all vector store components using factory
            vector_components = VectorStoreFactory.create(self.config.vector_store)

            self.vector_store = vector_components.store
            self.vector_store_writer = vector_components.writer
            self.vector_store_searcher = vector_components.search

            logger.info("Vector store components initialized successfully")
            return self

        except Exception as e:
            logger.error(f"Failed to initialize vector store components: {str(e)}")
            raise

    def build_sql_llm(self):
        """
        Build the SQL LLM handler.

        Creates and configures the language model handler used for
        SQL-related operations.

        Returns:
            self: Builder instance for method chaining

        Raises:
            RuntimeError: If LLM initialization fails
        """
        self.sql_llm = LLMFactory.create_handler(self.config.sql_llm)
        return self

    def build_table_metadata_extractor(self):
        """
        Build the table metadata extractor.

        Creates the component responsible for extracting metadata from database tables.
        Requires an active database connection.

        Returns:
            self: Builder instance for method chaining

        Raises:
            RuntimeError: If database connection is not available
        """
        if not self.db:
            raise RuntimeError("Cannot build metadata extractor without DB connection")

        self.table_metadata_extractor = MetadataFactory.create_table_metadata_extractor(
            config=self.config.database,
            db=self.db,
        )
        return self

    def build_column_metadata_extractor(self):
        """
        Build the column metadata extractor.

        Creates the component responsible for extracting metadata from database columns.
        Requires an active database connection.

        Returns:
            self: Builder instance for method chaining

        Raises:
            RuntimeError: If database connection is not available
        """
        if not self.db:
            raise RuntimeError("Cannot build metadata extractor without DB connection")

        self.column_metadata_extractor = (
            MetadataFactory.create_column_metadata_extractor(
                config=self.config.database,
                db=self.db,
            )
        )
        return self

    def build_table_metadata_enhancer(self):
        """
        Build the table metadata enhancer.

        Creates the component responsible for enhancing table metadata using LLM.
        Requires an initialized LLM handler.

        Returns:
            self: Builder instance for method chaining

        Raises:
            RuntimeError: If LLM handler is not available
        """
        if not self.sql_llm:
            raise RuntimeError("Cannot build metadata enhancer without LLM handler")

        self.table_metadata_enhancer = MetadataFactory.create_table_metadata_enhancer(
            llm_handler=self.sql_llm
        )
        return self

    def build_column_metadata_enhancer(self):
        """
        Build the column metadata enhancer.

        Creates the component responsible for enhancing column metadata using LLM.
        Requires an initialized LLM handler.

        Returns:
            self: Builder instance for method chaining

        Raises:
            RuntimeError: If LLM handler is not available
        """
        if not self.sql_llm:
            raise RuntimeError("Cannot build metadata enhancer without LLM handler")

        self.column_metadata_enhancer = MetadataFactory.create_column_metadata_enhancer(
            llm_handler=self.sql_llm
        )
        return self

    def build_cache(self):
        """
        Build the metadata cache component.

        Creates and configures the caching system for metadata storage.

        Returns:
            self: Builder instance for method chaining
        """
        self.cache = CacheFactory.create_cache(self.config.cache)
        return self

    def build_recipe_registry(self):
        """
        Build and initialize the RAG recipe registry.

        Creates a registry and populates it with the default RAG recipes.

        Returns:
            self: Builder instance for method chaining

        Raises:
            RuntimeError: If required dependencies are not available
        """
        if not self.sql_llm:
            raise RuntimeError("Cannot build recipe registry without LLM handler")
        if not self.vector_store_searcher:
            raise RuntimeError(
                "Cannot build recipe registry without vector store searcher"
            )
        if not self.db:
            raise RuntimeError(
                "Cannot build recipe registry without database connector"
            )

        logger.info("Initializing RAG recipe registry")

        # Create recipe registry
        self.recipe_registry = RAGRecipeRegistry()

        # Create basic RAG recipe
        basic_recipe = (
            RAGRecipeBuilder(
                "basic_rag", "Basic RAG recipe with cosine similarity retrieval"
            )
            .with_query_understanding(PassthroughQueryUnderstandingStrategy())
            .with_retrieval(
                CosineSimRetrievalStrategy(
                    vector_store_search=self.vector_store_searcher,
                    tables_limit=3,
                    columns_limit=5,
                    queries_limit=2,
                )
            )
            .with_context_processing(
                SimpleContextProcessor(
                    include_table_descriptions=True,
                    include_column_descriptions=True,
                    include_sample_queries=True,
                )
            )
            .with_prompt_building(StandardPromptBuilder())
            .with_llm_interaction(
                DirectLLMInteractionStrategy(
                    llm_handler=self.sql_llm,
                    system_prompt="You are a SQL expert. Generate valid, executable SQL queries based on the user's question and database schema information.",
                )
            )
            .with_response_processing(
                SQLResponseProcessor(
                    db=self.db, max_preview_rows=10, execute_query=True
                )
            )
            .build()
        )

        # Register the basic recipe as default
        self.recipe_registry.register_recipe(basic_recipe, set_as_default=True)

        # TODO: In future, we could load additional recipes from config files
        # recipe_loader = RAGRecipeLoader(dependencies={...})
        # recipe_loader.load_and_register_recipes(config_path, self.recipe_registry)

        logger.info(f"Registered default RAG recipe: {basic_recipe.name}")
        return self

    def build(self) -> AppComponents:
        """
        Build and return the complete application components.

        Executes the complete build process in the correct order,
        ensuring all dependencies are properly initialized.

        Returns:
            AppComponents: Fully initialized application components

        Raises:
            RuntimeError: If any component initialization fails
        """
        self.build_database()
        self.build_vector_store()
        self.build_sql_llm()
        self.build_cache()
        self.build_table_metadata_extractor()
        self.build_column_metadata_extractor()
        self.build_table_metadata_enhancer()
        self.build_column_metadata_enhancer()
        self.build_recipe_registry()

        return AppComponents(
            db=self.db,
            vector_store=self.vector_store,
            vector_store_writer=self.vector_store_writer,
            vector_store_searcher=self.vector_store_searcher,
            sql_llm=self.sql_llm,
            cache=self.cache,
            table_metadata_extractor=self.table_metadata_extractor,
            column_metadata_extractor=self.column_metadata_extractor,
            table_metadata_enhancer=self.table_metadata_enhancer,
            column_metadata_enhancer=self.column_metadata_enhancer,
            recipe_registry=self.recipe_registry,
        )
