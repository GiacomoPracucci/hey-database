from typing import Dict

import json
import logging

logger = logging.getLogger("hey-database")


class ResponseParser:
    @staticmethod
    def parse_llm_response(response: str) -> Dict[str, str]:
        """
        Parse the JSON response from LLM.

        Args:
            response: JSON string from LLM

        Returns:
            Dict[str, str]: Dictionary with query and explanation
        """
        try:
            # Remove any potential markdown or extra text
            if isinstance(response, str):
                # If it is a string, it attempts JSON parsing
                response = response.strip()
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0]
                elif "```" in response:
                    response = response.split("```")[1].split("```")[0]

                return json.loads(response)
            elif isinstance(response, dict):
                # If it is a dictionary, it returns it as is
                return response

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            return {
                "query": "",
                "explanation": f"Error during JSON parsing: {str(e)}",
            }
