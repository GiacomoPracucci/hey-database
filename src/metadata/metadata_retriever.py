import sqlalchemy as sa
import logging

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from sqlalchemy import inspect, text
from sqlalchemy.engine import Inspector

from src.models.metadata import TableMetadata, EnhancedTableMetadata
from src.cache.metadata_cache import MetadataCache
from src.agents.metadata_enhancer_agent import MetadataAgent
from src.llm_handler.llm_handler import LLMHandler
from src.config.models.metadata import MetadataConfig
from src.metadata.enhancement_strategy import MetadataEnhancementStrategy

logger = logging.getLogger("hey-database")


class DatabaseMetadataRetriever(ABC):
    """Classe base per il recupero dei metadati del database"""

    def __init__(
        self,
        db_engine: sa.Engine,
        llm_handler: LLMHandler,
        enhancement_strategy: MetadataEnhancementStrategy,
        metadata_config: MetadataConfig,
        schema: str = None,
        cache_dir: Optional[str] = None,
    ):
        """
        Args:
            db_engine: Engine del database
            llm_handler: Handler per il modello di linguaggio
            enhancement_strategy: Strategia per determinare se fare enhancement
            metadata_config: Configurazione per il recupero dei metadati
            schema: Nome dello schema da utilizzare
            cache_dir: Directory opzionale per il caching dei metadati
        """
        self.engine = db_engine
        self.llm_handler = llm_handler
        self.enhancement_strategy = enhancement_strategy
        self.metadata_config = metadata_config
        self.schema = schema or db_engine.url.database
        self.tables: Dict[str, EnhancedTableMetadata] = {}
        self.inspector: Inspector = inspect(self.engine)
        self.metadata_agent = MetadataAgent(llm_handler)
        logger.info(f"Inizializzando metadata retriever per schema: {self.schema}")
        self.cache = MetadataCache(cache_dir, self.schema) if cache_dir else None
        self._load_schema_info()

    def _load_schema_info(self):
        """Carica le informazioni relative allo schema del database.
        Prima prova dalla cache, se non disponibile o invalida carica dal DB."""

        try:
            # prima verifichiamo se abbiamo gia localmente i metadati
            self._get_local_metadata()
            if self.tables:
                # se sono stati trovati i metadati, possiamo uscire
                return

            # se non c'è cache o è invalida, carica dal database
            logger.info("Loading metadata from database")
            base_metadata = {}

            for table_name in self.inspector.get_table_names(schema=self.schema):
                logger.info(f"Estraggo i metadati per la tabella: {table_name}")
                try:
                    # 1. Estrazione metadati base
                    base_metadata[table_name] = self._extract_base_metadata(table_name)
                except Exception as e:
                    logger.error(
                        f"Errore nel processare la tabella {table_name}: {str(e)}"
                    )
                    continue

            # 2. Enhancement dei metadati se necessario
            if self.enhancement_strategy.should_enhance():
                logger.info("Performing metadata enhancement")
                enhancement_result = self.metadata_agent.run(base_metadata)
                if enhancement_result.success:
                    self.tables = enhancement_result.enhanced_metadata
                else:
                    logger.error(f"Enhancement failed: {enhancement_result.error}")
                    # crea enhanced metadata con valori di default
                    self.tables = {
                        name: EnhancedTableMetadata(
                            base_metadata=metadata,
                            description="",
                            keywords=[],
                            importance_score=0.0,
                        )
                        for name, metadata in base_metadata.items()
                    }
            else:
                logger.info("Skipping metadata enhancement")
                # in questo caso creiamo enhanced metadata fittizi
                self.tables = {
                    name: EnhancedTableMetadata(
                        base_metadata=metadata,
                        description="",
                        keywords=[],
                        importance_score=0.0,
                    )
                    for name, metadata in base_metadata.items()
                }

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

    def _extract_base_metadata(self, table_name: str) -> TableMetadata:
        """Estrae i metadati base di una tabella.
        Args:
            table_name: Nome della tabella
        Returns:
            TableMetadata: Metadati base della tabella
        """
        # 1. estrazione delle info sulle colonne
        columns = self._get_table_columns_metadata(table_name)

        # 2. estrazione delle info sulle pks
        primary_keys = self._get_table_pk_metadata(table_name)

        # 3. estrazione delle info sulle fks
        foreign_keys = self._get_table_fk_metadata(table_name)

        # 4. row count della tabella
        row_count = self._get_row_count(table_name)

        return TableMetadata(
            name=table_name,
            columns=columns,
            primary_keys=primary_keys,
            foreign_keys=foreign_keys,
            row_count=row_count,
        )

    def _get_local_metadata(self) -> bool:
        """Recupera i metadati dalla cache locale se disponibili.
        Returns:
            bool: True se i metadati sono stati caricati dalla cache
        """
        if self.cache:
            cached_metadata = self.cache.get()
            if cached_metadata:
                logger.info("Loading metadata from cache")
                self.tables = cached_metadata
                return True
            logger.info("No valid cache found")
        return False

    def _get_table_columns_metadata(self, table_name: str) -> List[Dict[str, Any]]:
        """Recupera i metadati delle colonne per una tabella.
        Args:
            table_name: Nome della tabella
        Returns:
            List[Dict[str, Any]]: Lista dei metadati delle colonne
        """
        columns = []
        for col in self.inspector.get_columns(table_name, schema=self.schema):
            column_info = {
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col["nullable"],
            }

            if self.metadata_config.retrieve_distinct_values:
                column_info["distinct_values"] = self._get_column_distinct_values(
                    table_name,
                    col["name"],
                    max_values=self.metadata_config.max_distinct_values,
                )

            columns.append(column_info)
        return columns

    def _get_table_pk_metadata(self, table_name: str) -> List[str]:
        """Recupera i metadati delle chiavi primarie di una tabella"""
        pk_info = self.inspector.get_pk_constraint(table_name, schema=self.schema)
        return pk_info["constrained_columns"] if pk_info else []

    def _get_table_fk_metadata(self, table_name: str) -> List[Dict[str, Any]]:
        """Recupera i metadati delle chiavi esterne di una tabella"""
        foreign_keys = []
        for fk in self.inspector.get_foreign_keys(table_name, schema=self.schema):
            foreign_keys.append(
                {
                    "constrained_columns": fk["constrained_columns"],
                    "referred_table": fk["referred_table"],
                    "referred_columns": fk["referred_columns"],
                }
            )
        return foreign_keys

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
                query = text(
                    f"SELECT * FROM {self.schema}.{table_name} LIMIT {max_rows}"
                )
                result = connection.execute(query)

                columns = result.keys()
                return [dict(zip(columns, row)) for row in result]

        except Exception as e:
            logger.error(
                f"Errore nel recupero dei dati di esempio per {table_name}: {str(e)}"
            )
            return []

    @abstractmethod
    def _get_row_count(self, table_name: str) -> int:
        """Recupera il conteggio delle righe per una tabella (implementazione specifica per database)"""
        pass

    @abstractmethod
    def get_table_definition(self, table_name: str) -> str:
        """Recupera la definizione DDL di una tabella (implementazione specifica per database)"""
        pass

    @abstractmethod
    def _get_column_distinct_values(
        self, table_name: str, column_name: str, max_values: int = 100
    ) -> List[str]:
        """Recupera i valori distinti per una colonna.

        Args:
            table_name: Nome della tabella
            column_name: Nome della colonna
            max_values: Numero massimo di valori distinti da recuperare

        Returns:
            Lista di valori distinti come stringhe
        """
        pass
