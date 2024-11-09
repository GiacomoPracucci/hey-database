from typing import List, Optional
from datetime import datetime, timezone
import time
import hashlib
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer
from src.config.models import QueryStorePayload, SearchResult
from src.store.base_vectorstore import VectorStore

class QdrantStore(VectorStore):
    """Implementazione del vectorstore Qdrant"""
    
    def __init__(self,
                 url: str,
                 collection_name: str,
                 api_key: Optional[str] = None,
                 embedding_model: str = "sentence-transformers/multi-qa-MiniLM-L6-cos-v1"
                 ) -> None:
        """ Inizializza il client Qdrant
        
        Args:
            url: URL del server Qdrant
            collection_name: Nome della collezione da utilizzare
            api_key: API key opzionale per l'autenticazione (per qdrant cloud)
            embedding_model: Modello da utilizzare per generare gli embedding
        """
        self.client = QdrantClient(url=url, api_key=api_key)
        self.collection_name = collection_name
        self.embedding_model = SentenceTransformer(embedding_model)
        self.vector_size = self.embedding_model.get_sentence_embedding_dimension()
        
    def _payload_to_dict(self, payload: QueryStorePayload) -> dict:
        """Converte un QueryStorePayload in un dizionario per Qdrant"""
        return {
            "question": payload.question,
            "sql_query": payload.sql_query,
            "positive_votes": payload.positive_votes,
            "created_at": payload.created_at.isoformat(),
            "last_used": payload.last_used.isoformat()
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
        
    def handle_positive_feedback(self, question: str, sql_query: str) -> bool:
        """Gestisce il feedback positivo dell'utente per una coppia domanda-risposta.
        Se la coppia esiste, incrementa il contatore. Se non esiste, crea una nuova entry.
        
        Args:
            question: La domanda dell'utente
            sql_query: La query SQL generata
            
        Returns:
            bool: True se l'operazione ha successo, False altrimenti
        """
        try:
            # cerca se esiste già una entry con questa domanda
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
            )[0]
            
            current_time = datetime.now(timezone.utc)
            
            if results:  # se esiste, aggiorna solo i voti e il timestamp
                point = results[0]
                payload = point.payload
                payload["positive_votes"] += 1
                payload["last_used"] = current_time.isoformat()
                
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=[models.PointStruct(
                        id=point.id,
                        vector=point.vector,
                        payload=payload
                    )]
                )
            else:  # se non esiste, crea una nuova entry
                vector = self.embedding_model.encode(question)
                payload = QueryStorePayload(
                    question=question,
                    sql_query=sql_query,
                    positive_votes=1,  # Inizia da 1 perché è un feedback positivo
                    created_at=current_time,
                    last_used=current_time
                )
                
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=[models.PointStruct(
                        id=self._generate_id(question),
                        vector=vector.tolist(),
                        payload=self._payload_to_dict(payload)
                    )]
                )
            return True
        
        except Exception as e:
                print(f"Errore nella gestione del feedback: {str(e)}")
                return False
                
            
    def add_entry(self, question: str, sql_query: str) -> bool:
        """Aggiunge una nuova entry nel vector store"""
        try:
            vector = self.embedding_model.encode(question)
            
            current_time = datetime.now(timezone.utc)
            payload = QueryStorePayload(
                question=question,
                sql_query=sql_query,
                positive_votes=0,
                created_at=current_time,
                last_used=current_time
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[models.PointStruct(
                    id=self._generate_id(question),
                    vector=vector.tolist(),
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
                query_vector=vector.tolist(),
                limit=limit
            )
            
            return [ # restituiamo rispettando il formato definito 
                SearchResult(
                    question=r.payload["question"],
                    sql_query=r.payload["sql_query"],
                    score=r.score,
                    positive_votes=r.payload["positive_votes"],
                    last_used=datetime.fromisoformat(r.payload["last_used"])
                )
                for r in results
            ]
        
        except Exception as e:
            print(f"Errore nella ricerca: {str(e)}")
            return []
        
    def increment_votes(self, question: str) -> bool:
        """Incrementa il contatore dei voti positivi"""
        def update(payload):
            payload["positive_votes"] += 1
            payload["last_used"] = datetime.now(timezone.utc).isoformat()
        
        return self._update_payload(question, update)
        
    def update_last_used(self, question: str) -> bool:
        """Aggiorna il timestamp di ultimo utilizzo"""
        def update(payload):
            payload["last_used"] = datetime.now(timezone.utc).isoformat()
        
        return self._update_payload(question, update)
        
        
    def _update_payload(self, question: str, updater_func) -> bool:
        """Helper per aggiornare il payload di un punto con match esatto sulla domanda.
        
        Args:
            question: La domanda da cercare
            updater_func: Funzione che riceve il payload e lo aggiorna
            
        Returns:
            bool: True se l'aggiornamento ha successo, False altrimenti
        """
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
            )[0]
            
            if not results:
                return False
                
            point = results[0]
            payload = point.payload
            updater_func(payload)
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[models.PointStruct(
                    id=point.id,
                    vector=point.vector,
                    payload=payload
                )]
            )
            return True
            
        except Exception as e:
            print(f"Errore nell'aggiornamento del payload: {str(e)}")
            return False
            
    def _generate_id(self, question: str) -> str:
        """Genera un ID combinando timestamp e hash"""
        timestamp = int(time.time() * 1000)  # millisecondi
        question_hash = hashlib.md5(question.encode('utf-8')).hexdigest()[:8]
        return f"{timestamp}-{question_hash}"


    def close(self) -> None:
        """Chiude la connessione al vector store"""
        self.client.close()