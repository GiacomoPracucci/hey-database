from typing import Dict, List, Optional

from src.embedding.base_embedding_model import EmbeddingModel
from src.vectorstore.base.base_vectorstore_client import BaseVectorStoreClient
from src.vectorstore.services.base_services.base_metadata_service import (
    BaseMetadataService, 
    TablePayload
)
from src.vectorstore.services.base_services.base_search_service import (
    BaseSearchService,
    TableSearchResult,
    QuerySearchResult
)
from src.vectorstore.services.base_services.base_feedback_service import BaseFeedbackService
from src.config.models.metadata import EnhancedTableMetadata

class BaseVectorStoreFacade:
    """Interfaccia base per la facade del vector store"""
    
    def __init__(self,
                 metadata_service: BaseMetadataService,
                 search_service: BaseSearchService,
                 feedback_service: BaseFeedbackService):
        self.metadata_service = metadata_service
        self.search_service = search_service
        self.feedback_service = feedback_service
    
    def initialize_store(self, metadata: Dict[str, EnhancedTableMetadata]) -> bool:
        """Inizializza il vector store con i metadati
        
        Args:
            metadata: Metadati delle tabelle
            
        Returns:
            bool: True se l'inizializzazione è riuscita
        """
        return self.metadata_service.initialize_metadata(metadata)
    
    def search_similar_tables(self, question: str, limit: int = 3) -> List[TableSearchResult]:
        """Cerca tabelle simili alla domanda dell'utente"""
        return self.search_service.search_similar_tables(question, limit)
    
    def search_similar_queries(self, question: str, limit: int = 3) -> List[QuerySearchResult]:
        """Cerca query simili alla domanda dell'utente"""
        return self.search_service.search_similar_queries(question, limit)
    
    def find_exact_match(self, question: str) -> Optional[QuerySearchResult]:
        """Cerca una corrispondenza esatta per la domanda"""
        return self.search_service.find_exact_query_match(question)
    
    def handle_positive_feedback(self, question: str, sql_query: str, explanation: str) -> bool:
        """Gestisce il feedback positivo dell'utente"""
        return self.feedback_service.handle_positive_feedback(question, sql_query, explanation)
    
    def get_table_metadata(self, table_name: str) -> Optional[TablePayload]:
        """Recupera i metadati di una tabella"""
        return self.metadata_service.get_table_metadata(table_name)
    
    def update_table_metadata(self, table_name: str, metadata: EnhancedTableMetadata) -> bool:
        """Aggiorna i metadati di una tabella"""
        return self.metadata_service.update_table_metadata(table_name, metadata)