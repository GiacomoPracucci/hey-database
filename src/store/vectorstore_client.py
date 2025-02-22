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
    def handle_positive_feedback(
        self, question: str, sql_query: str, explanation: str
    ) -> bool:
        """Gestisce il feedback positivo dell'utente per una coppia domanda-risposta.
        Se la coppia esiste, incrementa il contatore. Se non esiste, crea una nuova entry."""

    pass

    @abstractmethod
    def _verify_connection(self) -> bool:
        """Verifica la connessione al vector store"""
        pass

    def close(self) -> None:
        """Chiude la connessione al vector store"""
        self.client.close()
