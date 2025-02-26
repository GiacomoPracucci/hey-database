from typing import List, Dict
from dataclasses import asdict
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct, UpdateStatus

from src.models.metadata import TableMetadata, ColumnMetadata, QueryMetadata
from src.store.qdrant.qdrant_client import QdrantStore
from src.store.vectorstore_write import StoreWriter
from src.store.vectorstore_utils import VectorStoreUtils

import logging

logger = logging.getLogger("hey-database")


class QdrantWriter(StoreWriter):
    """
    Qdrant-specific implementation of the vector store writer.

    This class is responsible for adding, updating, and deleting documents
    in a Qdrant vector database. It handles the conversion between application
    metadata models and Qdrant's point structure, as well as generating the
    appropriate embeddings for semantic search.
    """

    def __init__(self, vector_store: QdrantStore):
        """
        Initialize the Qdrant writer with a connection to the vector store.

        Args:
            vector_store: Initialized QdrantStore instance for vectorstore operations
        """
        self.vector_store = vector_store

    def add_table(self, metadata: TableMetadata) -> bool:
        """
        Add or update table metadata in the vector database.

        Generates embeddings from the table name, description, and keywords,
        then stores the complete metadata payload in the vector database.

        Args:
            metadata: Enhanced table metadata to store

        Returns:
            bool: True if the operation was successful, False otherwise
        """
        try:
            # Generate embedding from table name, description and keywords
            embedding_text = (
                f"{metadata.name} {metadata.description} {' '.join(metadata.keywords)}"
            )
            vector = self.vector_store.embedding_model.encode(embedding_text)

            # Upsert document with generated ID
            self.vector_store.client.upsert(
                collection_name=self.vector_store.collection_name,
                points=[
                    models.PointStruct(
                        id=VectorStoreUtils.generate_table_id(metadata.name),
                        vector=vector,
                        payload=asdict(metadata),
                    )
                ],
            )
            logger.debug(f"Metadata added/updated for table: {metadata.name}")
            return True

        except Exception as e:
            logger.error(f"Error adding table metadata: {str(e)}")
            return False

    def add_tables_batch(self, metadata_list: List[TableMetadata]) -> Dict[str, bool]:
        """
        Add or update multiple tables in a single batch operation.

        Batch operations are more efficient than individual calls when
        adding multiple tables at once.

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
                table_name = metadata.name
                try:
                    # Generate embedding for the table
                    embedding_text = f"{table_name} {metadata.description} {' '.join(metadata.keywords)}"
                    vector = self.vector_store.embedding_model.encode(embedding_text)

                    # Create point structure
                    point = PointStruct(
                        id=VectorStoreUtils.generate_table_id(table_name),
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
                self.vector_store.client.upsert(
                    collection_name=self.vector_store.collection_name, points=points
                )

            return table_status

        except Exception as e:
            logger.error(f"Batch table update failed: {str(e)}")
            return {metadata.name: False for metadata in metadata_list}

    def add_column(self, metadata: ColumnMetadata) -> bool:
        """
        Add or update column metadata in the vector database.

        Generates embeddings from the column name and description,
        then stores the complete metadata payload in the vector database.

        Args:
            metadata: Enhanced column metadata to store

        Returns:
            bool: True if the operation was successful, False otherwise
        """
        try:
            # Generate embedding from column name and description
            embedding_text = f"{metadata.name} {metadata.description}"
            vector = self.vector_store.embedding_model.encode(embedding_text)

            # Upsert document with generated ID
            self.vector_store.client.upsert(
                collection_name=self.vector_store.collection_name,
                points=[
                    models.PointStruct(
                        id=VectorStoreUtils.generate_column_id(
                            metadata.table, metadata.name
                        ),
                        vector=vector,
                        payload=asdict(metadata),
                    )
                ],
            )
            logger.debug(
                f"Column metadata added/updated for: {metadata.table}.{metadata.name}"
            )
            return True

        except Exception as e:
            logger.error(f"Error adding column metadata: {str(e)}")
            return False

    def add_columns_batch(self, metadata_list: List[ColumnMetadata]) -> Dict[str, bool]:
        """
        Add or update multiple columns in a single batch operation.

        Batch operations are more efficient than individual calls when
        adding multiple columns at once.

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
                column_id = f"{metadata.table}.{metadata.name}"
                try:
                    # Generate embedding for the column
                    embedding_text = f"{metadata.name} {metadata.description}"
                    vector = self.vector_store.embedding_model.encode(embedding_text)

                    # Create point structure
                    point = PointStruct(
                        id=VectorStoreUtils.generate_column_id(
                            metadata.table, metadata.name
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
                self.vector_store.client.upsert(
                    collection_name=self.vector_store.collection_name, points=points
                )

            return column_status

        except Exception as e:
            logger.error(f"Batch column update failed: {str(e)}")
            return {f"{m.table}.{m.name}": False for m in metadata_list}

    def add_query(self, query: QueryMetadata) -> bool:
        """
        Add or update a query metadata in the vector database.

        Stores user questions along with their SQL translations and explanations
        for future semantic search.

        Args:
            query: Query metadata to store

        Returns:
            bool: True if operation was successful, False otherwise
        """
        try:
            vector = self.vector_store.embedding_model.encode(query.question)

            self.vector_store.client.upsert(
                collection_name=self.vector_store.collection_name,
                points=[
                    models.PointStruct(
                        id=VectorStoreUtils.generate_query_id(query.question),
                        vector=vector,
                        payload=asdict(query),
                    )
                ],
            )
            logger.debug(f"Query added/updated: '{query.question}'")
            return True

        except Exception as e:
            logger.error(f"Error adding query: {str(e)}")
            return False

    def add_queries_batch(self, queries: List[QueryMetadata]) -> Dict[str, bool]:
        """
        Add or update multiple queries in a single batch operation.

        Batch operations are more efficient than individual calls when
        adding multiple queries at once.

        Args:
            queries: List of query metadata to be stored

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
                    vector = self.vector_store.embedding_model.encode(query.question)

                    # Create point structure
                    point = PointStruct(
                        id=VectorStoreUtils.generate_query_id(query.question),
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
                self.vector_store.client.upsert(
                    collection_name=self.vector_store.collection_name, points=points
                )

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
            response = self.vector_store.client.delete(
                collection_name=self.vector_store.collection_name,
                points_selector=models.PointIdsList(points=point_ids),
            )
            # Check if operation was successful
            if response.status == UpdateStatus.COMPLETED:
                logger.debug(f"Successfully deleted {len(point_ids)} points")
                return True
            else:
                logger.error(f"Points deletion failed with status: {response.status}")
                return False

        except Exception as e:
            logger.error(f"Failed to delete points: {str(e)}")
            return False

    def update_vectors(self, points: Dict[str, List[float]]) -> bool:
        """
        Update vectors for existing points without changing their payloads.

        This is useful when the embedding model has changed but the metadata
        remains the same.

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

            self.vector_store.client.batch_update_points(
                collection_name=self.vector_store.collection_name,
                update_operations=[operation],
            )
            logger.debug(f"Successfully updated vectors for {len(points)} points")
            return True

        except Exception as e:
            logger.error(f"Failed to update vectors: {str(e)}")
            return False
