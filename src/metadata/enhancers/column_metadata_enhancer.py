from typing import Optional
import logging

from src.models.metadata import ColumnMetadata, EnhancedColumnMetadata
from src.llm_handler.llm_handler import LLMHandler
from src.keywords.YAKE_keywords_finder import YAKEKeywordsFinder

logger = logging.getLogger("hey-database")


class ColumnMetadataEnhancer:
    """
    Enhancer responsible for enriching column metadata with:
    - Semantic description generated via LLM
    - Keywords extracted from the description
    """

    def __init__(self, llm_handler: LLMHandler):
        self.keywords_finder = YAKEKeywordsFinder()
        self.llm_handler = llm_handler

    def enhance(self, base_metadata: ColumnMetadata) -> EnhancedColumnMetadata:
        """
        Enriches the metadata of a database column

        Args:
            base_metadata: Base metadata of the column

        Returns:
            EnhancedColumnMetadata containing the enriched metadata or error information
        """
        try:
            description = self._generate_description(base_metadata)

            if not description:
                return EnhancedColumnMetadata(
                    base_metadata=base_metadata,
                    ai_name="placeholder",
                    description="No description available",
                    keywords=[],
                )

            keywords_response = self.keywords_finder.find_keywords(description)
            if not keywords_response.success:
                return EnhancedColumnMetadata(
                    base_metadata=base_metadata,
                    ai_name="placeholder",
                    description=description,
                    keywords=[],
                )

            return EnhancedColumnMetadata(
                base_metadata=base_metadata,
                ai_name="placeholder",
                description=description,
                keywords=keywords_response.keywords,
            )

        except Exception as e:
            logger.exception(f"Error enhancing column metadata: {str(e)}")
            return EnhancedColumnMetadata(
                base_metadata=base_metadata,
                ai_name="placeholder",
                description="Error enhancing column metadata",
                keywords=[],
            )

    def build_prompt(self, metadata: ColumnMetadata) -> str:
        """
        Builds the prompt for generating the column description
        TODO: This responsibility should be moved to a separate class
        """
        prompt_parts = [
            f"""Provide a semantic description of this database column, focusing on the meaning of the data it contains.
    Context:
    - Table: {metadata.table}
    - Column Name: {metadata.name}
    - Data Type: {metadata.data_type}
    - Nullable: {"Yes" if metadata.nullable else "No"}
    - Primary Key: {"Yes" if metadata.is_primary_key else "No"}
    - Foreign Key: {"Yes" if metadata.is_foreign_key else "No"}
    """
        ]

        if metadata.distinct_values:
            sample_values = metadata.distinct_values[:10]
            prompt_parts.append(
                f"- Sample values: {', '.join(map(str, sample_values))}"
            )

        prompt_parts.append("""
    Provide an extremely concise description (max 1 short sentence) that explains the meaning of the data contained in the column.
    The description should focus on the semantic meaning of the data, not on technical or relational aspects.
    Example 1:
    Context:
    - Table: products
    - Column Name: last_modified
    - Data Type: TIMESTAMP
    - Nullable: Yes
    - Primary Key: No
    - Sample values: 2024-01-15 14:30:00, 2024-01-16 09:45:22
    ❌ INCORRECT: "Timestamp that automatically updates whenever a record is modified, useful for tracking"
    ✅ CORRECT: "Date and time of the product's last modification"
                            
    Example 2:
    Context:
    - Table: users
    - Column Name: is_active
    - Data Type: CHAR(1)
    - Nullable: No
    - Primary Key: No
    - Sample values: Y, N
    ❌ INCORRECT: "Boolean flag indicating if the user is currently active in the system and can perform operations"
    ✅ CORRECT: "Y/N indicator of user's activity status"            
             
    Do not include reasoning, hypotheses, or assumptions in the description. Describe ONLY what is objectively present in the provided data.
    IMPORTANT: Base the description exclusively on the distinct values actually present in the column, without making inferences about other possible values.
    Wrong example: for a flag column with only the distinct value "-", DO NOT write "Flag that can take Y/N values", since that's not what you observe from the data, but limit yourself to describing the observed data.
         """)

        return "\n".join(prompt_parts)

    def _generate_description(self, metadata: ColumnMetadata) -> Optional[str]:
        """Generates a semantic description of the column using the LLM"""
        prompt = self.build_prompt(metadata)

        description = self.llm_handler.get_completion(
            prompt=prompt,
            system_prompt="You are a database expert who provides detailed and technically accurate column descriptions",
            temperature=0.05,
        )

        return description.strip() if description else None
