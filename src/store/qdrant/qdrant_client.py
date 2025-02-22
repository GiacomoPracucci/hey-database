import logging
from typing import Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams

from src.store.vectorstore_client import VectorStore
from src.embedding.embedding import Embedder
from models.vector_store import (
    QueryPayload,
    QuerySearchResult,
)

logger = logging.getLogger("hey-database")


class QdrantStore(VectorStore):
    """Implementazione del vectorstore Qdrant"""

    def __init__(
        self,
        collection_name: str,
        embedding_model: Embedder,
        path: Optional[str] = None,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        """
        Inizializza il client Qdrant

        Args:
            collection_name: Nome della collezione
            path: Path per storage locale (opzionale)
            url: URL del server remoto (opzionale)
            api_key: API key per server remoto (opzionale)
            embedding_model: Modello per generare gli embedding
        """
        if path:
            self.client = QdrantClient(path=path)
        elif url:
            self.client = QdrantClient(url=url, api_key=api_key)
        else:
            raise ValueError("Neither path nor url specified")

        if not self._verify_connection():
            raise RuntimeError("Unable to establish connection to vector store")

        self.embedding_model = embedding_model
        self.collection_name = collection_name
        self.vector_size = self.embedding_model.get_embedding_dimension()

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
        try:
            exists = self.collection_exists()
            if exists:
                # For existing collections, verify vector configuration
                if not self._check_vector_size():
                    logger.error(
                        f"Vector size mismatch for collection: {self.collection_name}. "
                        f"Expected size: {self.vector_size}"
                    )
                    return False

            if not exists:
                # Create new collection with proper configuration
                logger.info(f"Creating new collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size, distance=Distance.COSINE
                    ),
                )
                logger.info(f"Collection {self.collection_name} created successfully")
            else:
                logger.info(
                    f"Collection {self.collection_name} exists with valid configuration"
                )

            return True

        except Exception as e:
            logger.error(f"Error in collection initialization: {str(e)}")
            return False

    def collection_exists(self) -> bool:
        """
        Check if the collection exists in the vector store.

        This method queries the vector store to verify the existence
        of a collection with the configured name.

        Returns:
            bool: True if collection exists, False otherwise or on error
        """
        try:
            collections = self.client.get_collections().collections
            return any(c.name == self.collection_name for c in collections)
        except Exception as e:
            logger.error(f"Error checking collection existence: {str(e)}")
            return False

    def _check_vector_size(self) -> bool:
        """
        Validate vector dimensions of an existing collection.

        This method ensures that the vector dimensions in the collection
        match the dimensions of the configured embedding model. This check
        is crucial as dimension mismatch would cause insertion/query failures.

        Returns:
            bool: True if vector dimensions match, False otherwise or on error
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            current_size = collection_info.config.params.vectors.size
            expected_size = self.vector_size

            if current_size != expected_size:
                logger.error(
                    f"Vector size mismatch. Collection: {current_size}, "
                    f"Embedding model: {expected_size}"
                )
                return False

            return True
        except Exception as e:
            logger.error(f"Error checking vector dimensions: {str(e)}")
            return False

    def _table_exists(self, table_name: str) -> bool:
        """Verifica se i metadati di una tabella esistono già nello store"""
        try:
            response = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="type", match=models.MatchValue(value="table")
                        ),
                        models.FieldCondition(
                            key="table_name", match=models.MatchValue(value=table_name)
                        ),
                    ]
                ),
                limit=1,
            )
            return len(response[0]) > 0
        except Exception as e:
            logger.error(f"Error checking table existence: {str(e)}")
            return False

    def handle_positive_feedback(
        self, question: str, sql_query: str, explanation: str
    ) -> bool:
        """Gestisce il feedback positivo per una query"""
        try:
            # checkiamo se la domanda è già presente nello store
            search_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="type", match=models.MatchValue(value="query")
                        ),
                        models.FieldCondition(
                            key="question", match=models.MatchValue(value=question)
                        ),
                    ]
                ),
                limit=1,
            )[0]

            # se è già presente, semplicemente incrementiamo i voti
            if search_result:
                existing = search_result[0].payload
                votes = existing["positive_votes"] + 1
            else:  # altrimenti è il primo voto
                votes = 1

            # se è una nuova domanda
            # crea/aggiorna in base alla situazione che si è verificata
            query = QueryPayload(
                question=question,
                sql_query=sql_query,
                explanation=explanation,
                positive_votes=votes,
            )

            return self.add_query(query)

        except Exception as e:
            logger.error(f"Errore nella gestione del feedback: {str(e)}")
            return False

    def find_exact_match(self, question: str) -> Optional[QuerySearchResult]:
        """Cerca una corrispondenza esatta della domanda nel database"""
        logger.debug(f"Cercando match esatto per: {question}")
        try:
            results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="question", match=models.MatchValue(value=question)
                        )
                    ]
                ),
                limit=1,
            )[0]  # scroll returns (results, next_page_offset)

            logger.debug(f"Risultati trovati: {len(results)}")
            if results:
                point = results[0]
                logger.debug(f"Match trovato con payload: {point.payload}")
                return QuerySearchResult(
                    question=point.payload["question"],
                    sql_query=point.payload["sql_query"],
                    explanation=point.payload["explanation"],
                    score=1.0,  # match esatto = score 1
                    positive_votes=point.payload["positive_votes"],
                )
            return None

        except Exception as e:
            logger.error(f"Errore nella ricerca esatta: {str(e)}")
            return None

    def _verify_connection(self) -> bool:
        """Verifica che il vector store sia raggiungibile
        Returns:
            bool: True se la connessione è stabilita correttamente
        """
        try:
            return self.client.get_collections() is not None
        except Exception as e:
            logger.error(f"Vector store connection check failed: {str(e)}")
            return False
