from dataclasses import dataclass
from typing import List, Tuple, Optional
import yake
import logging
from src.agents.agent import Agent

logger = logging.getLogger('hey-database')

@dataclass
class KeywordExtractionResponse:
    """Classe che rappresenta la risposta dell'agente di estrazione keywords"""
    success: bool
    keywords: Optional[List[Tuple[str, float]]] = None
    scores: Optional[List[float]] = None
    error: Optional[str] = None

class KeywordExtractionAgent(Agent):
    """Questa è una baseline di estrazione keyword
    TODO capire come irrobustire l'estrazione, seppur gia funziona decentemente considerata la semplicità
    """
    def __init__(self, max_keywords: int = 5, language: str = "it"):
        """Inizializza l'estrattore YAKE
        Args:
            max_keywords: Numero massimo di keywords da estrarre
            language: Lingua del testo (default: italiano)
        """
        try:
            self.extractor = yake.KeywordExtractor(
                lan=language,
                n=1,  # unigramma
                dedupLim=0.2,
                top=max_keywords,
                features=None
            )
            logger.debug(f"Initialized YAKE extractor with max_keywords={max_keywords}, language={language}")
        except Exception as e:
            logger.error(f"Failed to initialize YAKE extractor: {str(e)}")
            raise

    def run(self, text: str) -> KeywordExtractionResponse:
        """Estrae le keywords dal testo fornito
        Args:
            text: Testo da cui estrarre le keywords
        Returns:
            KeywordExtractionResponse contenente le keywords estratte o l'errore
        """
        if not text or not text.strip():
            logger.warning("Empty or whitespace-only text provided")
            return KeywordExtractionResponse(
                success=False,
                error="Input text cannot be empty"
            )
        try:
            # YAKE restituisce (keyword, score) - score più basso = più rilevante
            keywords = self.extractor.extract_keywords(text)
            logger.debug(f"Successfully extracted {len(keywords)} keywords")

            return KeywordExtractionResponse(success=True, keywords=[keyword for keyword, _ in keywords], scores= [score.item() for _, score in keywords])

        except Exception as e:
            logger.error(f"Error extracting keywords with YAKE: {str(e)}")
            return KeywordExtractionResponse(success=False, error=str(e))
