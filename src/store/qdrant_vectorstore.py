import logging
from typing import List, Optional, Dict
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
from dataclasses import asdict

from src.store.vectorstore import VectorStore
from src.embedding.embedding import Embedder
from src.models.metadata import EnhancedTableMetadata, EnhancedColumnMetadata
from src.models.vector_store import (
    TablePayload,
    QueryPayload,
    TableSearchResult,
    QuerySearchResult,
)

logger = logging.getLogger("hey-database")


class QdrantStore(VectorStore):
    """Implementazione del vectorstore Qdrant
    TODO sta classe è arrivata a fare troppa roba, andrebbero divisi i vari servizi che offre
    TODO disassociare il concetto di metadati enhanced allo store e integrarlo all'estrazione dei metadati dallo schema
    """

    def __init__(
        self,
        collection_name: str,
        embedding_model: Embedder,
        path: Optional[str] = None,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        """Inizializza il client Qdrant

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

    def add_table(self, metadata: EnhancedTableMetadata) -> bool:
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

    def add_column(self, metadata: EnhancedColumnMetadata) -> bool:
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

    def search_similar_tables(
        self, question: str, limit: int = 3
    ) -> List[TableSearchResult]:
        """Trova le tabelle più rilevanti per domanda utente usando similarità del coseno"""
        try:
            vector = self.embedding_model.encode(question)

            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=vector,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="type", match=models.MatchValue(value="table")
                        )
                    ]
                ),
                limit=limit,
            )

            return [
                TableSearchResult(
                    table_name=hit.payload["table_name"],
                    metadata=TablePayload(
                        type="table",
                        table_name=hit.payload["table_name"],
                        description=hit.payload["description"],
                        keywords=hit.payload["keywords"],
                        columns=hit.payload["columns"],
                        primary_keys=hit.payload["primary_keys"],
                        foreign_keys=hit.payload["foreign_keys"],
                        row_count=hit.payload["row_count"],
                        importance_score=hit.payload.get("importance_score", 0.0),
                    ),
                    relevance_score=hit.score,
                )
                for hit in search_result
            ]

        except Exception as e:
            logger.error(f"Errore nella ricerca delle tabelle: {str(e)}")
            return []

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

    def search_similar_queries(
        self, question: str, limit: int = 3
    ) -> List[QuerySearchResult]:
        """Cerca query simili nel vector store"""
        try:
            vector = self.embedding_model.encode(question)

            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=vector,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="type", match=models.MatchValue(value="query")
                        )
                    ]
                ),
                limit=limit,
            )

            return [
                QuerySearchResult(
                    question=hit.payload["question"],
                    sql_query=hit.payload["sql_query"],
                    explanation=hit.payload["explanation"],
                    score=hit.score,
                    positive_votes=hit.payload["positive_votes"],
                )
                for hit in search_result
            ]

        except Exception as e:
            logger.error(f"Error searching similar queries: {str(e)}")
            return []

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

    def update_table_documents(
        self, enhanced_metadata: Dict[str, EnhancedTableMetadata]
    ) -> bool:
        """Aggiorna i documenti table di una collezione"""
        try:
            for table_name, metadata in enhanced_metadata.items():
                if not self.add_table(metadata):
                    logger.error(f"Failed to update metadata for table: {table_name}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Error updating metadata: {str(e)}")
            return False

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
