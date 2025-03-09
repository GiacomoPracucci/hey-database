from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from src.rag.recipe import RAGRecipe


@dataclass
class StrategyConfig:
    """Configurazione per una singola strategia in una recipe RAG"""

    type: str
    params: Dict[str, Any]


@dataclass
class RecipeConfig:
    """Configurazione completa per una singola recipe RAG"""

    name: str
    description: str
    default: bool
    query_understanding: StrategyConfig
    retrieval: StrategyConfig
    context_processing: StrategyConfig
    prompt_building: StrategyConfig
    llm_interaction: StrategyConfig
    response_processing: StrategyConfig


@dataclass
class RecipesCollection:
    """Collezione di tutte le recipes RAG disponibili"""

    recipes: Dict[str, RAGRecipe]
    default_recipe_name: Optional[str] = None

    def get_recipe(self, name: Optional[str] = None) -> RAGRecipe:
        """Ottiene una recipe per nome o la recipe predefinita"""
        if name is None:
            if self.default_recipe_name is None:
                raise ValueError("Nessuna recipe predefinita impostata")
            return self.recipes[self.default_recipe_name]

        if name not in self.recipes:
            raise ValueError(f"Recipe '{name}' non trovata")

        return self.recipes[name]

    def list_recipes(self) -> List[Dict[str, Any]]:
        """Elenca tutte le recipes disponibili con i loro dettagli"""
        return [
            {
                "name": name,
                "description": recipe.description,
                "is_default": name == self.default_recipe_name,
            }
            for name, recipe in self.recipes.items()
        ]
