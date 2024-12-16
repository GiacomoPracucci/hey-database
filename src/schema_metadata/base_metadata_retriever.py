import sqlalchemy as sa
import logging

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from sqlalchemy import inspect, text
from src.config.models.metadata import TableMetadata
from src.cache.metadata_cache import MetadataCache

logger = logging.getLogger('hey-database')

class DatabaseMetadataRetriever(ABC):
    """Classe base per il recupero dei metadati del database"""

    def __init__(self,
                 db_engine: sa.Engine,
                 schema: str = None,
                 cache_dir: Optional[str] = None):
        """Inizializza il gestore dello schema

        Args:
            db_engine: Engine del database
            schema: Nome dello schema da utilizzare
            cache_dir: Directory opzionale per il caching dei metadati
        """
        self.engine = db_engine
        self.schema = schema or db_engine.url.database
        self.tables: Dict[str, TableMetadata] = {}
        logger.info(f"Inizializzando metadata retriever per schema: {self.schema}")
        self.cache = MetadataCache(cache_dir, self.schema) if cache_dir else None
        self._load_schema_info()
        

    def _load_schema_info(self):
        """Carica le informazioni relative allo schema del database.
        Prima prova dalla cache, se non disponibile o invalida carica dal DB."""
        try:
            # prova a caricare dalla cache se disponibile
            if self.cache:
                cached_metadata = self.cache.get()
                if cached_metadata:
                    logger.info("Loading metadata from cache")
                    self.tables = cached_metadata
                    return
                logger.info("No valid cache found, loading from database")

            # se non c'è cache o è invalida, carica dal database
            logger.info("Loading metadata from database")
            inspector = inspect(self.engine)

            for table_name in inspector.get_table_names(schema=self.schema):
                logger.info(f"Estraggo i metdati per la tabella: {table_name}")
                try:
                    # info colonne
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
                    #row_count = self._get_row_count(table_name)
                    row_count = 10

                    self.tables[table_name] = TableMetadata(
                        name=table_name,
                        columns=columns,
                        primary_keys=primary_keys,
                        foreign_keys=foreign_keys,
                        row_count=row_count
                    )
                    logger.info(f"Tabella {table_name} processata con successo")

                except Exception as e:
                    logger.error(f"Errore nel processare la tabella {table_name}: {str(e)}")
                    continue

            if self.cache and self.tables:
                logger.info("Saving metadata to cache")
                self.cache.set(self.tables)

        except Exception as e:
            logger.error(f"Error loading schema metadata: {str(e)}")
            # se abbiamo dati in cache e incontriamo un errore, usiamo quelli
            if self.cache and self.tables:
                logger.warning("Using cached metadata after database error")
            else:
                raise

    def refresh_metadata(self) -> None:
        """Forza il refresh dei metadati invalidando la cache"""
        if self.cache:
            logger.debug("Invalidating metadata cache")
            self.cache.invalidate()
        self._load_schema_info()

    def get_table_metadata(self, table_name: str) -> Optional[TableMetadata]:
        """Recupera i metadati di una tabella specifica"""
        return self.tables.get(table_name)

    def get_all_tables_metadata(self) -> Dict[str, TableMetadata]:
        """Recupera i metadati di tutte le tabelle dello schema"""
        return self.tables

    def get_sample_data(self, table_name: str, max_rows: int = 3) -> List[Dict]:
        """Recupera dati di esempio da una tabella"""
        try:
            with self.engine.connect() as connection:
                query = text(f"SELECT * FROM {self.schema}.{table_name} LIMIT {max_rows}")
                result = connection.execute(query)

                columns = result.keys()
                return [dict(zip(columns, row)) for row in result]

        except Exception as e:
            logger.error(f"Errore nel recupero dei dati di esempio per {table_name}: {str(e)}")
            return []

    @abstractmethod
    def _get_row_count(self, table_name: str) -> int:
        """Recupera il conteggio delle righe per una tabella (implementazione specifica per database)"""
        pass

    @abstractmethod
    def get_table_definition(self, table_name: str) -> str:
        """Recupera la definizione DDL di una tabella (implementazione specifica per database)"""
        pass