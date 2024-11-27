from typing import List, Dict, Optional

from src.vectorstore.services.base_services.base_metadata_service import TablePayload
from src.vectorstore.services.base_services.base_search_service import (
    BaseSearchService, SearchResult, TableSearchResult, QuerySearchResult
)

class QdrantSearchService(BaseSearchService):
    """Implementazione del servizio di ricerca per Qdrant"""
    
    def _raw_vector_search(self, 
                          text: str, 
                          filter_conditions: Dict,
                          limit: int) -> List[SearchResult]:
        """Esegue una ricerca vettoriale grezza in Qdrant
        
        Args:
            text: Testo da cercare
            filter_conditions: Condizioni di filtro
            limit: Numero massimo di risultati
            
        Returns:
            List[SearchResult]: Risultati grezzi della ricerca
        """
        try:
            # Genera embedding per il testo
            vector = self.embedding_model.encode(text)
            
            # Prepara la query per Qdrant
            from qdrant_client.http import models
            
            must_conditions = [
                models.FieldCondition(
                    key=key,
                    match=models.MatchValue(value=value)
                ) for key, value in filter_conditions.items()
            ]
            
            # Esegue la ricerca
            results = self.client.client.search(
                collection_name=self.client.collection_name,
                query_vector=vector,
                query_filter=models.Filter(must=must_conditions),
                limit=limit
            )
            
            # Converte i risultati nel formato standard
            return [
                SearchResult(
                    payload=hit.payload,
                    score=hit.score
                ) for hit in results
            ]
            
        except Exception as e:
            print(f"Search failed: {e}")
            return []
    
    def search_similar_tables(self, 
                            question: str, 
                            limit: int = 3) -> List[TableSearchResult]:
        """Cerca tabelle simili in Qdrant"""
        # Filtra per documenti di tipo "table"
        results = self._raw_vector_search(
            text=question,
            filter_conditions={"type": "table"},
            limit=limit
        )
        
        # Converte i risultati nel formato TableSearchResult
        return [
            TableSearchResult(
                table_name=result.payload["table_name"],
                metadata=TablePayload(**{
                    k: v for k, v in result.payload.items()
                    if k in TablePayload.__annotations__
                }),
                score=result.score
            ) for result in results
        ]
    
    def search_similar_queries(self, 
                             question: str, 
                             limit: int = 3) -> List[QuerySearchResult]:
        """Cerca query simili in Qdrant"""
        # Filtra per documenti di tipo "query"
        results = self._raw_vector_search(
            text=question,
            filter_conditions={"type": "query"},
            limit=limit
        )
        
        # Converte i risultati nel formato QuerySearchResult
        return [
            QuerySearchResult(
                question=result.payload["question"],
                sql_query=result.payload["sql_query"],
                explanation=result.payload["explanation"],
                score=result.score,
                positive_votes=result.payload["positive_votes"]
            ) for result in results
        ]
    
    def find_exact_query_match(self, question: str) -> Optional[QuerySearchResult]:
        """Cerca una corrispondenza esatta della domanda in Qdrant"""
        try:
            from qdrant_client.http import models
            
            # Cerca una corrispondenza esatta
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
            )[0]  # scroll returns (results, next_page_offset)
            
            if results:
                point = results[0]
                return QuerySearchResult(
                    question=point.payload["question"],
                    sql_query=point.payload["sql_query"],
                    explanation=point.payload["explanation"],
                    score=1.0,  # match esatto = score massimo
                    positive_votes=point.payload["positive_votes"]
                )
            
            return None
            
        except Exception as e:
            print(f"Exact match search failed: {e}")
            return None