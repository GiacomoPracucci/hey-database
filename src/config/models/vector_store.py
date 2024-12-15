from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Literal

from src.config.models.embedding import EmbeddingConfig
from src.config.models.metadata import EnhancedTableMetadata

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
    
    @classmethod
    def from_enhanced_metadata(cls, metadata: EnhancedTableMetadata) -> 'TablePayload':
        """Crea un payload da metadati enhanced"""
        return cls(
            type='table',
            table_name=metadata.base_metadata.name,
            description=metadata.description,
            keywords=metadata.keywords,
            columns=metadata.base_metadata.columns,
            primary_keys=metadata.base_metadata.primary_keys,
            foreign_keys=metadata.base_metadata.foreign_keys,
            row_count=metadata.base_metadata.row_count,
            importance_score=metadata.importance_score
        )
        
@dataclass
class QueryPayload(BasePayload):
    """Payload per le query cached"""
    question: str
    sql_query: str
    explanation: str
    positive_votes: int
    
    def __init__(self, **kwargs):
        super().__init__(
            type='query'
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

@dataclass
class QuerySearchResult:
    """Rappresenta un risultato della ricerca in un vectorstore"""
    question: str
    sql_query: str
    explanation: str
    score: float
    positive_votes: int        