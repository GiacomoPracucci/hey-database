import logging
from src.llm_handler.llm_handler import LLMHandler
from src.keywords.keywords_finder import KeywordsFinder
from src.models.keywords import KeywordsFinderResponse
from src.llm_output_processing.parser import ResponseParser as parser

logger = logging.getLogger("hey-database")


class LLMKeywordsFinder(KeywordsFinder):
    """Keywords finder implementation using LLM"""

    def __init__(self, llm: LLMHandler):
        self.llm = llm
        self.system_prompt = """
        You are an expert in natural language analysis specialized in extracting relevant keywords from database queries.
        ALWAYS respond in JSON format with a list of keywords. Example: {“keywords”: [“keyword1”, “keyword2”]}
        """

    def find_keywords(self, text: str) -> KeywordsFinderResponse:
        try:
            logger.debug(f"I'll extract keywords from '{text}'")
            prompt = self.build_prompt(text)
            logger.debug(f"Built prompt: {prompt}")
            response = self.llm.get_completion(
                prompt=prompt, system_prompt=self.system_prompt, temperature=0.05
            )

            if not response:
                logger.error("Failed to get response from LLM")
                return KeywordsFinderResponse(
                    success=False, error="Failed to get response from LLM"
                )

            cleaned_keywords = parser.parse_llm_response(response)
            logger.debug(f"Found keywords: {cleaned_keywords}")

            return KeywordsFinderResponse(
                success=True,
                keywords=[keyword for keyword in cleaned_keywords["keywords"]],
                scores=[1.0 for _ in cleaned_keywords["keywords"]],
            )

        except Exception as e:
            logger.error(f"Error extracting keywords with LLM: {str(e)}")
            return KeywordsFinderResponse(success=False, error=str(e))

    def build_prompt(self, text: str) -> str:
        """
        Build the prompt for the keywords extraction task.

        Args:
            text:
        Returns:
            str: Formatted prompt for the LLM
        """
        prompt_parts = []

        # base template with core instructions
        prompt_parts.append(f"""Given a query on the database, identify ONLY the most relevant keywords to find related columns.
        Important rules:
        1. Extract ONLY words that could match column names or their contents
        2. Completely ignore numbers, years, months, and days-these are never keywords
        3. Include dates and numbers if present and relevant
        4. Respond ONLY with a JSON object containing a 'keywords' list
        """)

        #
        prompt_parts.append("""Examples""")
        prompt_parts.append("\nQUERY:")
        prompt_parts.append(text)

        return "\n\n".join(prompt_parts)
