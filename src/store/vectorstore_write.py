from typing import List, Dict
from abc import ABC, abstractmethod

from src.models.metadata import TableMetadata, ColumnMetadata, QueryMetadata


class StoreWriter(ABC):
    """
    Abstract base class defining the interface for vector store writing operations.
    This class provides methods for adding or updating metadata documents
    (tables, columns, queries) in a vector database, both individually and in batch.

    The class follows the template method pattern, defining the basic structure
    of write operations while allowing specific implementations to define
    the actual storage logic.
    """

    @abstractmethod
    def add_table(self, metadata: TableMetadata) -> bool:
        """
        Add or update a table metadata document in the vector store.

        Args:
            metadata: Enhanced metadata of the table to be stored

        Returns:
            bool: True if operation was successful, False otherwise
        """
        pass

    @abstractmethod
    def add_tables_batch(self, metadata_list: List[TableMetadata]) -> Dict[str, bool]:
        """
        Add or update multiple table metadata documents in the vector store.
        This operation is more efficient than adding tables individually.

        Args:
            metadata_list: List of table metadata to be stored

        Returns:
            Dict[str, bool]: Dictionary mapping table names to operation success status
        """
        pass

    @abstractmethod
    def add_column(self, metadata: ColumnMetadata) -> bool:
        """
        Add or update a column metadata document in the vector store.

        Args:
            metadata: Enhanced metadata of the column to be stored

        Returns:
            bool: True if operation was successful, False otherwise
        """
        pass

    @abstractmethod
    def add_columns_batch(self, metadata_list: List[ColumnMetadata]) -> Dict[str, bool]:
        """
        Add or update multiple column metadata documents in the vector store.
        This operation is more efficient than adding columns individually.

        Args:
            metadata_list: List of column metadata to be stored

        Returns:
            Dict[str, bool]: Dictionary mapping column identifiers to operation success status
        """
        pass

    @abstractmethod
    def add_query(self, query: QueryMetadata) -> bool:
        """
        Add or update a query document in the vector store.
        This stores user questions along with their SQL translations and explanations.

        Args:
            query: Query payload containing the question, SQL, and explanation

        Returns:
            bool: True if operation was successful, False otherwise
        """
        pass

    @abstractmethod
    def add_queries_batch(self, queries: List[QueryMetadata]) -> Dict[str, bool]:
        """
        Add or update multiple query documents in the vector store.
        This operation is more efficient than adding queries individually.

        Args:
            queries: List of query payloads to be stored

        Returns:
            Dict[str, bool]: Dictionary mapping query identifiers to operation success status
        """
        pass

    @abstractmethod
    def delete_points(self, point_ids: List[str]) -> bool:
        """
        Delete multiple points from the vector store by their IDs.

        Args:
            point_ids: List of point IDs to delete

        Returns:
            bool: True if all deletions were successful, False otherwise
        """
        pass

    @abstractmethod
    def update_vectors(self, points: Dict[str, List[float]]) -> bool:
        """
        Update vectors for existing points in the store.

        Args:
            points: Dictionary mapping point IDs to their new vectors

        Returns:
            bool: True if all updates were successful, False otherwise
        """
        pass
