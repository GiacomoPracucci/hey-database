import logging
from typing import Dict, List, Optional

from src.rag.recipe import RAGRecipe

logger = logging.getLogger("hey-database")


class RAGRecipeRegistry:
    """
    Registry for managing and accessing RAG recipes.

    This class provides a central repository for all available RAG recipes,
    allowing them to be registered, retrieved, and listed. It ensures that
    recipe names are unique and provides a default recipe that can be used
    when no specific recipe is requested.
    """

    def __init__(self):
        """Initialize an empty recipe registry."""
        self._recipes: Dict[str, RAGRecipe] = {}
        self._default_recipe_name: Optional[str] = None

    def register_recipe(self, recipe: RAGRecipe, set_as_default: bool = False) -> None:
        """
        Register a RAG recipe in the registry.

        Args:
            recipe: The recipe to register
            set_as_default: Whether to set this recipe as the default

        Raises:
            ValueError: If a recipe with the same name already exists
        """
        if recipe.name in self._recipes:
            raise ValueError(f"Recipe with name '{recipe.name}' already exists")

        self._recipes[recipe.name] = recipe
        logger.info(f"Registered RAG recipe: {recipe.name}")

        if set_as_default or self._default_recipe_name is None:
            self._default_recipe_name = recipe.name
            logger.info(f"Set default RAG recipe to: {recipe.name}")

    def get_recipe(self, name: Optional[str] = None) -> RAGRecipe:
        """
        Get a RAG recipe by name or the default recipe if no name is provided.

        Args:
            name: Name of the recipe to retrieve, or None for default

        Returns:
            The requested RAG recipe

        Raises:
            ValueError: If the requested recipe does not exist or no default recipe is set
        """
        if name is None:
            if self._default_recipe_name is None:
                raise ValueError("No default recipe set")
            return self._recipes[self._default_recipe_name]

        if name not in self._recipes:
            raise ValueError(f"Recipe with name '{name}' not found")

        return self._recipes[name]

    def list_recipes(self) -> List[Dict[str, str]]:
        """
        List all registered recipes.

        Returns:
            List of dictionaries containing name and description of each recipe,
            with the default recipe marked
        """
        return [
            {
                "name": recipe.name,
                "description": recipe.description,
                "is_default": recipe.name == self._default_recipe_name,
            }
            for recipe in self._recipes.values()
        ]

    def has_recipe(self, name: str) -> bool:
        """
        Check if a recipe with the given name exists.

        Args:
            name: Name of the recipe to check

        Returns:
            True if the recipe exists, False otherwise
        """
        return name in self._recipes

    def set_default_recipe(self, name: str) -> None:
        """
        Set the default recipe.

        Args:
            name: Name of the recipe to set as default

        Raises:
            ValueError: If the recipe does not exist
        """
        if name not in self._recipes:
            raise ValueError(f"Recipe with name '{name}' not found")

        self._default_recipe_name = name
        logger.info(f"Set default RAG recipe to: {name}")

    def get_default_recipe_name(self) -> Optional[str]:
        """
        Get the name of the default recipe.

        Returns:
            Name of the default recipe, or None if no default is set
        """
        return self._default_recipe_name
