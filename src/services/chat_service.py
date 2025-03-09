import logging
from typing import Optional, Dict, Any

from src.store.vectorstore_client import VectorStore
from src.models.recipes import RecipesCollection

logger = logging.getLogger("hey-database")


class ChatService:
    """
    Service for processing user chat messages and generating SQL responses.

    This service uses the RAG (Retrieval Augmented Generation) system to:
    1. Retrieve relevant database schema information
    2. Generate SQL queries based on natural language questions
    3. Execute the generated queries and return the results

    The service delegates the processing to RAG recipes from a registry.
    """

    def __init__(
        self,
        recipes_collection: RecipesCollection,
        vector_store: Optional[VectorStore] = None,
    ):
        """
        Initialize the chat service with required components.

        Args:
            recipes-collectiom: Lists of RAG recipes to use for processing messages
            vector_store: Optional vector store for handling feedback
        """
        self.vector_store = vector_store
        self.recipes_collection = recipes_collection

    def process_message(
        self, message: str, recipe_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a SQL response.

        Args:
            message: The user's natural language question
            recipe_name: Optional name of the RAG recipe to use (uses default if None)

        Returns:
            Dictionary containing the response with SQL query, explanation, and results
        """
        try:
            logger.debug(f"Processing message: '{message}'")

            # Get the appropriate recipe
            recipe = self.recipes_collection.get_recipe(recipe_name)
            logger.debug(f"Using RAG recipe: {recipe.name}")

            # Execute the RAG recipe
            response = recipe.execute(message)

            # Return formatted response for API consumption
            return {
                "success": response.success,
                "query": response.query,
                "explanation": response.explanation,
                "results": response.results,
                "preview": response.preview,
                "error": response.error,
                "from_vector_store": response.from_vector_store,
                "original_question": response.original_question,
            }

        except Exception as e:
            logger.exception(f"Error processing message: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to process message: {str(e)}",
                "original_question": message,
            }

    def handle_feedback(self, question: str, sql_query: str, explanation: str) -> bool:
        """
        Handle positive user feedback for a question-answer pair.

        This method stores the feedback in the vector store for future retrieval.
        When users mark a response as helpful, it gets stored and can be used for
        similar questions in the future.

        Args:
            question: The user's original question
            sql_query: The SQL query that was generated
            explanation: The explanation of the query

        Returns:
            bool: True if feedback was successfully handled, False otherwise
        """
        try:
            if not self.vector_store:
                logger.warning("Cannot handle feedback: no vector store available")
                return False

            logger.debug(f"Handling positive feedback for question: '{question}'")
            return self.vector_store.handle_positive_feedback(
                question=question, sql_query=sql_query, explanation=explanation
            )

        except Exception as e:
            logger.exception(f"Error handling feedback: {str(e)}")
            return False
