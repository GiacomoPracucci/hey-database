from typing import Dict, List
from sqlalchemy import text
from src.schema_metadata.base_metadata_retriever import DatabaseMetadataRetriever

class SnowflakeMetadataRetriever(DatabaseMetadataRetriever):
    """Implementazione Snowflake del retriever di metadati"""
    
    def _get_row_count(self, table_name: str) -> int:
        """Implementazione Snowflake del conteggio righe.
        
        In Snowflake, possiamo usare la vista INFORMATION_SCHEMA.TABLES
        che mantiene statistiche aggiornate sulle tabelle.
        """
        query = text("""
            SELECT ROW_COUNT 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = :schema 
            AND TABLE_NAME = :table
        """)
        
        with self.engine.connect() as connection:
            result = connection.execute(query, {
                "schema": self.schema.upper(),  # Snowflake usa maiuscole di default
                "table": table_name.upper()
            })
            return result.scalar() or 0
    
    def get_table_definition(self, table_name: str) -> str:
        """Recupera il DDL di una tabella usando funzioni di sistema Snowflake."""
        try:
            # In Snowflake possiamo usare GET_DDL per ottenere la definizione esatta
            query = text("""
                SELECT GET_DDL('TABLE', :table_ref)
            """)
            
            table_ref = f"{self.schema}.{table_name}".upper()
            
            with self.engine.connect() as conn:
                result = conn.execute(query, {"table_ref": table_ref})
                return result.scalar() or ""
                
        except Exception as e:
            print(f"Errore nel recupero del DDL per {table_name}: {str(e)}")
            return ""
            
    def get_sample_data(self, table_name: str, max_rows: int = 3) -> List[Dict]:
        """Override del metodo base per gestire le maiuscole in Snowflake."""
        try:
            with self.engine.connect() as connection:
                # In Snowflake usiamo maiuscole e sampling per performance
                query = text(f"""
                    SELECT * 
                    FROM {self.schema.upper()}.{table_name.upper()} 
                    SAMPLE ({max_rows} ROWS)
                """)
                result = connection.execute(query)
                
                columns = result.keys()
                return [dict(zip(columns, row)) for row in result]
                
        except Exception as e:
            print(f"Errore nel recupero dei dati di esempio per {table_name}: {e}")
            return []