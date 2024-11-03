from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional
import sqlalchemy as sa
from sqlalchemy import inspect, text

@dataclass
class TableMetadata:
    """Classe per memorizzare i metadati essenziali di una tabella."""
    name: str
    columns: List[Dict[str, str]]  # [{"name": "id", "type": "integer", "nullable": false}, ...]
    primary_keys: List[str]        
    foreign_keys: List[Dict[str, str]]  
    row_count: int
    
class DatabaseMetadataRetriever(ABC):
    """Interfaccia base per il recupero dei metadati del database"""

    def __init__(self, db_engine: sa.Engine, schema: str = None):
        """Inizializza il gestore dello schema
        
        Args:
            db_engine (sqlalchemy.Engine): Engine del database
            schema (str): Nome dello schema da utilizzare
        """
        self.engine = db_engine
        self.schema = schema or db_engine.url.database
        self.tables: Dict[str, TableMetadata] = {}
        self._load_schema_info()
        

    def _load_schema_info(self):
        """Carica le informazioni relative allo schema del database"""
        inspector = inspect(self.engine)
        
        for table_name in inspector.get_table_names(schema=self.schema):
            try:
                # Info colonne
                columns = [{
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"]
                } for col in inspector.get_columns(table_name, schema=self.schema)]
                
                # Chiavi primarie
                pk_info = inspector.get_pk_constraint(table_name, schema=self.schema)
                primary_keys = pk_info['constrained_columns'] if pk_info else []
                
                # Foreign keys
                foreign_keys = []
                for fk in inspector.get_foreign_keys(table_name, schema=self.schema):
                    foreign_keys.append({
                        "constrained_columns": fk["constrained_columns"],
                        "referred_table": fk["referred_table"],
                        "referred_columns": fk["referred_columns"]
                    })
                
                # Conteggio righe - implementazione specifica per database
                row_count = self._get_row_count(table_name)
                
                self.tables[table_name] = TableMetadata(
                    name=table_name,
                    columns=columns,
                    primary_keys=primary_keys,
                    foreign_keys=foreign_keys,
                    row_count=row_count
                )
                
            except Exception as e:
                print(f"Errore nel processare la tabella {table_name}: {str(e)}")
                
    @abstractmethod
    def _get_row_count(self, table_name: str) -> int:
        """Recupera il conteggio delle righe per una tabella.
        
        Args:
            table_name (str): Nome della tabella
            
        Returns:
            int: Numero di righe nella tabella
        """
        pass
    
    @abstractmethod
    def get_table_definition(self, table_name: str) -> str:
        """Recupera la definizione DDL di una tabella"""
        pass
    
    def get_table_metadata(self, table_name: str) -> Optional[TableMetadata]:
        """Recupera i metadati di una tabella specifica."""
        return self.tables.get(table_name)
    
    def get_all_tables_metadata(self) -> Dict[str, TableMetadata]:
        """Recupera i metadati di tutte le tabelle dello schema"""
        return self.tables
    
    def get_sample_data(self, table_name: str, max_rows: int = 3) -> List[Dict]:
        """Recupera dati di esempio da una tabella."""
        try:
            with self.engine.connect() as connection:
                query = text(f"SELECT * FROM {self.schema}.{table_name} LIMIT {max_rows}")
                result = connection.execute(query)
                
                columns = result.keys()
                return [dict(zip(columns, row)) for row in result]
                
        except Exception as e:
            print(f"Errore nel recupero dei dati di esempio per {table_name}: {e}")
            return []
