import logging
import uuid
from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams

from src.store.base_vectorstore import VectorStore
from src.embedding.base_embedding_model import EmbeddingModel
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
        
    def initialize(self) -> bool:
        """Inizializza la collection se non esiste"""
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
            return True
            
        except Exception as e:
            print(f"Errore nell'inizializzazione della collection: {str(e)}")
            return False

    def add_table(self, metadata: TablePayload) -> bool:
        """Aggiunge o aggiorna i metadati di una tabella"""
        try:
            # embedding dalla descrizione e keywords
            embedding_text = f"{metadata.table_name} {metadata.description} {' '.join(metadata.keywords)}"
            vector = self.embedding_model.encode(embedding_text)
            
            # conversione del payload in dict
            payload_dict = {
                "type": metadata.type,
                "embedding_source": metadata.embedding_source,
                "table_name": metadata.table_name,
                "description": metadata.description,
                "keywords": metadata.keywords,
                "columns": metadata.columns,
                "primary_keys": metadata.primary_keys,
                "foreign_keys": metadata.foreign_keys,
                "row_count": metadata.row_count,
                "importance_score": metadata.importance_score
            }
            
            # upsert del punto
            self.client.upsert(
                collection_name=self.collection_name,
                points=[models.PointStruct(
                    id=self._generate_table_id(metadata.table_name),
                    vector=vector,
                    payload=payload_dict
                )]
            )
            logger.debug(f"Metadati aggiunti/aggiornati per tabella: {metadata.table_name}")
            return True
        
        except Exception as e:
            logger.error(f"Errore nell'aggiunta dei metadati: {str(e)}")
            return False
        
    def get_relevant_tables(self, query: str, limit: int = 3) -> List[TableSearchResult]:
        """Trova le tabelle più rilevanti per una query
        TODO implementazione base che sfrutta solo similarità del coseno, va arricchita e strutturata maggiormente
        """
        try:
            vector = self.embedding_model.encode(query)
            
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=vector,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition( # cerchiamo solo nei documenti type = "table"
                            key="type",
                            match=models.MatchValue(value="table")
                        )
                    ]
                ),
                limit=limit
            )
        
            results = []
            for hit in search_result:
                payload = hit.payload

                # ricotruzione dell'oggetto TableMetadataPayload
                metadata = TablePayload(
                    table_name=payload["table_name"],
                    description=payload["description"],
                    keywords=payload["keywords"],
                    columns=payload["columns"],
                    primary_keys=payload["primary_keys"],
                    foreign_keys=payload["foreign_keys"],
                    row_count=payload["row_count"],
                    embedding_source=payload["embedding_source"],
                    importance_score=payload.get("importance_score", 0.0)
                )
                
                # keywords che hanno fatto match
                query_words = set(query.lower().split())
                matched_keywords = [
                    k for k in metadata.keywords 
                    if k.lower() in query_words
                ]
                
                results.append(TableSearchResult(
                    table_name=metadata.table_name,
                    metadata=metadata,
                    relevance_score=hit.score,
                    matched_keywords=matched_keywords
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"Errore nella ricerca delle tabelle: {str(e)}")
            return []
        
        
    def add_query(self, query: QueryPayload) -> bool:
        """Aggiunge una nuova query allo store"""
        try:
            vector = self.embedding_model.encode(query.question)
            
            payload_dict = {
                "type": query.type,
                "embedding_source": query.embedding_source,
                "question": query.question,
                "sql_query": query.sql_query,
                "explanation": query.explanation,
                "positive_votes": query.positive_votes
            }
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[models.PointStruct(
                    id=self._generate_query_id(query.question),
                    vector=vector,
                    payload=payload_dict
                )]
            )
            return True
            
        except Exception as e:
            logger.error(f"Errore nell'aggiunta della query: {str(e)}")
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
            logger.error(f"Errore nella ricerca delle query: {str(e)}")
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
                positive_votes=votes,
                embedding_source="question"
            )
            
            return self.add_query(query)
            
        except Exception as e:
            logger.error(f"Errore nella gestione del feedback: {str(e)}")
            return False

    def _generate_table_id(self, table_name: str) -> str:
        """Genera un ID deterministico per una tabella"""
        return f"table_{table_name}"
    
    def _generate_query_id(self, question: str) -> str:
        """Genera un ID deterministico per una query"""
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, question))