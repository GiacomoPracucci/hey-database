import yake
from src.keywords.keywords_finder import KeywordsFinder
from models.keywords import KeywordsFinderResponse
import logging

logger = logging.getLogger("hey-database")


class YAKEKeywordsFinder(KeywordsFinder):
    """Keywords finder base on YAKE algorithm (https://github.com/LIAAD/yake)"""

    def __init__(self, max_keywords: int = 5, language: str = "en"):
        """
        Initialize YAKE Finder

        Args:
            max_keywords: Max number of keywords to extract
            language: Language of the text (default: English) TODO: need to read the language from the config
        """
        try:
            self.finder = yake.KeywordExtractor(
                lan=language,
                n=2,  # n-grams
                dedupLim=0.2,
                top=max_keywords,
                features=None,
            )
            logger.debug(
                f"Initialized YAKE extractor with max_keywords={max_keywords}, language={language}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize YAKE extractor: {str(e)}")
            raise

    def find_keywords(self, text: str) -> KeywordsFinderResponse:
        if not text or not text.strip():
            logger.warning("Empty or whitespace-only text provided")
            return KeywordsFinderResponse(
                success=False, error="Input text cannot be empty"
            )
        try:
            # YAKE return (keyword, score) - lower score = more relevant
            keywords = self.finder.extract_keywords(text)
            logger.debug(f"Successfully extracted {len(keywords)} keywords")

            return KeywordsFinderResponse(
                success=True,
                keywords=[keyword for keyword, _ in keywords],
                scores=[score.item() for _, score in keywords],
            )

        except Exception as e:
            logger.error(f"Error extracting keywords with YAKE: {str(e)}")
            return KeywordsFinderResponse(success=False, error=str(e))
