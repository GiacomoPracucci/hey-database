from sqlalchemy import text, inspect
from collections import defaultdict
from src.schema_metadata.base_metadata_retriever import DatabaseMetadataRetriever
import logging
from src.config.models.metadata import TableMetadata

logger = logging.getLogger('hey-database')

class VerticaMetadataRetriever(DatabaseMetadataRetriever):
    """Implementazione Vertica del retriever di metadati"""

    def _get_row_count(self, table_name: str) -> int:
        """Implementazione Vertica del conteggio righe"""
        query = text(f"SELECT COUNT(*) FROM {self.schema}.{table_name}")
        with self.engine.connect() as connection:
            return connection.execute(query).scalar() or 0

    def _get_foreign_keys(self, table_name: str) -> list:
        """Recupera le foreign keys direttamente dal catalogo di sistema di Vertica."""
        try:
            query = text("""
                SELECT 
                    constraint_name,
                    reference_table_schema,
                    reference_table_name,
                    reference_column_name,
                    column_name
                FROM v_catalog.foreign_keys 
                WHERE table_schema = :schema
                AND table_name = :table
                ORDER BY constraint_name, ordinal_position
            """)

            with self.engine.connect() as conn:
                result = conn.execute(query, {
                    "schema": self.schema,
                    "table": table_name
                })

                # Raggruppa le colonne per constraint_name
                fk_map = defaultdict(lambda: {
                    "constrained_columns": [],
                    "referred_columns": [],
                    "referred_table": "",
                    "referred_schema": ""
                })

                for row in result:
                    fk = fk_map[row.constraint_name]
                    fk["constrained_columns"].append(row.column_name)
                    fk["referred_columns"].append(row.reference_column_name)
                    fk["referred_table"] = row.reference_table_name
                    fk["referred_schema"] = row.reference_table_schema

                return [{
                    "constrained_columns": fk["constrained_columns"],
                    "referred_table": fk["referred_table"],
                    "referred_columns": fk["referred_columns"]
                } for fk in fk_map.values()]

        except Exception as e:
            logger.error(f"Errore nel recupero delle foreign keys per {table_name}: {str(e)}")
            return []

    def _load_schema_info(self):
        """Override del metodo base per usare il custom foreign key retriever"""
        try:
            # Prova a caricare dalla cache se disponibile
            if self.cache:
                cached_metadata = self.cache.get()
                if cached_metadata:
                    logger.info("Loading metadata from cache")
                    self.tables = cached_metadata
                    return
                logger.info("No valid cache found, loading from database")

            # Se non c'è cache o è invalida, carica dal database
            logger.info("Loading metadata from database")
            inspector = inspect(self.engine)

            for table_name in inspector.get_table_names(schema=self.schema):
                logger.info(f"Estraggo i metadati per la tabella: {table_name}")
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

                    # Foreign keys usando il nostro metodo custom
                    foreign_keys = self._get_foreign_keys(table_name)

                    # Conteggio righe
                    row_count = self._get_row_count(table_name)

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
            if self.cache and self.tables:
                logger.warning("Using cached metadata after database error")
            else:
                raise

    def get_table_definition(self, table_name: str) -> str:
        """Recupera il DDL di una tabella usando EXPORT_TABLES di Vertica."""
        try:
            query = text("""
                SELECT EXPORT_TABLES('', :table_ref);
            """)

            table_ref = f"{self.schema}.{table_name}"

            with self.engine.connect() as conn:
                result = conn.execute(query, {"table_ref": table_ref})
                ddl = result.scalar()
                return ddl if ddl else ""

        except Exception as e:
            logger.error(f"Errore nel recupero del DDL per {table_name}: {str(e)}")
            return ""