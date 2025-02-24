from dataclasses import dataclass
from typing import List, Dict, Optional, Literal

import uuid

from src.models.embedding import EmbeddingConfig
from src.models.metadata import Metadata


@dataclass
class VectorStoreConfig:
    """Configurazione standard per il vector store"""

    type: str  # qdrant, ecc
    collection_name: str
    path: Optional[str]  # path per lo storage locale
    url: Optional[str]  # url per server remoto
    embedding: EmbeddingConfig
    api_key: Optional[str] = None
    batch_size: int = 100


# "type" possibili di documento all'interno dello store
DocumentType = Literal["table", "column", "query"]


@dataclass
class BasePayload:
    """Base class per tutti i payload nel vector store"""

    type: DocumentType


@dataclass
class TablePayload(BasePayload):
    """Rappresenta il payload per i metadati di un documento 'tabella' nel vector store"""

    name: str
    description: str
    keywords: List[str]
    columns: List[str]
    primary_keys: List[str]
    foreign_keys: List[Dict[str, str]]
    row_count: int
    importance_score: float = 0.0

    @classmethod
    def from_enhanced_metadata(cls, metadata: Metadata) -> "TablePayload":
        """Crea un payload da metadati enhanced"""
        return cls(
            type="table",
            name=metadata.base_metadata.name,
            description=metadata.description,
            keywords=metadata.keywords,
            columns=metadata.base_metadata.columns,
            primary_keys=metadata.base_metadata.primary_keys,
            foreign_keys=metadata.base_metadata.foreign_keys,
            row_count=metadata.base_metadata.row_count,
            importance_score=metadata.importance_score,
        )


@dataclass
class ColumnPayload(BasePayload):
    """Rappresenta il payload per i metadati di un documento 'colonna' nel vector store"""

    column_name: str
    ai_name: str
    table_name: str
    description: str
    keywords: List[str]
    data_type: str
    nullable: bool
    is_primary_key: bool
    is_foreign_key: bool
    distinct_values: List[str]
    # relationships:  List[Dict[str, str]] = field(default_factory=list)

    @classmethod
    def from_enhanced_metadata(cls, metadata: Metadata) -> "ColumnPayload":
        """Crea un payload da metadati enhanced della colonna"""
        return cls(
            type="column",
            column_name=metadata.base_metadata.name,
            ai_name=metadata.column_name_alias,
            table_name=metadata.base_metadata.table_name,
            description=metadata.description,
            keywords=metadata.keywords,
            data_type=metadata.base_metadata.data_type,
            nullable=metadata.base_metadata.nullable,
            is_primary_key=metadata.base_metadata.is_primary_key,
            is_foreign_key=metadata.base_metadata.is_foreign_key,
            distinct_values=metadata.base_metadata.distinct_values,
            # relationships=metadata.base_metadata.relationships if metadata.base_metadata.is_foreign_key else None
        )

    @staticmethod
    def generate_id(table_name: str, column_name: str) -> str:
        """Generate a unique id for a column, based on table and column name"""
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"column_{table_name}_{column_name}"))


@dataclass
class QueryPayload(BasePayload):
    """Payload per le query cached"""

    question: str
    sql_query: str
    explanation: str
    positive_votes: int

    def __init__(self, **kwargs):
        super().__init__(type="query")
        self.question = kwargs["question"]
        self.sql_query = kwargs["sql_query"]
        self.explanation = kwargs["explanation"]
        self.positive_votes = kwargs.get("positive_votes", 0)


@dataclass
class TableSearchResult:
    """Risultato della ricerca di tabelle rilevanti"""

    table_name: str
    metadata: TablePayload
    relevance_score: float


@dataclass
class ColumnSearchResult:
    """Risultato della ricerca di colonne rilevanti"""

    id: str
    column_name: str
    ai_name: str
    table_name: str
    metadata: ColumnPayload
    relevance_score: float


@dataclass
class QuerySearchResult:
    """Rappresenta un risultato della ricerca in un vectorstore"""

    question: str
    sql_query: str
    explanation: str
    score: float
    positive_votes: int
