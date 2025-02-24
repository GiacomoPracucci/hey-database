from typing import List
from qdrant_client.http import models
from src.models.vector_store import (
    TablePayload,
    TableSearchResult,
    ColumnPayload,
    ColumnSearchResult,
    QuerySearchResult,
)
from src.store.qdrant.qdrant_client import QdrantStore
from src.store.vectorstore_search import StoreSearch

import logging

logger = logging.getLogger("hey-database")


class QdrantSearch(StoreSearch):
    """
    Classe per il recupero di informazioni da un database vettoriale Qdrant.
    Permette di cercare tabelle, colonne e query simili alla domanda utente.
    Per i commenti ai metodi rifarsi alla classe padre

    Attributes:
        vector_store (VectorStore): Istanza del vector store per l'accesso al database Qdrant
    """

    def __init__(self, vector_store: QdrantStore):
        """Prende in input lo store dal quale recuperare le informazioni

        Args:
            vector_store: Istanza di VectorStore per l'interazione con Qdrant
        """

        self.vector_store = vector_store

    def _search_points_by_type(self, vector: List[float], type_value: str, limit: int):
        """Esegue una ricerca nel database Qdrant per un tipo specifico di entità"""

        # filtro base che ricerca i documenti per tipologia (tabella, colonna, query)
        must_conditions = [
            models.FieldCondition(key="type", match=models.MatchValue(value=type_value))
        ]

        return self.vector_store.client.search(
            collection_name=self.vector_store.collection_name,
            query_vector=vector,
            query_filter=models.Filter(must=must_conditions),
            limit=limit,
        )

    def search_tables(self, question: str, limit: int = 3) -> List[TableSearchResult]:
        """Trova le tabelle più rilevanti per domanda utente usando similarità del coseno"""
        try:
            vector = self.embedding_model.encode(question)

            search_result = self._search_points_by_type(
                vector=vector, type_value="table", limit=limit
            )

            return [self._convert_to_table_result(hit) for hit in search_result]

        except Exception as e:
            logger.error(f"Errore nella ricerca delle tabelle: {str(e)}")
            return []

    def _convert_to_table_result(self, hit) -> TableSearchResult:
        """Utility per convertire un risultato di ricerca in TableSearchResult"""
        return TableSearchResult(
            id=hit.id,
            table_name=hit.payload["table_name"],
            metadata=TablePayload(**hit.payload),
            relevance_score=hit.score,
        )

    def search_columns(self, question: str, limit: int = 5) -> List[ColumnSearchResult]:
        try:
            vector = self.vector_store.embedding_model.encode(question)
            search_result = self._search_with_filter(
                vector=vector, type_value="column", limit=limit
            )

            return [self._convert_to_column_result(hit) for hit in search_result]

        except Exception as e:
            logger.error(f"Error searching similar columns: {str(e)}")
            return []

    def _convert_to_column_result(self, hit) -> ColumnSearchResult:
        """Utility per convertire un risultato di ricerca in ColumnSearchResult"""
        return ColumnSearchResult(
            id=hit.id,
            column_name=hit.payload["column_name"],
            column_name_alias=hit.payload["column_name_alias"],
            table_name=hit.payload["table_name"],
            metadata=ColumnPayload(**hit.payload),
            relevance_score=hit.score,
        )

    def search_queries(self, question: str, limit: int = 3) -> List[QuerySearchResult]:
        try:
            vector = self.vector_store.embedding_model.encode(question)
            search_result = self._search_with_filter(
                vector=vector, type_value="query", limit=limit
            )

            return [self._convert_to_query_result(hit) for hit in search_result]

        except Exception as e:
            logger.error(f"Error searching similar queries: {str(e)}")
            return []

    def _convert_to_query_result(self, hit) -> QuerySearchResult:
        """Utility per convertire un risultato di ricerca in QuerySearchResult"""
        return QuerySearchResult(
            id=hit.id,
            question=hit.payload["question"],
            sql_query=hit.payload["sql_query"],
            explanation=hit.payload["explanation"],
            score=hit.score,
            positive_votes=hit.payload["positive_votes"],
        )
