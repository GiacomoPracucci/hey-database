from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class MetadataConfig:
    """Configurazione per il recupero ed elaborazione dei metadati"""

    retrieve_distinct_values: bool = True
    max_distinct_values: int = 100


@dataclass
class TableMetadata:
    """Metadati base inferiti dallo schema"""

    name: str
    columns: List[str]
    primary_keys: List[str]
    foreign_keys: List[Dict[str, str]]
    row_count: int


@dataclass
class EnhancedTableMetadata:
    """Metadati che generiamo noi con l'enhancer"""

    base_metadata: TableMetadata  # metadati originali
    description: str  # descrizione generata
    keywords: List[str]  # keywords estratte
    importance_score: float  # score calcolato


@dataclass
class TableRelationship:
    """Rappresenta una relazione (entrante o uscente) tra due tabelle"""

    related_table: str  # Nome della tabella collegata
    direction: str  # "incoming" o "outgoing"
    local_columns: List[str]  # Colonne della tabella corrente coinvolte nella relazione
    remote_columns: List[
        str
    ]  # Colonne della tabella collegata coinvolte nella relazione


@dataclass
class ColumnMetadata:
    """Base metadata for a column"""

    name: str
    table: str
    data_type: str
    nullable: bool
    is_primary_key: bool
    is_foreign_key: bool
    distinct_values: List[str] = field(default_factory=list)
    relationships: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class EnhancedColumnMetadata:
    """Enhanced metadata for a column"""

    base_metadata: ColumnMetadata
    ai_name: str
    description: str
    keywords: List[str]
