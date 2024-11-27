from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass

from src.config.models.metadata import EnhancedTableMetadata
from src.embedding.base_embedding_model import EmbeddingModel
from src.vectorstore.base.base_vectorstore_client import BaseVectorStoreClient

@dataclass
class TablePayload:
    """Payload standardizzato per i metadati delle tabelle nel vector store"""
    table_name: str
    description: str
    keywords: List[str]
    columns: List[Dict]
    primary_keys: List[str]
    foreign_keys: List[Dict]
    row_count: int
    importance_score: float
    type: str = "table"  # discriminator per distinguere i tipi di documento

class BaseMetadataService(ABC):
    """Interfaccia base per la gestione dei metadati nel vector store"""
    
    def __init__(self, 
                 client: BaseVectorStoreClient,
                 embedding_model: EmbeddingModel):
        self.client = client
        self.embedding_model = embedding_model
        self._metadata_cache: Dict[str, TablePayload] = {}
    
    @abstractmethod
    def initialize_metadata(self, metadata: Dict[str, EnhancedTableMetadata]) -> bool:
        """Inizializza il vector store con i metadati delle tabelle
        
        Args:
            metadata: Dizionario di metadati enhanced indicizzato per nome tabella
            
        Returns:
            bool: True se l'inizializzazione è avvenuta con successo
        """
        pass
    
    @abstractmethod
    def update_table_metadata(self, table_name: str, metadata: EnhancedTableMetadata) -> bool:
        """Aggiorna i metadati di una singola tabella
        
        Args:
            table_name: Nome della tabella
            metadata: Nuovi metadati della tabella
            
        Returns:
            bool: True se l'aggiornamento è avvenuto con successo
        """
        pass
    
    @abstractmethod
    def get_table_metadata(self, table_name: str) -> Optional[TablePayload]:
        """Recupera i metadati di una tabella
        
        Args:
            table_name: Nome della tabella
            
        Returns:
            Optional[TableMetadataPayload]: Metadati della tabella se esistono
        """
        pass
    
    def clear_cache(self) -> None:
        """Pulisce la cache dei metadati"""
        self._metadata_cache.clear()