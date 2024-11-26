import logging
from typing import List, Optional, Dict
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
from dataclasses import asdict

from src.store.base_vectorstore import VectorStore
from src.embedding.base_embedding_model import EmbeddingModel
from src.config.models.metadata import EnhancedTableMetadata
from src.config.models.vector_store import (
    TablePayload,
    QueryPayload,
    TableSearchResult,
    QuerySearchResult
)

logger = logging.getLogger('hey-database')

class QdrantStore(VectorStore):
    """Implementazione del vectorstore Qdrant"""
    
    def __init__(self,
                collection_name: str,
                embedding_model: EmbeddingModel,
                path: Optional[str] = None,
                url: Optional[str] = None,
                api_key: Optional[str] = None
                ) -> None:
        """ Inizializza il client Qdrant
        
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

        self.embedding_model = embedding_model
        self.collection_name = collection_name
        self.vector_size = self.embedding_model.get_embedding_dimension()
        
    def initialize(self, enhanced_metadata: Optional[Dict[str, EnhancedTableMetadata]] = None) -> bool:
        """Inizializza la collection e opzionalmente carica i metadati"""
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                
            # se ci sono metadati da salvare nello store verifichiamo se sono già presenti
            # se non lo sono popoliamo in automatico la collection
            if enhanced_metadata:
                logger.debug("Starting metadata population check")
                for table_name, metadata in enhanced_metadata.items():
                    if not self._table_exists(table_name):
                        logger.debug(f"Adding metadata for table: {table_name}")
                        if not self.add_table(metadata):
                            logger.error(f"Error adding metadata for table: {table_name}")
                            return False
                    else:
                        logger.debug(f"Metadata already exists for table: {table_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error in store initialization: {str(e)}")
            return False
        
    def _table_exists(self, table_name: str) -> bool:
        """Verifica se i metadati di una tabella esistono già nello store"""
        try:
            response = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="type",
                            match=models.MatchValue(value="table")
                        ),
                        models.FieldCondition(
                            key="table_name",
                            match=models.MatchValue(value=table_name)
                        )
                    ]
                ),
                limit=1
            )
            return len(response[0]) > 0
        except Exception as e:
            logger.error(f"Error checking table existence: {str(e)}")
            return False

    def add_table(self, payload_metadata: EnhancedTableMetadata) -> bool:
        """Aggiunge o aggiorna un documento tabella nella collection
        
        Args:
            payload_metadata: Metadati arricchiti della tabella
        
        Returns:
            bool: True se l'operazione è andata a buon fine, False altrimenti
        """
        try:
            # costruiamo il payload nel formato stabilito a partire dai metadati arricchiti
            payload = TablePayload.from_enhanced_metadata(payload_metadata)
            
            # embedding dalla descrizione e keywords
            embedding_text = f"{payload.table_name} {payload.description} {' '.join(payload.keywords)}"
            vector = self.embedding_model.encode(embedding_text)
            
            # upsert del documento
            self.client.upsert(
                collection_name=self.collection_name,
                points=[models.PointStruct(
                    id=self._generate_table_id(payload.table_name),
                    vector=vector,
                    payload=asdict(payload)
                )]
            )
            logger.debug(f"Metadata added/updated for table: {payload.table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding table metadata: {str(e)}")
            return False
        
        
    def search_similar_tables(self, question: str, limit: int = 3) -> List[TableSearchResult]:
        """Trova le tabelle più rilevanti per domanda utente usando similarità del coseno"""
        try:
            vector = self.embedding_model.encode(question)
            
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=vector,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="type",
                            match=models.MatchValue(value="table")
                        )
                    ]
                ),
                limit=limit
            )
        
            return [
                TableSearchResult(
                    table_name=hit.payload["table_name"],
                    metadata=TablePayload(
                        type='table',
                        table_name=hit.payload["table_name"],
                        description=hit.payload["description"],
                        keywords=hit.payload["keywords"],
                        columns=hit.payload["columns"],
                        primary_keys=hit.payload["primary_keys"],
                        foreign_keys=hit.payload["foreign_keys"],
                        row_count=hit.payload["row_count"],
                        importance_score=hit.payload.get("importance_score", 0.0)
                    ),
                    relevance_score=hit.score
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
                points=[models.PointStruct(
                    id=self._generate_query_id(query.question),
                    vector=vector,
                    payload=asdict(query)
                )]
            )
            return True
            
        except Exception as e:
            logger.error(f"Error adding query: {str(e)}")
            return False
        

    def search_similar_queries(self, question: str, limit: int = 3) -> List[QuerySearchResult]:
        """Cerca query simili nel vector store"""
        try:
            vector = self.embedding_model.encode(question)
            
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=vector,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="type",
                            match=models.MatchValue(value="query")
                        )
                    ]
                ),
                limit=limit
            )
            
            return [
                QuerySearchResult(
                    question=hit.payload["question"],
                    sql_query=hit.payload["sql_query"],
                    explanation=hit.payload["explanation"],
                    score=hit.score,
                    positive_votes=hit.payload["positive_votes"]
                )
                for hit in search_result
            ]
            
        except Exception as e:
            logger.error(f"Error searching similar queries: {str(e)}")
            return []
        
        
    def handle_positive_feedback(self, question: str, sql_query: str, explanation: str) -> bool:
        """Gestisce il feedback positivo per una query"""
        try:
            # checkiamo se la domanda è già presente nello store
            search_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="type",
                            match=models.MatchValue(value="query")
                        ),
                        models.FieldCondition(
                            key="question",
                            match=models.MatchValue(value=question)
                        )
                    ]
                ),
                limit=1
            )[0]
            
            # se è già presente, semplicemente incrementiamo i voti
            if search_result:
                existing = search_result[0].payload
                votes = existing["positive_votes"] + 1
            else: # altrimenti è il primo voto
                votes = 1
            
            # crea/aggiorna in base alla situazione che si è verificata
            query = QueryPayload(
                question=question,
                sql_query=sql_query,
                explanation=explanation,
                positive_votes=votes
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
                            key="question",
                            match=models.MatchValue(value=question)
                        )
                    ]
                ),
                limit=1
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
                    positive_votes=point.payload["positive_votes"]
                )
            return None
                
        except Exception as e:
            logger.error(f"Errore nella ricerca esatta: {str(e)}")
            return None