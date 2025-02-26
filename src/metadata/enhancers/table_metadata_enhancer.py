from typing import Optional
import logging

from src.models.metadata import TableMetadata, BaseTableMetadata
from src.llm_handler.llm_handler import LLMHandler
from src.keywords.YAKE_keywords_finder import YAKEKeywordsFinder

logger = logging.getLogger("hey-database")


class TableMetadataEnhancer:
    """
    Enhancer responsible for enriching database table metadata.

    This class takes base table metadata extracted from the database schema
    and enhances it with AI-generated descriptions and semantic analysis, including:
    - Natural language descriptions generated via LLM
    - Keywords extracted from the description for improved semantic search
    - Importance score calculation based on table structure and relationships

    The enhancer provides a bridge between raw database schema information and
    semantically rich metadata that can be used for search, visualization, and
    natural language interfaces.
    """

    def __init__(self, llm_handler: LLMHandler):
        """
        Initialize the table metadata enhancer.

        Args:
            llm_handler: Handler for large language model operations,
                        used to generate semantic descriptions
        """
        # We could use the LLM-based finder which is more robust, but it would slow down the already slow process
        self.keywords_finder = YAKEKeywordsFinder()
        # TODO: Consider using LLM-based extractor for table keywords
        # TODO: Since tables are fewer than columns, we could adapt the query-focused prompt for description input
        self.llm_handler = llm_handler

    def enhance(self, base_metadata: BaseTableMetadata) -> TableMetadata:
        """
        Enrich table metadata with AI-generated descriptions and keywords.

        This method takes the base metadata extracted from the database schema
        and enhances it with semantic descriptions, keywords, and importance scores
        to make it more useful for search and natural language interactions.

        Args:
            base_metadata: Base table metadata extracted from database schema

        Returns:
            TableMetadata: Enhanced table metadata with descriptions, keywords, and importance score
        """
        try:
            # In production, uncomment the following line to use real LLM-generated descriptions
            # description = self._generate_description(base_metadata)
            description = "placeholder"

            if not description:
                return TableMetadata.from_base_metadata(
                    base=base_metadata,
                    description="No description available",
                    keywords=[],
                    importance_score=0.0,
                )

            keywords_response = self.keywords_finder.find_keywords(description)
            if not keywords_response.success:
                return TableMetadata.from_base_metadata(
                    base=base_metadata,
                    description=description,
                    keywords=[],
                    importance_score=0.0,
                )

            importance_score = self._calculate_importance_score(base_metadata)

            return TableMetadata.from_base_metadata(
                base=base_metadata,
                description=description,
                keywords=keywords_response.keywords,
                importance_score=importance_score,
            )

        except Exception as e:
            logger.exception(f"Error enhancing table metadata: {str(e)}")
            return TableMetadata.from_base_metadata(
                base=base_metadata,
                description="Error enhancing metadata",
                keywords=[],
                importance_score=0.0,
            )

    def _generate_description(self, metadata: BaseTableMetadata) -> Optional[str]:
        """
        Generate a semantic description of the table using the LLM.

        Uses a carefully constructed prompt to guide the LLM in generating
        a concise, accurate, and semantically meaningful description of the table
        based on its name, columns, keys, and relationships.

        Args:
            metadata: Base metadata about the table

        Returns:
            str: Generated description, or None if generation failed
        """
        prompt = self.build_prompt(metadata)

        description = self.llm_handler.get_completion(
            prompt=prompt,
            system_prompt="You are a database expert providing concise table descriptions.",
            temperature=0.1,
        )

        return description.strip() if description else None

    def build_prompt(self, metadata: BaseTableMetadata) -> str:
        """
        Build the prompt for generating the table description.

        Constructs a detailed prompt that provides the LLM with context about
        the table, including its name, columns, primary keys, and foreign key relationships.
        The prompt includes examples and guidance to ensure high-quality descriptions.

        Args:
            metadata: Base metadata about the table

        Returns:
            str: Complete prompt for LLM description generation
        """
        foreign_keys_info = []
        for fk in metadata.foreign_keys:
            from_cols = ", ".join(fk["constrained_columns"])
            to_table = fk["referred_table"]
            to_cols = ", ".join(fk["referred_columns"])
            foreign_keys_info.append(f"- {from_cols} -> {to_table}({to_cols})")

        prompt = f"""Describe the business meaning of the data contained in this database table.

Table: {metadata.name}
Number of records: {metadata.row_count}

Columns:
{metadata.columns}

Primary Keys: {", ".join(metadata.primary_keys)}

Foreign Keys:
{chr(10).join(foreign_keys_info) if foreign_keys_info else "No foreign keys"}

The description should focus on the semantic meaning of the data, not on technical or relational aspects.
Examples of effective descriptions:
Table: customers -> "Contains customer demographic and contact data, including residence information and communication preferences"
Table: orders -> "Stores all customer orders, with details on amounts, purchase dates, and processing status"
Table: products -> "Repository of products for sale with their technical specifications, prices, and warehouse availability"

Do not include reasoning, hypotheses, or assumptions in the description. Describe ONLY what is objectively present in the provided data/metadata.
The description must be clear and concise."""

        return prompt

    def _calculate_importance_score(self, metadata: BaseTableMetadata) -> float:
        """
        Calculate an importance score for the table based on its structure.

        Assigns a normalized score (0.0-1.0) based on the table's characteristics
        such as number of relationships, columns, and presence of primary keys.
        Tables with more relationships and columns, and those that act as primary
        entities (having primary keys) are considered more important in the schema.

        Args:
            metadata: Base metadata about the table

        Returns:
            float: Normalized importance score between 0.0 and 1.0
        """
        score = 0.0

        # Weight for relationships - tables with more relationships are more central
        relations_weight = len(metadata.foreign_keys) * 0.2

        # Weight for columns - tables with more columns contain more information
        columns_weight = len(metadata.columns) * 0.1

        # Weight for primary keys - tables with primary keys are often key entities
        pk_weight = 0.3 if metadata.primary_keys else 0

        # Normalize and combine scores
        score = min(1.0, relations_weight + columns_weight + pk_weight)

        return round(score, 2)
