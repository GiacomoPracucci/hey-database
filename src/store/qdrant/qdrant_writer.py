from typing import List, Dict
from dataclasses import asdict
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct, UpdateStatus

from src.models.metadata import (
    TableMetadata,
    ColumnMetadata,
    QueryPayload,
)

from src.store.qdrant.qdrant_client import QdrantStore
from src.store.vectorstore_writer import StoreWriter

import logging

logger = logging.getLogger("hey-database")


class QdrantWriter(StoreWriter):
    def __init__(self, vector_store: QdrantStore):
        """
        Prende in input lo store in cui scrivere i risultati

        Args:
            vector_store: Istanza di VectorStore per l'interazione con Qdrant
        """

        self.vector_store = vector_store

    def add_table(self, metadata: TableMetadata) -> bool:
        """
        Aggiunge o aggiorna un documento tabella nella collection
        Args:
            metadata: Metadati arricchiti della tabella
        Returns:
            bool: True se l'operazione è andata a buon fine, False altrimenti
        """
        try:
            # embedding dalla descrizione e keywords
            embedding_text = f"{metadata.base_metadata.name} {metadata.description} {' '.join(metadata.keywords)}"
            vector = self.embedding_model.encode(embedding_text)

            # upsert del documento
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=self._generate_table_id(metadata.base_metadata.name),
                        vector=vector,
                        payload=asdict(metadata),
                    )
                ],
            )
            logger.debug(
                f"Metadata added/updated for table: {metadata.base_metadata.name}"
            )
            return True
        except Exception as e:
            logger.error(f"Error adding table metadata: {str(e)}")
            return False

    def add_tables_batch(self, metadata_list: List[TableMetadata]) -> Dict[str, bool]:
        """
        Add or update multiple tables in a single batch operation.

        Args:
            metadata_list: List of table metadata to be stored

        Returns:
            Dict[str, bool]: Status of each table operation, keyed by table name
        """
        try:
            points = []
            table_status = {}

            # Prepare all points for batch insertion
            for metadata in metadata_list:
                table_name = metadata.base_metadata.name
                try:
                    # Generate embedding for the table
                    embedding_text = f"{table_name} {metadata.description} {' '.join(metadata.keywords)}"
                    vector = self.embedding_model.encode(embedding_text)

                    # Create point structure
                    point = PointStruct(
                        id=self._generate_table_id(table_name),
                        vector=vector,
                        payload=asdict(metadata),
                    )
                    points.append(point)
                    table_status[table_name] = True
                except Exception as e:
                    logger.error(f"Failed to prepare table {table_name}: {str(e)}")
                    table_status[table_name] = False

            # Execute batch upsert
            if points:
                self.client.upsert(collection_name=self.collection_name, points=points)

            return table_status

        except Exception as e:
            logger.error(f"Batch table update failed: {str(e)}")
            return {metadata.base_metadata.name: False for metadata in metadata_list}

    def add_column(self, metadata: ColumnMetadata) -> bool:
        """
        Aggiunge o aggiorna un documento colonna nella collection

        Args:
            metadata: Metadati arricchiti della colonna
        Returns:
            bool: True se l'operazione è andata a buon fine
        """

        try:
            embedding_text = f"{metadata.base_metadata.name} {metadata.description}"
            vector = self.embedding_model.encode(embedding_text)

            # upsert del documento
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=self._generate_column_id(
                            metadata.base_metadata.table, metadata.base_metadata.name
                        ),
                        vector=vector,
                        payload=asdict(metadata),
                    )
                ],
            )
            logger.debug(
                f"Column metadata added/updated for: {metadata.base_metadata.table}.{metadata.base_metadata.name}"
            )
            return True

        except Exception as e:
            logger.error(f"Error adding column metadata: {str(e)}")
            return False

    def add_columns_batch(self, metadata_list: List[ColumnMetadata]) -> Dict[str, bool]:
        """
        Add or update multiple columns in a single batch operation.

        Args:
            metadata_list: List of column metadata to be stored

        Returns:
            Dict[str, bool]: Status of each column operation, keyed by "table.column"
        """
        try:
            points = []
            column_status = {}

            # Prepare all points for batch insertion
            for metadata in metadata_list:
                column_id = (
                    f"{metadata.base_metadata.table}.{metadata.base_metadata.name}"
                )
                try:
                    # Generate embedding for the column
                    embedding_text = (
                        f"{metadata.base_metadata.name} {metadata.description}"
                    )
                    vector = self.embedding_model.encode(embedding_text)

                    # Create point structure
                    point = PointStruct(
                        id=self._generate_column_id(
                            metadata.base_metadata.table, metadata.base_metadata.name
                        ),
                        vector=vector,
                        payload=asdict(metadata),
                    )
                    points.append(point)
                    column_status[column_id] = True
                except Exception as e:
                    logger.error(f"Failed to prepare column {column_id}: {str(e)}")
                    column_status[column_id] = False

            # Execute batch upsert
            if points:
                self.client.upsert(collection_name=self.collection_name, points=points)

            return column_status

        except Exception as e:
            logger.error(f"Batch column update failed: {str(e)}")
            return {
                f"{m.base_metadata.table}.{m.base_metadata.name}": False
                for m in metadata_list
            }

    def add_query(self, query: QueryPayload) -> bool:
        """Aggiunge una risposta del LLM al vector store (domanda utente + query sql + spiegazione)"""
        try:
            vector = self.embedding_model.encode(query.question)

            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=self._generate_query_id(query.question),
                        vector=vector,
                        payload=asdict(query),
                    )
                ],
            )
            return True

        except Exception as e:
            logger.error(f"Error adding query: {str(e)}")
            return False

    def add_queries_batch(self, queries: List[QueryPayload]) -> Dict[str, bool]:
        """
        Add or update multiple queries in a single batch operation.

        Args:
            queries: List of query payloads to be stored

        Returns:
            Dict[str, bool]: Status of each query operation, keyed by question
        """
        try:
            points = []
            query_status = {}

            # Prepare all points for batch insertion
            for query in queries:
                try:
                    # Generate embedding for the query
                    vector = self.embedding_model.encode(query.question)

                    # Create point structure
                    point = PointStruct(
                        id=self._generate_query_id(query.question),
                        vector=vector,
                        payload=asdict(query),
                    )
                    points.append(point)
                    query_status[query.question] = True
                except Exception as e:
                    logger.error(
                        f"Failed to prepare query '{query.question}': {str(e)}"
                    )
                    query_status[query.question] = False

            # Execute batch upsert
            if points:
                self.client.upsert(collection_name=self.collection_name, points=points)

            return query_status

        except Exception as e:
            logger.error(f"Batch query update failed: {str(e)}")
            return {query.question: False for query in queries}

    def delete_points(self, point_ids: List[str]) -> bool:
        """
        Delete multiple points from the vector store.

        Args:
            point_ids: List of point IDs to delete

        Returns:
            bool: True if all deletions were successful
        """
        try:
            response = self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(points=point_ids),
            )
            # Check if operation was successful
            if response.status == UpdateStatus.COMPLETED:
                return True
            else:
                logger.error(f"Points deletion failed with status: {response.status}")
                return False

        except Exception as e:
            logger.error(f"Failed to delete points: {str(e)}")
            return False

    def update_vectors(self, points: Dict[str, List[float]]) -> bool:
        """
        Update vectors for existing points.

        Args:
            points: Dictionary mapping point IDs to their new vectors

        Returns:
            bool: True if all updates were successful
        """
        try:
            vectors_to_update = [
                models.PointVectors(id=point_id, vector=vector)
                for point_id, vector in points.items()
            ]

            operation = models.UpdateVectorsOperation(
                update_vectors=models.UpdateVectors(points=vectors_to_update)
            )

            self.client.batch_update_points(
                collection_name=self.collection_name, update_operations=[operation]
            )
            return True

        except Exception as e:
            logger.error(f"Failed to update vectors: {str(e)}")
            return False
