from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class MetadataConfig:
    """Configurazione per il recupero ed elaborazione dei metadati"""

    retrieve_distinct_values: bool = True
    max_distinct_values: int = 100


@dataclass
class BaseTableMetadata:
    """Metadati base inferiti dallo schema"""

    name: str
    columns: List[str]
    primary_keys: List[str]
    foreign_keys: List[Dict[str, str]]
    row_count: int


@dataclass
class TableMetadata:
    """Metadati che generiamo noi con l'enhancer"""

    base_metadata: BaseTableMetadata  # metadati originali
    description: str  # descrizione generata
    keywords: List[str]  # keywords estratte
    importance_score: float  # score calcolato

    @classmethod
    def from_dict(cls, data: Dict) -> "TableMetadata":
        """
        Creates an EnhancedTableMetadata instance from a dictionary.
        Used when loading data from cache.

        Args:
            data: Dictionary containing the serialized metadata
        Returns:
            EnhancedTableMetadata instance
        """
        base_metadata = BaseTableMetadata(
            name=data["name"],
            columns=data["columns"],
            primary_keys=data["primary_keys"],
            foreign_keys=data["foreign_keys"],
            row_count=data["row_count"],
        )

        return cls(
            base_metadata=base_metadata,
            description=data["description"],
            keywords=data["keywords"],
            importance_score=data["importance_score"],
        )


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
class BaseColumnMetadata:
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
class ColumnMetadata:
    """Enhanced metadata for a column"""

    base_metadata: BaseColumnMetadata
    ai_name: str
    description: str
    keywords: List[str]

    @classmethod
    def from_dict(cls, data: Dict) -> "ColumnMetadata":
        """
        Creates an EnhancedColumnMetadata instance from a dictionary.
        Used when loading data from cache.

        Args:
            data: Dictionary containing the serialized metadata
        Returns:
            EnhancedColumnMetadata instance
        """
        base_metadata = BaseColumnMetadata(
            name=data["name"],
            table=data["table"],
            data_type=data["data_type"],
            nullable=data["nullable"],
            is_primary_key=data["is_primary_key"],
            is_foreign_key=data["is_foreign_key"],
            distinct_values=data["distinct_values"],
            relationships=[],  # Le relationships sono vuote perché non vengono serializzate
        )

        return cls(
            base_metadata=base_metadata,
            ai_name=data["ai_name"],
            description=data["description"],
            keywords=data["keywords"],
        )


@dataclass
class Metadata:
    """
    Represents the current state of database metadata.
    Acts as an immutable container for metadata information.
    """

    tables: Dict[str, TableMetadata]
    columns: Dict[str, Dict[str, ColumnMetadata]]

    @classmethod
    def from_dict(cls, data: Dict) -> "Metadata":
        """
        Builds a Metadata object from a dictionary.

        This method is used when metadata are loaded from the cache.
        """
        tables = {
            name: TableMetadata.from_dict(table_data)
            for name, table_data in data["tables"].items()
        }
        columns = {
            table_name: {
                col_name: ColumnMetadata.from_dict(col_data)
                for col_name, col_data in table_cols.items()
            }
            for table_name, table_cols in data["columns"].items()
        }
        return cls(tables=tables, columns=columns)
