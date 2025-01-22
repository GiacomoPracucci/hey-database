from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass
class SQLAgentResponse:
    """Classe che rappresenta la risposta dell'agente SQL"""

    success: bool
    query: Optional[str] = None
    explanation: Optional[str] = None
    results: Optional[List[Dict]] = None
    preview: Optional[List[Dict]] = None
    error: Optional[str] = None
    from_vector_store: bool = False
    original_question: Optional[str] = None
