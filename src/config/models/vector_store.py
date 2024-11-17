from dataclasses import dataclass
from typing import Optional
from src.config.models.embedding import EmbeddingConfig

@dataclass
class QueryStorePayload:
    """Rappresenta il payload standard per ogni record nel vector store"""
    question: str
    sql_query: str
    explanation: str
    positive_votes: int

@dataclass
class VectorStoreConfig:
    """Configurazione standard per il vector store"""
    enabled: bool
    type: str # qdrant, ecc
    collection_name: str
    path: Optional[str] # path per lo storage locale
    url: Optional[str] # url per server remoto
    embedding: EmbeddingConfig
    api_key: Optional[str] = None
    batch_size: int = 100
    
@dataclass
class SearchResult:
    """Rappresenta un risultato della ricerca in un vectorstore"""
    question: str
    sql_query: str
    explanation: str
    score: float
    positive_votes: int