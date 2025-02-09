import uuid
from abc import ABC, abstractmethod
from typing import List
from src.models.vector_store import TableSearchResult, QuerySearchResult, QueryPayload
from src.models.metadata import Metadata


class VectorStore(ABC):
    """Interfaccia base per i vectorstore"""

    @abstractmethod
    def initialize(self) -> bool:
        """Inizializza la connessione e crea la collection se necessario"""
        pass

    @abstractmethod
    def handle_positive_feedback(
        self, question: str, sql_query: str, explanation: str
    ) -> bool:
        """Gestisce il feedback positivo dell'utente per una coppia domanda-risposta.
        Se la coppia esiste, incrementa il contatore. Se non esiste, crea una nuova entry."""

    pass

    @abstractmethod
    def search_similar_tables(
        self, question: str, limit: int
    ) -> List[TableSearchResult]:
        """Cerca tabelle simili nel vectorstore rispetto alla domanda dell'utente"""
        pass

    @abstractmethod
    def add_table(self, payload: Metadata) -> bool:
        """Aggiunge una tabella al vectorstore"""
        pass

    @abstractmethod
    def search_similar_queries(
        self, question: str, limit: int
    ) -> List[QuerySearchResult]:
        """Cerca domande-querysql-spiegazione simili nel vectorstore rispetto alla domanda dell'utente"""
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
