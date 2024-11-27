from typing import Optional

from src.vectorstore.base.base_vectorstore_client import VectorPoint
from src.vectorstore.services.base_services.base_search_service import QueryPayload
from src.vectorstore.services.base_services.base_feedback_service import BaseFeedbackService

class QdrantFeedbackService(BaseFeedbackService):
    """Implementazione del servizio di feedback per Qdrant"""
    
    def create_query_point(self,
                          question: str,
                          sql_query: str,
                          explanation: str,
                          positive_votes: int = 1) -> VectorPoint:
        """Crea un punto vettoriale per una query in Qdrant"""
        # Crea il payload
        payload = QueryPayload(
            question=question,
            sql_query=sql_query,
            explanation=explanation,
            positive_votes=positive_votes
        )
        
        # Genera l'embedding dalla domanda
        vector = self.embedding_model.encode(question)
        
        # Genera un ID deterministico per la query
        from uuid import uuid5, NAMESPACE_DNS
        point_id = str(uuid5(NAMESPACE_DNS, question))
        
        return VectorPoint(
            id=point_id,
            vector=vector,
            payload=payload
        )
    
    def handle_positive_feedback(self,
                               question: str,
                               sql_query: str,
                               explanation: str) -> bool:
        """Gestisce il feedback positivo in Qdrant"""
        try:
            # Verifica se la query esiste già
            from qdrant_client.http import models
            
            existing_points = self.client.client.scroll(
                collection_name=self.client.collection_name,
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
            
            if existing_points:
                # Se esiste, incrementa i voti positivi
                existing_point = existing_points[0]
                votes = existing_point.payload["positive_votes"] + 1
            else:
                # Se non esiste, inizia con un voto
                votes = 1
            
            # Crea il nuovo punto
            point = self.create_query_point(
                question=question,
                sql_query=sql_query,
                explanation=explanation,
                positive_votes=votes
            )
            
            # Salva nel vector store (upsert)
            success = self.client.add_points(
                collection_name=self.client.collection_name,
                points=[point]
            )
            
            return success
            
        except Exception as e:
            print(f"Failed to handle feedback: {e}")
            return False
        
    def get_feedback_stats(self, question: str) -> Optional[dict]:
        """Recupera le statistiche di feedback per una query
        
        Args:
            question: Domanda dell'utente
            
        Returns:
            Optional[dict]: Statistiche del feedback se trovate
        """
        try:
            from qdrant_client.http import models
            
            results = self.client.client.scroll(
                collection_name=self.client.collection_name,
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
            
            if results:
                point = results[0]
                return {
                    "positive_votes": point.payload["positive_votes"],
                    "sql_query": point.payload["sql_query"],
                    "explanation": point.payload["explanation"]
                }
            
            return None
            
        except Exception as e:
            print(f"Failed to get feedback stats: {e}")
            return None