# RAG Recipe System Documentation

## Overview
The RAG (Retrieval Augmented Generation) Recipe system is a flexible framework for processing natural language queries, retrieving relevant context, and generating responses using LLMs. It's designed around the concept of "recipes" - configurable pipelines that define how a query is processed from start to finish.

## Core Components

### RAGRecipe
A RAGRecipe is a complete pipeline for processing a user query. It orchestrates the execution of various strategies in sequence to produce a response. Each recipe consists of:
- Name: A unique identifier for the recipe
- Description: A human-readable description of the recipe's purpose
- Strategies: Six specific strategies, each handling a different phase of processing

The six phases of a RAG recipe are:

- `Query Understanding`: Processing and potentially rewriting the user's query
- `Retrieval`: Fetching relevant information from the vector store or other sources
- `Context Processing`: Formatting and organizing the retrieved information
- `Prompt Building`: Constructing the prompt to send to the LLM
- `LLM Interaction`: Sending the prompt to the LLM and receiving a response
- `Response Processing`: Processing the LLM's response into a final, structured result

### RAGRecipeRegistry

The RAGRecipeRegistry is a centralized repository for managing and accessing RAG recipes. It provides the following functionality:
- Registration: Recipes can be registered with the registry via register_recipe()
- Retrieval: Recipes can be retrieved by name via get_recipe()
- Default Recipe: One recipe can be designated as the default, which is used when no specific recipe is requested
- Listing: All available recipes can be listed via list_recipes()

## Using the Recipe Registry

### Creating and Registering Recipes
```python 
# Create a registry
registry = RAGRecipeRegistry()

# Create a recipe using the builder
recipe = RAGRecipeBuilder("basic_rag", "Basic RAG with cosine similarity")
    .with_query_understanding(PassthroughQueryUnderstandingStrategy())
    .with_retrieval(CosineSimRetrievalStrategy(...))
    .with_context_processing(SimpleContextProcessor(...))
    .with_prompt_building(StandardPromptBuilder(...))
    .with_llm_interaction(DirectLLMInteractionStrategy(...))
    .with_response_processing(SQLResponseProcessor(...))
    .build()

# Register the recipe as the default
registry.register_recipe(recipe, set_as_default=True)

# Register additional recipes
registry.register_recipe(another_recipe)
```

### Using Recipes
```python 
# Get the default recipe
default_recipe = registry.get_recipe()

# Get a specific recipe
specific_recipe = registry.get_recipe("advanced_rag")

# Execute a recipe on a user query
response = default_recipe.execute("Show me sales by region for last quarter")

# The recipe handles all phases internally and returns the final response
```
### In the ChatService
The ChatService creates and manages a recipe registry internally:
```python 
def process_message(self, message: str, recipe_name: Optional[str] = None) -> Dict[str, Any]:
    """Process a user message and generate a response"""
    # Get the appropriate recipe (default if none specified)
    recipe = self.recipe_registry.get_recipe(recipe_name)
    
    # Execute the recipe
    response = recipe.execute(message)
    
    # Format and return the response
    return {
        "success": response.success,
        "query": response.query,
        # ... other fields
    }
```

## Current Implementation
In the current implementation, we create a default registry with a single "basic_rag" recipe, which uses:
- `PassthroughQueryUnderstandingStrategy`: Passes the query through unchanged
- `CosineSimRetrievalStrategy`: Retrieves relevant tables, columns, and queries using cosine similarity
- `SimpleContextProcessor`: Formats the retrieved information into a readable context
- `StandardPromptBuilder`: Builds a prompt that requests a structured JSON response
- `DirectLLMInteractionStrategy`: Sends the prompt directly to the LLM
- `SQLResponseProcessor`: Extracts SQL and explanation from the LLM response, executes the SQL, and returns results

This recipe is registered as the default and used automatically when processing messages through the ChatService.

## Extending with New Recipes
To add new recipes:
- Create new strategy implementations for any phases you want to customize
- Use the RAGRecipeBuilder to create a new recipe with your strategies
- Register the recipe with the registry

For example, to create an "advanced_rag" recipe that uses query rewriting:

```python 
# Create a new recipe with a query rewriting strategy
advanced_recipe = RAGRecipeBuilder("advanced_rag", "Advanced RAG with query rewriting")
    .with_query_understanding(QueryRewritingStrategy(...))
    # ... other strategies
    .build()

# Register the recipe
registry.register_recipe(advanced_recipe)
```

Users can then specify this recipe when calling the API:
```python 
POST /api/chat
{
    "message": "How many sales in Q1?",
    "recipe_name": "advanced_rag"
}
```
If no recipe name is provided, the default recipe is used.

