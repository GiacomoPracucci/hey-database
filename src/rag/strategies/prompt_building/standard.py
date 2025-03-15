import logging
from typing import Dict, Any, Optional
from string import Template

from src.rag.utils import get_config_value
from src.rag.models import RAGContext
from src.rag.strategies.strategies import PromptBuildingStrategy

logger = logging.getLogger("hey-database")


class StandardPromptBuilder(PromptBuildingStrategy):
    """
    A standard prompt building strategy using string templates.

    This strategy constructs prompts for the LLM using configurable templates,
    inserting the retrieved context and user query into appropriate places
    in the template.
    """

    # Default template for SQL generation
    DEFAULT_TEMPLATE = """
    You are an SQL expert who helps convert natural language queries into SQL queries.
    
    Your task is to translate the following question into a valid SQL query.
    
    ${context}
    
    Question: ${query}
    
    You must respond with a JSON object in the following format:
    {
        "query": "YOUR SQL QUERY HERE",
        "explanation": "Brief explanation of what the query does and what results to expect"
    }
    
    Important:
    - Always insert schema name "${schema}" before the tables
    - Do not include comments in the SQL query
    - The query must be executable
    - Use the provided context information to ensure correct column names and types
    - Follow the foreign key relationships when joining tables
    - If you do not have the necessary information to respond or if the requested data does not appear to be in the DB:
        - Explain in the explanation field why the request cannot be fulfilled
        - Generate a simple SQL query to extract generic data from a single table (with a LIMIT 5)
        - Explain what the sample data shows
    
    Response must be valid JSON - do not include any other text or markdown formatting.
    """

    def __init__(
        self, schema: str, template: Optional[str] = None, include_original_query: bool = True
    ):
        """
        Initialize the prompt builder with a custom template.

        Args:
            schema: Database schema name to use in SQL queries
            template: Custom template string (optional, uses default if None)
            include_original_query: Whether to use the original query in the prompt
                                   (if False, uses processed_query)
        """
        self.schema = schema
        self.template = template or self.DEFAULT_TEMPLATE
        self.include_original_query = include_original_query

    def execute(self, context: RAGContext) -> RAGContext:
        """
        Build a prompt by filling in the template with context and query.

        Args:
            context: The RAG context containing processed_context and query

        Returns:
            The updated RAG context with final_prompt set
        """
        logger.debug("Building prompt from template")
        context.add_metadata("prompt_building_strategy", "standard_template")

        # Decide which query to use
        query = (
            context.original_query
            if self.include_original_query
            else (context.processed_query or context.original_query)
        )

        # Create a template and substitute values
        template = Template(self.template)

        # Build the prompt with context if available
        context_str = context.processed_context or "No relevant context available."

        prompt = template.safe_substitute(context=context_str, query=query, schema=self.schema)

        # Set the final prompt in the context
        context.final_prompt = prompt

        logger.debug("Prompt built successfully")
        return context

    @classmethod
    def from_config(
        cls, config: Dict[str, Any], **dependencies
    ) -> "StandardPromptBuilder":
        """
        Create a StandardPromptBuilder from a configuration dictionary.

        Args:
            config: Configuration dictionary with builder parameters
            **dependencies: Additional dependencies (not used by this strategy)

        Returns:
            An initialized StandardPromptBuilder
        """
        template = StandardPromptBuilder._get_template_from_config(config)
        schema = StandardPromptBuilder._get_schema_from_config(dependencies)

        return cls(
            schema=schema,
            template=template,
            include_original_query=get_config_value(
                config, "include_original_query", True, value_type=bool
            ),
        )

    @staticmethod   
    def _get_schema_from_config(dependencies: Dict[str, Any]) -> str:
        """
        Get the schema name from the dependencies.

        Args:
            dependencies: A dictionary of dependencies

        Returns:
            The schema name
        """
        schema = dependencies.get("schema")
        if not schema and "db_connector" in dependencies:
            schema = dependencies["db_connector"].schema

        if not schema:
            raise ValueError("Database schema name not provided for prompt building")
        
        return schema
        
    @staticmethod
    def _get_template_from_config(config: Dict[str, Any]) -> Optional[str]:
        """
        Get the template string from the configuration.

        Args:
            config: Configuration dictionary

        Returns:
            The template string, or None if not provided
        """
        template = None
        template_file = get_config_value(config, "template_file", None)

        if template_file:
            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    template = f.read()
                logger.debug(f"Loaded prompt template from {template_file}")
            except Exception as e:
                logger.error(f"Failed to load template from {template_file}: {str(e)}")
                # Fall back to inline template or default

        # Use inline template if provided and file loading failed or wasn't attempted
        if template is None:
            template = get_config_value(config, "template", None)
        
        return template