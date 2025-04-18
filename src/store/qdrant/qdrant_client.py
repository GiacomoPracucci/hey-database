import logging
from typing import Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams

from src.store.vectorstore_client import VectorStore
from src.embedding.embedding import Embedder
from src.models.vector_store import QuerySearchResult
from src.models.metadata import QueryMetadata

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
        sync_on_startup: bool = True,
    ) -> None:
        """
        Inizializza il client Qdrant

        Args:
            collection_name: Nome della collezione
            path: Path per storage locale (opzionale)
            url: URL del server remoto (opzionale)
            api_key: API key per server remoto (opzionale)
            embedding_model: Modello per generare gli embedding
            sync_on_startup: Se sincronizzare i metadati all'avvio (default: True)
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
        self.sync_on_startup = sync_on_startup

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
        
    def is_collection_empty(self) -> bool:
        """
        Check if the vector store collection is empty.
        
        Uses collection statistics to determine if it contains any points.

        This is the cleaneast way to check if a collection is empty, but 
        get_collection in some cases returns "points_count" None even if there are points.

        So I also implemented _is_collection_empty below that do the same thing but in a different way.
        In vector store startup, the other method is used, until this cleaner way is fixed. 
        
        Returns:
            bool: True if the collection is empty or doesn't exist, False otherwise
        """
        try:
            # Check if collection exists first
            if not self.collection_exists():
                return True
                
            # Get collection info which includes point count
            collection_info = self.client.get_collection(self.collection_name)
            
            # Check points_count directly
            points_count = collection_info.vectors_count
            logger.debug(f"Collection {self.collection_name} contains {points_count} points")
            
            if points_count is None:
                # If count is not available, assume it's empty
                return True

            return points_count == 0 # return True if empty, False otherwise
            
        except Exception as e:
            logger.warning(f"Error checking if collection {self.collection_name} is empty: {str(e)}")
            # In case of error, assume it's empty for safety
            return True
        
    def _is_collection_empty(self) -> bool:
        """
        Check if the vector store collection is empty.
        
        This method queries the collection to determine if it contains any points/documents.
        It's useful for initialization logic that needs to determine if a collection
        is newly created or already populated.
        
        Returns:
            bool: True if the collection is empty or doesn't exist, False otherwise
        """
        try:
            # Check if collection exists first
            if not self.collection_exists():
                logger.debug(f"Collection {self.collection_name} doesn't exist, considering it empty")
                return True
                
            # Execute a minimal query that returns at most 1 point to check if collection has any data
            result = self.client.scroll(
                collection_name=self.collection_name,
                limit=1
            )
            
            # result[0] contains the list of points, if empty the collection is empty
            is_empty = len(result[0]) == 0
            logger.debug(f"Collection {self.collection_name} is {'empty' if is_empty else 'not empty'}")
            return is_empty
            
        except Exception as e:
            logger.warning(f"Error checking if collection {self.collection_name} is empty: {str(e)}")
            # In case of error, assume it's empty for safety
            return True

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
