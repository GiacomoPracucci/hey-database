from typing import Optional, List, Tuple
from dataclasses import dataclass


@dataclass
class KeywordsFinderResponse:
    """Class representing the object that every implementation of keywords finder must return"""

    success: bool
    keywords: Optional[List[Tuple[str, float]]] = None
    scores: Optional[List[float]] = None
    error: Optional[str] = None
