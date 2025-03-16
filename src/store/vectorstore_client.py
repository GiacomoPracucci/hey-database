from abc import ABC, abstractmethod


class VectorStore(ABC):
    """Interfaccia base per i vectorstore"""

    @abstractmethod
    def initialize_collection(self) -> bool:
        """
        Initialize the vector store collection. This method:
        1. Checks if collection exists
        2. If exists, validates the vector configuration
        3. If doesn't exist, creates it with proper configuration

        Collection initialization ensures that:
        - The collection exists in the vector store
        - Vector dimensions match the embedding model
        - Distance metric is properly set

        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass

    @abstractmethod
    def is_collection_empty(self) -> bool:
        """
        Check if the vector store collection is empty.
        
        Uses collection statistics to determine if it contains any points.
        
        Returns:
            bool: True if the collection is empty or doesn't exist, False otherwise
        """
        pass

    @abstractmethod
    def _verify_connection(self) -> bool:
        """Verifica la connessione al vector store"""
        pass

    def close(self) -> None:
        """Chiude la connessione al vector store"""
        self.client.close()
