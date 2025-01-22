from dataclasses import dataclass
from typing import List, Dict

@dataclass
class MetadataConfig:
    """Configurazione per il recupero ed elaborazione dei metadati"""
    retrieve_distinct_values: bool = False  # Se True, recupera i valori distinti delle colonne
    max_distinct_values: int = 100         # Numero massimo di valori distinti da recuperare per colonna

@dataclass
class TableMetadata:
    """Metadati inferiti dallo schema"""
    name: str
    columns: List[Dict[str, str]]  # [{"name": "id", "type": "integer", "nullable": false}, ...]
    primary_keys: List[str]        
    foreign_keys: List[Dict[str, str]]  
    row_count: int

@dataclass
class EnhancedTableMetadata:
    """Metadati che generiamo noi con l'enhancer"""
    base_metadata: TableMetadata    # metadati originali
    description: str               # descrizione generata
    keywords: List[str]           # keywords estratte
    importance_score: float       # score calcolato