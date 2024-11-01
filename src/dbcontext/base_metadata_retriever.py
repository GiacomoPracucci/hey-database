from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional
import sqlalchemy as sa
from sqlalchemy import inspect

@dataclass
class TableMetadata:
    """Classe per memorizzare i metadati essenziali di una tabella."""
    name: str
    columns: List[Dict[str, str]]  # [{"name": "id", "type": "integer", "nullable": false}, ...]
    primary_keys: List[str]        # Manteniamo questa info perché utile per il contesto
    foreign_keys: List[Dict[str, str]]  # Manteniamo anche questa per le relazioni
    row_count: int
    
class DatabaseMetadataRetriever(ABC):
    """Interfaccia base per il recupero dei metadati del database"""
    
    @abstractmethod
    def get_table_definition(self, table_name: str) -> str:
        """Recupera la definizione DDL di una tabella"""
        pass
    
    @abstractmethod
    def get_table_metadata(self, table_name: str) -> Optional[TableMetadata]:
        """Recupera i metadati di una tabella specifica"""
        pass
    
    @abstractmethod
    def get_all_tables(self) -> Dict[str, TableMetadata]:
        """Recupera i metadati di tutte le tabelle"""
        pass
    
    @abstractmethod
    def get_sample_data(self, table_name: str, max_rows: int = 3) -> List[Dict]:
        """Recupera dati di esempio da una tabella"""
        pass