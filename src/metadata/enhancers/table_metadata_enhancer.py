from typing import Optional
import logging

from src.models.metadata import TableMetadata, EnhancedTableMetadata
from src.llm_handler.llm_handler import LLMHandler
from src.keywords.YAKE_keywords_finder import YAKEKeywordsFinder

logger = logging.getLogger("hey-database")


class TableMetadataEnhancer:
    """
    Enhancer responsible for enriching table metadata with:
    - Semantic description generated via LLM
    - Keywords extracted from the description
    - Calculated importance score
    """

    def __init__(self, llm_handler: LLMHandler):
        # We could use the LLM-based finder which is more robust, but it would slow down the already slow process
        self.keywords_finder = YAKEKeywordsFinder()
        # TODO: Consider using LLM-based extractor for table keywords
        # TODO: Since tables are fewer than columns, we could adapt the query-focused prompt for description input
        self.llm_handler = llm_handler

    def enhance(self, base_metadata: TableMetadata) -> EnhancedTableMetadata:
        """
        Enriches the metadata of a database table

        Args:
            base_metadata: Base metadata of the table

        Returns:
            EnhancedTableMetadata containing the enriched metadata or error information
        """
        try:
            # description = self._generate_description(base_metadata)
            description = "placeholder"

            if not description:
                return EnhancedTableMetadata(
                    base_metadata=base_metadata,
                    description="No description available",
                    keywords=[],
                    importance_score=0.0,
                )

            keywords_response = self.keywords_finder.find_keywords(description)
            if not keywords_response.success:
                return EnhancedTableMetadata(
                    base_metadata=base_metadata,
                    description=description,
                    keywords=[],
                    importance_score=0.0,
                )

            importance_score = self._calculate_importance_score(base_metadata)

            return EnhancedTableMetadata(
                base_metadata=base_metadata,
                description=description,
                keywords=keywords_response.keywords,
                importance_score=importance_score,
            )

        except Exception as e:
            logger.exception(f"Error enhancing table metadata: {str(e)}")
            return EnhancedTableMetadata(
                base_metadata=base_metadata,
                description="Error enhancing metadata",
                keywords=[],
                importance_score=0.0,
            )

    def build_prompt(self, metadata: TableMetadata) -> str:
        """Builds the prompt for generating the table description"""

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

    def _generate_description(self, metadata: TableMetadata) -> Optional[str]:
        """Generates a semantic description of the table using the LLM"""
        prompt = self.build_prompt(metadata)

        description = self.llm_handler.get_completion(
            prompt=prompt,
            system_prompt="You are a database expert providing concise table descriptions.",
            temperature=0.1,
        )

        return description.strip() if description else None

    def _calculate_importance_score(self, metadata: TableMetadata) -> float:
        """
        Calculates an importance score for the table
        The logic is that a table is more important if it has more relationships, columns, and primary keys
        """
        score = 0.0

        # weight for relationships
        relations_weight = len(metadata.foreign_keys) * 0.2
        # weight for columns
        columns_weight = len(metadata.columns) * 0.1
        # weight for primary keys
        pk_weight = 0.3 if metadata.primary_keys else 0
        # normalize and combine scores
        score = min(1.0, relations_weight + columns_weight + pk_weight)

        return round(score, 2)
