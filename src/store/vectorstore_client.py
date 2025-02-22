import uuid
from abc import ABC, abstractmethod
from src.models.vector_store import QueryPayload
from src.models.metadata import Metadata


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
    def add_table(self, payload: Metadata) -> bool:
        """Aggiunge una tabella al vectorstore"""
        pass

    @abstractmethod
    def add_query(self, query: QueryPayload) -> bool:
        """Aggiunge una query al vectorstore"""
        pass

    def _generate_table_id(self, table_name: str) -> str:
        """Genera un ID deterministico per una tabella"""
        # Usiamo UUID5 che genera un UUID deterministico basato su namespace + nome
        # NAMESPACE_DNS è solo un namespace arbitrario ma costante
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"table_{table_name}"))

    def _generate_column_id(self, table_name: str, column_name: str) -> str:
        """Genera un ID deterministico per una colonna"""
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"column_{table_name}_{column_name}"))

    def _generate_query_id(self, question: str) -> str:
        """Genera un ID deterministico per una query"""
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, question))

    @abstractmethod
    def _verify_connection(self) -> bool:
        """Verifica la connessione al vector store"""
        pass

    def close(self) -> None:
        """Chiude la connessione al vector store"""
        self.client.close()
