from dataclasses import dataclass
from typing import List, Dict

@dataclass
class TableMetadata:
    """Classe per memorizzare i metadati essenziali di una tabella."""
    name: str
    columns: List[Dict[str, str]]  # [{"name": "id", "type": "integer", "nullable": false}, ...]
    primary_keys: List[str]        
    foreign_keys: List[Dict[str, str]]  
    row_count: int
