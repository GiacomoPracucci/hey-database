import os
import logging
import yaml
from typing import Dict, Any, Optional, List, Union, Callable
import importlib

from src.rag.recipe import RAGRecipe
from src.rag.recipe_registry import RAGRecipeRegistry
from src.rag.strategy import RAGStrategy
from src.rag.strategies.strategies import (
    QueryUnderstandingStrategy,
    RetrievalStrategy,
    ContextProcessingStrategy,
    PromptBuildingStrategy,
    LLMInteractionStrategy,
    ResponseProcessingStrategy,
)

logger = logging.getLogger("hey-database")


class RAGRecipeLoader:
    """
    Utility class for loading RAG recipes from configuration files.

    This class provides functionality to load recipe configurations from YAML files,
    validate them, and create RAGRecipe instances based on the configuration.
    It can load a single recipe or a directory of recipes, and optionally
    register them in a RAGRecipeRegistry.
    """

    # Maps strategy types to their respective abstract base classes
    STRATEGY_TYPE_MAP = {
        "query_understanding": QueryUnderstandingStrategy,
        "retrieval": RetrievalStrategy,
        "context_processing": ContextProcessingStrategy,
        "prompt_building": PromptBuildingStrategy,
        "llm_interaction": LLMInteractionStrategy,
        "response_processing": ResponseProcessingStrategy,
    }

    def __init__(
        self,
        dependencies: Optional[Dict[str, Any]] = None,
        strategy_modules: Optional[List[str]] = None,
    ):
        """
        Initialize the RAGRecipeLoader.

        Args:
            dependencies: Dictionary of dependencies to be injected into strategies
                         (e.g., db_connector, vector_store, llm_handler)
            strategy_modules: Additional Python modules to search for strategy implementations
        """
        self.dependencies = dependencies or {}

        # Default module paths to search for strategy implementations
        self.strategy_modules = strategy_modules or [
            "src.rag.strategies.query_understanding",
            "src.rag.strategies.retrieval",
            "src.rag.strategies.context_processing",
            "src.rag.strategies.prompt_building",
            "src.rag.strategies.llm_interaction",
            "src.rag.strategies.response_processing",
        ]

    def load_recipe(self, config_path: str) -> RAGRecipe:
        """
        Load a single recipe from a YAML configuration file.

        Args:
            config_path: Path to the YAML configuration file

        Returns:
            RAGRecipe: The initialized recipe

        Raises:
            ValueError: If the configuration is invalid
            FileNotFoundError: If the configuration file doesn't exist
        """
        logger.debug(f"Loading recipe from {config_path}")

        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"Recipe configuration file not found: {config_path}"
            )

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # Validate the recipe configuration at a high level
            self._validate_recipe_config(config)

            # Create the recipe from the configuration
            recipe = RAGRecipe.from_config(config, self._create_strategy_factory())

            logger.info(
                f"Successfully loaded recipe '{recipe.name}' from {config_path}"
            )
            return recipe

        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML from {config_path}: {str(e)}")
            raise ValueError(f"Invalid YAML in recipe configuration: {str(e)}")
        except Exception as e:
            logger.error(f"Error loading recipe from {config_path}: {str(e)}")
            raise

    def load_recipes_from_directory(self, directory_path: str) -> List[RAGRecipe]:
        """
        Load all recipe configurations from a directory.

        Args:
            directory_path: Path to the directory containing YAML recipe configurations

        Returns:
            List[RAGRecipe]: List of initialized recipes
        """
        logger.debug(f"Loading recipes from directory {directory_path}")

        if not os.path.exists(directory_path):
            logger.warning(f"Recipe directory not found: {directory_path}")
            return []

        recipes = []
        for filename in os.listdir(directory_path):
            if filename.endswith((".yaml", ".yml")):
                try:
                    file_path = os.path.join(directory_path, filename)
                    recipe = self.load_recipe(file_path)
                    recipes.append(recipe)
                except Exception as e:
                    logger.error(f"Error loading recipe from {filename}: {str(e)}")
                    # Continue loading other recipes even if one fails

        logger.info(f"Loaded {len(recipes)} recipes from {directory_path}")
        return recipes

    def load_and_register_recipes(
        self,
        config_path: Union[str, List[str]],
        registry: RAGRecipeRegistry,
        default_recipe_name: Optional[str] = None,
    ) -> None:
        """
        Load recipes and register them in a RAGRecipeRegistry.

        Args:
            config_path: Path to a recipe file, directory, or list of paths
            registry: Registry to register the loaded recipes in
            default_recipe_name: Name of the recipe to set as default
        """
        loaded_recipes = []

        # Load recipes from various sources
        if isinstance(config_path, list):
            for path in config_path:
                if os.path.isdir(path):
                    loaded_recipes.extend(self.load_recipes_from_directory(path))
                else:
                    loaded_recipes.append(self.load_recipe(path))
        elif os.path.isdir(config_path):
            loaded_recipes.extend(self.load_recipes_from_directory(config_path))
        else:
            loaded_recipes.append(self.load_recipe(config_path))

        # Register recipes
        for recipe in loaded_recipes:
            is_default = recipe.name == default_recipe_name
            registry.register_recipe(recipe, set_as_default=is_default)

        # If default_recipe_name was specified but not found, set the first recipe as default
        if default_recipe_name and not any(
            r.name == default_recipe_name for r in loaded_recipes
        ):
            logger.warning(
                f"Default recipe '{default_recipe_name}' not found. Using first loaded recipe as default."
            )
            if loaded_recipes:
                registry.set_default_recipe(loaded_recipes[0].name)

    def _validate_recipe_config(self, config: Dict[str, Any]) -> None:
        """
        Validate the recipe configuration.

        Args:
            config: Recipe configuration dictionary

        Raises:
            ValueError: If the configuration is invalid
        """
        # Check that the required fields are present
        if not isinstance(config, dict):
            raise ValueError("Recipe configuration must be a dictionary")

        if "name" not in config:
            raise ValueError("Recipe configuration must include a 'name'")

        if "description" not in config:
            raise ValueError("Recipe configuration must include a 'description'")

        # Check that all required strategy sections are present
        for strategy_type in self.STRATEGY_TYPE_MAP.keys():
            if strategy_type not in config:
                raise ValueError(
                    f"Recipe configuration must include a '{strategy_type}' section"
                )

            strategy_config = config[strategy_type]
            if not isinstance(strategy_config, dict):
                raise ValueError(f"'{strategy_type}' section must be a dictionary")

            if "type" not in strategy_config:
                raise ValueError(f"'{strategy_type}' section must include a 'type'")

    def _create_strategy_factory(self) -> Callable[[str, Dict[str, Any]], RAGStrategy]:
        """
        Create a factory function for creating strategy instances.

        Returns:
            A factory function that creates strategy instances based on type and configuration
        """

        def strategy_factory(
            strategy_type: str, strategy_config: Dict[str, Any]
        ) -> RAGStrategy:
            """
            Factory function for creating strategy instances.

            Args:
                strategy_type: Type of strategy to create (e.g., 'query_understanding')
                strategy_config: Configuration for the strategy

            Returns:
                An initialized strategy instance

            Raises:
                ValueError: If the strategy type or class is invalid
            """
            if strategy_type not in self.STRATEGY_TYPE_MAP:
                raise ValueError(f"Unknown strategy type: {strategy_type}")

            strategy_class_name = strategy_config["type"]
            strategy_base_class = self.STRATEGY_TYPE_MAP[strategy_type]

            # Find the strategy class in the registered modules
            strategy_class = None
            for module_name in self.strategy_modules:
                try:
                    module = importlib.import_module(module_name)
                    if hasattr(module, strategy_class_name):
                        strategy_class = getattr(module, strategy_class_name)
                        break
                except (ImportError, AttributeError):
                    continue

            if not strategy_class:
                raise ValueError(f"Strategy class not found: {strategy_class_name}")

            # Check that the strategy class is a subclass of the expected base class
            if not issubclass(strategy_class, strategy_base_class):
                raise ValueError(
                    f"{strategy_class_name} is not a {strategy_type} strategy"
                )

            # Create strategy instance with configuration and dependencies
            try:
                # Get strategy-specific parameters
                params = strategy_config.get("params", {})

                # Add any dependencies the strategy might need
                return strategy_class.from_config(params, **self.dependencies)
            except Exception as e:
                logger.error(f"Error creating strategy {strategy_class_name}: {str(e)}")
                raise ValueError(
                    f"Failed to create strategy {strategy_class_name}: {str(e)}"
                )

        return strategy_factory
