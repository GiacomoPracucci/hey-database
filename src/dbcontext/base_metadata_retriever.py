from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional
import sqlalchemy as sa
from sqlalchemy import inspect, text
from src.config.schema_metadata import (
    ERColumn, ERRelationship, ERTable, ERDiagram
)
from src.utils.caching import SchemaCache

@dataclass
class TableMetadata:
    """Classe per memorizzare i metadati essenziali di una tabella."""
    name: str
    columns: List[Dict[str, str]]  # [{"name": "id", "type": "integer", "nullable": false}, ...]
    primary_keys: List[str]        
    foreign_keys: List[Dict[str, str]]  
    row_count: int

class DatabaseMetadataRetriever(ABC):
    """Classe base per il recupero dei metadati del database"""

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


    def get_er_diagram(self) -> ERDiagram:
        """Genera la struttura dati per il diagramma ER.
        Questo metodo non modifica i metadati esistenti ma crea una nuova struttura
        specifica per la visualizzazione."""
        
        tables = []
        relationships = []
        
        # Utilizziamo i metadati già caricati da _load_schema_info
        for table_name, table_info in self.tables.items():
            # Converti le colonne nel formato ER
            er_columns = []
            primary_keys = table_info.primary_keys
            
            # Raccogli tutte le colonne che sono foreign keys
            foreign_key_columns = {
                col
                for fk in table_info.foreign_keys
                for col in fk['constrained_columns']
            }
            
            for col in table_info.columns:
                er_column = ERColumn(
                    name=col['name'],
                    type=str(col['type']),
                    is_primary_key=col['name'] in primary_keys,
                    is_foreign_key=col['name'] in foreign_key_columns,
                    is_nullable=col['nullable']
                )
                er_columns.append(er_column)
            
            # Crea la tabella ER
            er_table = ERTable(
                name=table_name,
                columns=er_columns
            )
            tables.append(er_table)
            
            # Aggiungi le relazioni
            for fk in table_info.foreign_keys:
                for idx, from_col in enumerate(fk['constrained_columns']):
                    to_col = fk['referred_columns'][idx]
                    
                    relationship = ERRelationship(
                        from_table=table_name,
                        to_table=fk['referred_table'],
                        from_column=from_col,
                        to_column=to_col,
                        # Per ora assumiamo N-1 come default, 
                        # in futuro potremmo analizzare gli indici per determinarlo più accuratamente
                        relationship_type='N-1'
                    )
                    relationships.append(relationship)
        
        return ERDiagram(tables=tables, relationships=relationships)

    def get_er_metadata(self) -> dict:
        """Converte il diagramma ER in un formato JSON-friendly per il frontend.
        Questo metodo prepara i dati nel formato esatto necessario per la 
        visualizzazione del diagramma."""
        
        er_diagram = self.get_er_diagram()
        
        return {
            "tables": [
                {
                    "name": table.name,
                    "columns": [
                        {
                            "name": col.name,
                            "type": col.type,
                            "isPrimaryKey": col.is_primary_key,
                            "isForeignKey": col.is_foreign_key,
                            "isNullable": col.is_nullable
                        }
                        for col in table.columns
                    ],
                    "position": {
                        "x": table.position_x if table.position_x is not None else 0,
                        "y": table.position_y if table.position_y is not None else 0
                    }
                }
                for table in er_diagram.tables
            ],
            "relationships": [
                {
                    "fromTable": rel.from_table,
                    "toTable": rel.to_table,
                    "fromColumn": rel.from_column,
                    "toColumn": rel.to_column,
                    "type": rel.relationship_type
                }
                for rel in er_diagram.relationships
            ]
        }