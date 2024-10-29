from dataclasses import dataclass
from typing import Dict, List, Optional
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy import text

@dataclass
class TableInfo:
    """Classe per memorizzare le informazioni di una tabella."""
    name: str
    columns: List[Dict[str, str]]
    primary_keys: List[str]
    foreign_keys: List[Dict[str, str]]
    row_count: int
    
class SchemaContextManager:
    """Classe responsabile per l'acquisizione e la gestione delle informazioni sullo schema del database """
    def __init__(self, db_engine: sa.Engine, schema: str = 'video_games'):
        """Inizializza il gestore dello schema
        
        Args:
            db_engine (sqlalchemy.Engine): Engine del database
            schema (str): Nome dello schema da utilizzare
        """
        self.engine = db_engine
        self.schema = schema
        self.tables: Dict[str, TableInfo] = {}
        self.load_schema_info()
        
    def load_schema_info(self):
        """Carica le informazioni relative allo schema del database"""
        inspector = inspect(self.engine)
        
        print(f"Cercando tabelle nello schema: {self.schema}")
        tables = inspector.get_table_names(schema=self.schema)
        print(f"Tabelle trovate: {tables}")
        
        with self.engine.connect() as connection:
            for table_name in tables:
                print(f"\nProcessando tabella: {table_name}")
                
                try:
                    # informazioni sulle colonne
                    columns = []
                    for column in inspector.get_columns(table_name, schema=self.schema):
                        columns.append({
                            "name": column["name"],
                            "type": str(column["type"]),
                            "nullable": column["nullable"]
                        })
                    
                    pk_info = inspector.get_pk_constraint(table_name, schema=self.schema)
                    primary_keys = pk_info['constrained_columns'] if pk_info else []
                    
                    foreign_keys = []
                    for fk in inspector.get_foreign_keys(table_name, schema=self.schema):
                        foreign_keys.append({
                            "constrained_columns": fk["constrained_columns"],
                            "referred_table": fk["referred_table"],
                            "referred_columns": fk["referred_columns"]
                        })
                    
                    query = text(f"SELECT COUNT(*) FROM {self.schema}.{table_name}")
                    result = connection.execute(query)
                    row_count = result.scalar()
                    
                    self.tables[table_name] = TableInfo(
                        name=table_name,
                        columns=columns,
                        primary_keys=primary_keys,
                        foreign_keys=foreign_keys,
                        row_count=row_count
                    )
                    print(f"Tabella {table_name} processata con successo")
                    
                except Exception as e:
                    print(f"Errore nel processare la tabella {table_name}: {str(e)}")
    
    def get_table_info(self, table_name: str) -> Optional[TableInfo]:
        """Ottiene le informazioni di una specifica tabella.
        
        Args:
            table_name (str): Nome della tabella
            
        Returns:
            Optional[TableInfo]: Informazioni della tabella o None se non esiste"""
        return self.tables.get(table_name)
    
    def get_all_tables(self) -> Dict[str, TableInfo]:
        """Ottiene le informazioni di tutte le tabelle.
        
        Returns:
            Dict[str, TableInfo]: Dizionario con tutte le informazioni delle tabelle"""
        return self.tables    
    
    def get_sample_data(self, table_name: str, max_rows: int = 3) -> List[Dict]:
        """Ottiene dati di esempio da una tabella."""
        try:
            with self.engine.connect() as connection:
                query = text(f"SELECT * FROM {self.schema}.{table_name} LIMIT {max_rows}")
                result = connection.execute(query)
                
                columns = result.keys()
                
                return [dict(zip(columns, row)) for row in result]
        except Exception as e:
            print(f"Errore nel recupero dei dati di esempio per {table_name}: {e}")
            return []