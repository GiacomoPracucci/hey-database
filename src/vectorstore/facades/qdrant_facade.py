from typing import Dict, List, Optional

from src.embedding.base_embedding_model import EmbeddingModel
from src.vectorstore.facades.base_vectorstore_facade import BaseVectorStoreFacade
from src.vectorstore.services.implementations.qdrant_metadata_service import QdrantMetadataService
from src.vectorstore.services.implementations.qdrant_search_service import QdrantSearchService
from src.vectorstore.services.implementations.qdrant_feedback_service import QdrantFeedbackService

class QdrantVectorStoreFacade(BaseVectorStoreFacade):
    """Implementazione della facade per Qdrant"""
    
    @classmethod
    def create(cls,
              collection_name: str,
              embedding_model: EmbeddingModel,
              path: Optional[str] = None,
              url: Optional[str] = None,
              api_key: Optional[str] = None) -> 'QdrantVectorStoreFacade':
        """Factory method per creare un'istanza della facade
        
        Args:
            collection_name: Nome della collection
            embedding_model: Modello per gli embedding
            path: Path per storage locale
            url: URL del server remoto
            api_key: API key per il server
            
        Returns:
            QdrantVectorStoreFacade: Nuova istanza della facade
        """
        from src.vectorstore.implementations.qdrant_client import QdrantClient
        from src.vectorstore.services.implementations.qdrant_metadata_service import QdrantMetadataService
        from src.vectorstore.services.implementations.qdrant_search_service import QdrantSearchService
        from src.vectorstore.services.implementations.qdrant_feedback_service import QdrantFeedbackService
        
        # Crea il client
        client = QdrantClient(
            collection_name=collection_name,
            path=path,
            url=url,
            api_key=api_key
        )
        
        # Verifica la connessione
        if not client.connect():
            raise ConnectionError("Failed to connect to Qdrant")
        
        # Crea i servizi
        metadata_service = QdrantMetadataService(client, embedding_model)
        search_service = QdrantSearchService(client, embedding_model)
        feedback_service = QdrantFeedbackService(client, embedding_model)
        
        # Crea e restituisce la facade
        return cls(
            metadata_service=metadata_service,
            search_service=search_service,
            feedback_service=feedback_service
        )
    
    def __init__(self,
                 metadata_service: QdrantMetadataService,
                 search_service: QdrantSearchService,
                 feedback_service: QdrantFeedbackService):
        """Inizializza la facade con i servizi Qdrant"""
        super().__init__(metadata_service, search_service, feedback_service)