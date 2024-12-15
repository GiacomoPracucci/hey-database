from sqlalchemy import text
from src.schema_metadata.base_metadata_retriever import DatabaseMetadataRetriever

    
class PostgresMetadataRetriever(DatabaseMetadataRetriever):
    """Implementazione PostgreSQL del retriever di metadati"""
    
    def _get_row_count(self, table_name: str) -> int:
        """Implementazione PostgreSQL del conteggio righe"""
        query = text(f"SELECT COUNT(*) FROM {self.schema}.{table_name}")
        with self.engine.connect() as connection:
            return connection.execute(query).scalar() or 0
    
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