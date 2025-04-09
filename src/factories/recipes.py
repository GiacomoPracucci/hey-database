import logging
import importlib
from typing import Dict, Any, List

from src.models.recipes import RecipeConfig, RecipesCollection
from src.rag.recipe import RAGRecipe
from src.rag.recipe_builder import RAGRecipeBuilder
from src.rag.strategy import RAGStrategy

logger = logging.getLogger("hey-database")


class RecipeFactory:
    """
    Factory for creating RAG recipes from configurations.

    This class handles the instantiation of RAG recipes by creating and
    configuring their component strategies based on provided configurations.
    It manages the dependencies injection and ensures proper initialization
    of all recipe components.
    """

    def __init__(self, dependencies: Dict[str, Any]):
        """
        Initialize the factory with necessary dependencies.

        Args:
            dependencies: Dictionary of dependencies needed by the strategies,
                        such as database connectors, vector stores, and LLM handlers
        """
        self.dependencies = dependencies
        
        if "schema" not in self.dependencies and "db_connector" in self.dependencies:
            db = self.dependencies["db_connector"]
            if hasattr(db, "schema"):
                self.dependencies["schema"] = db.schema

        self.strategy_modules = [
            "src.rag.strategies.query_understanding.passthrough",
            "src.rag.strategies.retrieval.cosine_sim",
            "src.rag.strategies.context_processing.simple",
            "src.rag.strategies.prompt_building.standard",
            "src.rag.strategies.llm_interaction.direct",
            "src.rag.strategies.response_processing.sql_processor",
        ]

    def create_recipes_collection(
        self, configs: List[RecipeConfig]
    ) -> RecipesCollection:
        """
        Create a collection of recipes from configurations.

        Args:
            configs: List of recipe configurations

        Returns:
            RecipesCollection containing all successfully created recipes
        """
        recipes = {}
        default_recipe_name = None

        for config in configs:
            try:
                recipe = self.create_recipe(config)
                recipes[config.name] = recipe

                # Imposta la recipe di default se necessario
                if config.default and default_recipe_name is None:
                    default_recipe_name = config.name
                    logger.info(f"Impostata recipe di default: {config.name}")
            except Exception as e:
                logger.error(
                    f"Errore nella creazione della recipe {config.name}: {str(e)}"
                )

        # Se nessuna recipe è impostata come default ma ne abbiamo almeno una, usa la prima
        if default_recipe_name is None and recipes:
            default_recipe_name = next(iter(recipes.keys()))
            logger.warning(
                f"Nessuna recipe di default specificata. Utilizzo {default_recipe_name} come default."
            )

        return RecipesCollection(
            recipes=recipes, default_recipe_name=default_recipe_name
        )

    def create_recipe(self, config: RecipeConfig) -> RAGRecipe:
        """
        Create a single recipe from its configuration.

        Args:
            config: Configuration for the recipe

        Returns:
            Initialized RAGRecipe instance with all required strategies

        Raises:
            ValueError: If recipe creation fails
        """
        logger.debug(f"Creazione recipe: {config.name}")

        # Crea un builder per la recipe
        builder = RAGRecipeBuilder(name=config.name, description=config.description)

        # Aggiungi ciascuna strategia al builder
        builder.with_query_understanding(
            self._create_strategy(
                "query_understanding",
                config.query_understanding.type,
                config.query_understanding.params,
            )
        )

        builder.with_retrieval(
            self._create_strategy(
                "retrieval", config.retrieval.type, config.retrieval.params
            )
        )

        builder.with_context_processing(
            self._create_strategy(
                "context_processing",
                config.context_processing.type,
                config.context_processing.params,
            )
        )

        builder.with_prompt_building(
            self._create_strategy(
                "prompt_building",
                config.prompt_building.type,
                config.prompt_building.params,
            )
        )

        builder.with_llm_interaction(
            self._create_strategy(
                "llm_interaction",
                config.llm_interaction.type,
                config.llm_interaction.params,
            )
        )

        builder.with_response_processing(
            self._create_strategy(
                "response_processing",
                config.response_processing.type,
                config.response_processing.params,
            )
        )

        # Costruisci e restituisci la recipe completa
        return builder.build()

    def _create_strategy(
        self, class_name: str, params: Dict[str, Any]
    ) -> RAGStrategy:
        """
        Create a strategy instance from its class name and parameters.

        Args:
            strategy_type: Type of strategy (e.g., "query_understanding")
            class_name: Name of the strategy class
            params: Configuration parameters for the strategy

        Returns:
            Initialized strategy instance

        Raises:
            ValueError: If strategy class is not found or initialization fails
        """
        # Cerca la classe della strategia nei moduli registrati
        strategy_class = None
        for module_name in self.strategy_modules:
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, class_name):
                    strategy_class = getattr(module, class_name)
                    break
            except (ImportError, AttributeError):
                continue

        if not strategy_class:
            raise ValueError(f"Classe strategia non trovata: {class_name}")

        # Crea l'istanza della strategia con i parametri e le dipendenze
        try:
            if hasattr(strategy_class, "from_config"):
                return strategy_class.from_config(params, **self.dependencies)
            else:
                # Fallback per strategie che non supportano from_config
                return strategy_class(**params)
        except Exception as e:
            logger.error(
                f"Errore nella creazione della strategia {class_name}: {str(e)}"
            )
            raise ValueError(f"Impossibile creare la strategia {class_name}: {str(e)}")
