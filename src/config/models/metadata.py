from dataclasses import dataclass
from typing import List, Dict

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