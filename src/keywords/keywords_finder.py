from models.keywords import KeywordsFinderResponse
from typing import List
from abc import ABC, abstractmethod

import logging

logger = logging.getLogger("hey-database")


class KeywordsFinder(ABC):
    """Base class for keyword finder implementations"""

    @abstractmethod
    def find_keywords(self, text: str) -> KeywordsFinderResponse:
        """
        Extracts keywords from text

        Args:
            text (str): Text to extract keywords from

        Returns:
            KeywordsFinderResponse: Object containing the extracted keywords
        """
        pass

    def get_keywords_list(self, finder_response: KeywordsFinderResponse) -> List[str]:
        """
        Extract keywords list from KeywordExtractionResponse object.

        Args:
            finder_response: Response object from run method

        Returns:
            List[str]: List of extracted keywords if successful, empty list otherwise
        """
        if finder_response.success:
            return finder_response.keywords
        else:
            logger.warning(f"Keywords extraction failed: {finder_response.error}")
            return []
