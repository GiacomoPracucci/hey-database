from typing import List, Optional
from datetime import datetime, timezone
import logging
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer
from src.config.models import QueryStorePayload, SearchResult
from src.store.base_vectorstore import VectorStore
from src.embedding.base_embedding_model import EmbeddingModel

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
        
    def _payload_to_dict(self, payload: QueryStorePayload) -> dict:
        """Converte un QueryStorePayload in un dizionario per Qdrant"""
        return {
            "question": payload.question,
            "sql_query": payload.sql_query,
            "explanation": payload.explanation,
            "positive_votes": payload.positive_votes,
        }
        
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
        
    def handle_positive_feedback(self, question: str, sql_query: str, explanation: str) -> bool:
        """Gestisce il feedback positivo dell'utente per una coppia domanda-risposta.
        Se la coppia esiste, incrementa il contatore. Se non esiste, crea una nuova entry.
        
        Args:
            question: La domanda dell'utente
            sql_query: La query SQL generata
            
        Returns:
            bool: True se l'operazione ha successo, False altrimenti
        """
        try:
            logger.debug(f"Ricevuto feedback positivo per la domanda: {question}")
            
            existing = self.find_exact_match(question)
            vector = self.embedding_model.encode(question)
            
            if existing:
                logger.debug(f"Trovata entry esistente")
                payload = QueryStorePayload(
                    question=existing.question,
                    sql_query=existing.sql_query,
                    explanation=existing.explanation,
                    positive_votes=existing.positive_votes + 1
                )
                logger.debug(f"Aggiornamento voti a {payload.positive_votes}")
            else:
                logger.debug("Creazione nuova entry")

                payload = QueryStorePayload(
                    question=question,
                    sql_query=sql_query,
                    explanation=explanation,
                    positive_votes=1
                )
                
            success = self.client.upsert(
                collection_name=self.collection_name,
                points=[models.PointStruct(
                    id=self._generate_id(question),
                    vector=vector,
                    payload=self._payload_to_dict(payload)
                )]
            )
            logger.debug(f"Upsert completato con successo: {success}")
            return success
        
        except Exception as e:
                logger.error(f"Errore nella gestione del feedback: {str(e)}")
                return False

    def find_exact_match(self, question: str) -> Optional[SearchResult]:
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
                return SearchResult(
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
                
            
    def add_entry(self, question: str, sql_query: str, explanation: str) -> bool:
        """Aggiunge una nuova entry nel vector store"""
        try:
            vector = self.embedding_model.encode(question)
            
            current_time = datetime.now(timezone.utc)
            payload = QueryStorePayload(
                question=question,
                sql_query=sql_query,
                explanation=explanation,
                positive_votes=0
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[models.PointStruct(
                    id=self._generate_id(question),
                    vector=vector,
                    payload=self._payload_to_dict(payload)
                )]
            )
            return True
            
        except Exception as e:
            print(f"Errore nell'inserimento: {str(e)}")
            return False
        
    def search_similar(self, question: str, limit: int = 3) -> List[SearchResult]:
        """Cerca domande simili utilizzando la similarity search di Qdrant"""
        try:
            vector = self.embedding_model.encode(question)
            
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=vector,
                limit=limit
            )
            
            return [ # restituiamo rispettando il formato definito 
                SearchResult(
                    question=r.payload["question"],
                    sql_query=r.payload["sql_query"],
                    explanation=r.payload["explanation"],
                    score=r.score
                )
                for r in results
            ]
        
        except Exception as e:
            print(f"Errore nella ricerca: {str(e)}")
            return []
        
        
    def _generate_id(self, question: str) -> str:
        """Genera un UUID v5 deterministico basato sulla domanda"""
        # Usiamo UUID v5 che genera un UUID deterministico basato su namespace + nome
        # NAMESPACE_DNS è solo un namespace arbitrario ma costante
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, question))
    

    def close(self) -> None:
        """Chiude la connessione al vector store"""
        self.client.close()