from dataclasses import dataclass
from typing import Dict, List, Optional
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy import text
from src.dbcontext.base_metadata_retriever import TableMetadata, DatabaseMetadataRetriever

    
class PostgresMetadataRetriever(DatabaseMetadataRetriever):
    """Implementazione PostgreSQL del retriever di metadati"""
    
    def __init__(self, db_engine: sa.Engine, schema: str = 'video_games'):
        """Inizializza il gestore dello schema
        
        Args:
            db_engine (sqlalchemy.Engine): Engine del database
            schema (str): Nome dello schema da utilizzare
        """
        self.engine = db_engine
        self.schema = schema
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
                
                # Conteggio righe
                query = text(f"SELECT COUNT(*) FROM {self.schema}.{table_name}")
                with self.engine.connect() as connection:
                    row_count = connection.execute(query).scalar()
                
                self.tables[table_name] = TableMetadata(
                    name=table_name,
                    columns=columns,
                    primary_keys=primary_keys,
                    foreign_keys=foreign_keys,
                    row_count=row_count
                )
                
            except Exception as e:
                print(f"Errore nel processare la tabella {table_name}: {str(e)}")
    
    def get_table_definition(self, table_name: str) -> str:
        """Recupera il DDL di una tabella usando funzioni di sistema PostgreSQL."""
        try:
            query = text(f"""
                SELECT 
                    'CREATE TABLE ' || table_name || ' (' ||
                    string_agg(
                        column_name || ' ' || data_type || 
                        CASE 
                            WHEN character_maximum_length IS NOT NULL 
                            THEN '(' || character_maximum_length || ')'
                            ELSE ''
                        END ||
                        CASE WHEN is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END,
                        ', '
                    ) ||
                    ');'
                FROM information_schema.columns
                WHERE table_schema = :schema AND table_name = :table
                GROUP BY table_name;
            """)
            
            with self.engine.connect() as conn:
                result = conn.execute(query, {"schema": self.schema, "table": table_name})
                return result.scalar() or ""
                
        except Exception as e:
            print(f"Errore nel recupero del DDL per {table_name}: {str(e)}")
            return ""
    
    def get_table_metadata(self, table_name: str) -> Optional[TableMetadata]:
        """Recupera i metadati di una tabella specifica.
        
        Args:
            table_name (str): Nome della tabella
            
        Returns:
            Optional[TableMetadata]: Metadati della tabella o None se non esiste
        """
        return self.tables.get(table_name)
    
    def get_all_tables(self) -> Dict[str, TableMetadata]:
        """Recupera i metadati di tutte le tabelle.
        
        Returns:
            Dict[str, TableMetadata]: Dizionario con tutte le informazioni delle tabelle
        """
        return self.tables
    
    def get_sample_data(self, table_name: str, max_rows: int = 3) -> List[Dict]:
        """Recupera dati di esempio da una tabella.
        
        Args:
            table_name (str): Nome della tabella
            max_rows (int): Numero massimo di righe da recuperare
            
        Returns:
            List[Dict]: Lista di dizionari contenenti i dati di esempio
        """
        try:
            with self.engine.connect() as connection:
                query = text(f"SELECT * FROM {self.schema}.{table_name} LIMIT {max_rows}")
                result = connection.execute(query)
                
                columns = result.keys()
                return [dict(zip(columns, row)) for row in result]
                
        except Exception as e:
            print(f"Errore nel recupero dei dati di esempio per {table_name}: {e}")
            return []