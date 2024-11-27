from abc import ABC, abstractmethod
from typing import Optional, List, Generic, TypeVar
from dataclasses import dataclass

from qdrant_client import QdrantClient
from qdrant_client.http import models

from vectorstore.base.base_vectorstore_client import BaseVectorStoreClient, VectorPoint

class QdrantClient(BaseVectorStoreClient):
    """Implementazione del client per Qdrant"""
    
    def __init__(self,
                 collection_name: str,
                 path: Optional[str] = None,
                 url: Optional[str] = None,
                 api_key: Optional[str] = None) -> None:
        """Inizializza il client Qdrant
        
        Args:
            collection_name: Nome della collection
            path: Path per storage locale
            url: URL del server remoto
            api_key: API key per autenticazione
        """
        
        if path:
            self.client = QdrantClient(path=path)
        elif url:
            self.client = QdrantClient(url=url, api_key=api_key) 
        else:
            raise ValueError("Either path or url must be specified")
            
        self.collection_name = collection_name
        self._models = models
    
    def connect(self) -> bool:
        """Verifica la connessione con Qdrant"""
        try:
            self.client.get_collections()
            return True
        except Exception as e:
            print(f"Failed to connect to Qdrant: {e}")
            return False
    
    def create_collection(self,
                         collection_name: str,
                         vector_size: int) -> bool:
        """Crea una collection in Qdrant"""
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=self._models.VectorParams(
                    size=vector_size,
                    distance=self._models.Distance.COSINE
                )
            )
            return True
        except Exception as e:
            print(f"Failed to create collection: {e}")
            return False
    
    def collection_exists(self, collection_name: str) -> bool:
        """Verifica se una collection esiste in Qdrant"""
        try:
            collections = self.client.get_collections().collections
            return any(c.name == collection_name for c in collections)
        except Exception as e:
            print(f"Failed to check collection existence: {e}")
            return False
    
    def add_points(self,
                  collection_name: str,
                  points: List[VectorPoint]) -> bool:
        """Aggiunge punti in Qdrant"""
        try:
            qdrant_points = [
                self._models.PointStruct(
                    id=p.id,
                    vector=p.vector,
                    payload=p.payload
                ) for p in points
            ]
            
            self.client.upsert(
                collection_name=collection_name,
                points=qdrant_points
            )
            return True
        except Exception as e:
            print(f"Failed to add points: {e}")
            return False

    def get_points(self,
                  collection_name: str,
                  point_ids: List[str]) -> List[VectorPoint]:
        """Recupera punti specifici da Qdrant"""
        try:
            results = self.client.retrieve(
                collection_name=collection_name,
                ids=point_ids
            )
            
            return [
                VectorPoint(
                    id=str(point.id),
                    vector=point.vector,
                    payload=point.payload
                ) for point in results
            ]
        except Exception as e:
            print(f"Failed to get points: {e}")
            return []
    
    def close(self) -> None:
        """Chiude la connessione con Qdrant"""
        if hasattr(self, 'client'):
            self.client.close()