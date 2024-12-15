from sqlalchemy import text
from src.schema_metadata.base_metadata_retriever import DatabaseMetadataRetriever

class MySQLMetadataRetriever(DatabaseMetadataRetriever):
    """Implementazione MySQL del retriever di metadati"""
    
    def _get_row_count(self, table_name: str) -> int:
        """Implementazione MySQL del conteggio righe"""
        query = text(f"SELECT TABLE_ROWS FROM information_schema.tables "
                    f"WHERE table_schema = :schema AND table_name = :table")
        with self.engine.connect() as connection:
            result = connection.execute(query, {"schema": self.schema, "table": table_name})
            return result.scalar() or 0
    
    def get_table_definition(self, table_name: str) -> str:
        """Recupera il DDL di una tabella usando funzioni di sistema MySQL."""
        try:
            query = text("SHOW CREATE TABLE " + self.schema + "." + table_name)
            
            with self.engine.connect() as conn:
                result = conn.execute(query)
                return result.fetchone()[1]
                
        except Exception as e:
            print(f"Errore nel recupero del DDL per {table_name}: {str(e)}")
            return ""