from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Literal

from src.config.models.embedding import EmbeddingConfig

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
    

# "type" possibili di documento all'interno dello store
DocumentType = Literal['table', 'query']

@dataclass
class BasePayload:
    """Base class per tutti i payload nel vector store"""
    type: DocumentType
    embedding_source: str  # campo da cui è stato generato l'embedding
    
@dataclass
class TablePayload(BasePayload):
    """Rappresenta il payload per i metadati di una tabella nel vector store"""
    table_name: str
    description: str
    keywords: List[str]
    columns: List[Dict[str, Any]]
    primary_keys: List[str]
    foreign_keys: List[Dict[str, str]]
    row_count: int
    importance_score: float = 0.0
    
    def __init__(self, **kwargs):
        super().__init__(
            type='table',
            embedding_source=kwargs.get('embedding_source', '')
        )
        self.table_name = kwargs['table_name']
        self.description = kwargs['description']
        self.keywords = kwargs['keywords']
        self.columns = kwargs['columns']
        self.primary_keys = kwargs['primary_keys']
        self.foreign_keys = kwargs['foreign_keys']
        self.row_count = kwargs['row_count']
        self.importance_score = kwargs.get('importance_score', 0.0)
        
@dataclass
class QueryPayload(BasePayload):
    """Payload per le query cached"""
    question: str
    sql_query: str
    explanation: str
    positive_votes: int
    
    def __init__(self, **kwargs):
        super().__init__(
            type='query',
            embedding_source=kwargs.get('embedding_source', '')
        )
        self.question = kwargs['question']
        self.sql_query = kwargs['sql_query']
        self.explanation = kwargs['explanation']
        self.positive_votes = kwargs.get('positive_votes', 0)

@dataclass
class TableSearchResult:
    """Risultato della ricerca di tabelle rilevanti"""
    table_name: str
    metadata: TablePayload
    relevance_score: float
    matched_keywords: List[str]

@dataclass
class QuerySearchResult:
    """Rappresenta un risultato della ricerca in un vectorstore"""
    question: str
    sql_query: str
    explanation: str
    score: float
    positive_votes: int        