from typing import Dict, Optional

from src.config.models.metadata import EnhancedTableMetadata
from src.vectorstore.services.base_services.base_metadata_service import BaseMetadataService, TablePayload
from src.vectorstore.base.base_vectorstore_client import VectorPoint

class QdrantMetadataService(BaseMetadataService):
    """Implementazione del metadata service per Qdrant"""
    
    def _create_vector_point(self, 
                           table_name: str, 
                           metadata: EnhancedTableMetadata) -> VectorPoint:
        """Crea un punto vettoriale dai metadati di una tabella
        
        Args:
            table_name: Nome della tabella
            metadata: Metadati enhanced della tabella
            
        Returns:
            VectorPoint: Punto da inserire nel vector store
        """
        # Creiamo il payload standardizzato
        payload = TablePayload(
            table_name=table_name,
            description=metadata.description,
            keywords=metadata.keywords,
            columns=metadata.base_metadata.columns,
            primary_keys=metadata.base_metadata.primary_keys,
            foreign_keys=metadata.base_metadata.foreign_keys,
            row_count=metadata.base_metadata.row_count,
            importance_score=metadata.importance_score
        )
        
        # Generiamo l'embedding dalla descrizione e keywords
        text_for_embedding = f"{table_name} {metadata.description} {' '.join(metadata.keywords)}"
        vector = self.embedding_model.encode(text_for_embedding)
        
        # Generiamo un ID deterministico per la tabella
        point_id = f"table_{table_name}"
        
        return VectorPoint(
            id=point_id,
            vector=vector,
            payload=payload
        )
    
    def initialize_metadata(self, metadata: Dict[str, EnhancedTableMetadata]) -> bool:
        """Inizializza Qdrant con i metadati delle tabelle"""
        try:
            # Convertiamo tutti i metadati in punti vettoriali
            points = [
                self._create_vector_point(table_name, table_metadata)
                for table_name, table_metadata in metadata.items()
            ]
            
            # Li aggiungiamo in batch
            success = self.client.add_points(
                collection_name=self.client.collection_name,
                points=points
            )
            
            if success:
                # Aggiorniamo la cache con i nuovi metadati
                self._metadata_cache.update({
                    point.payload.table_name: point.payload 
                    for point in points
                })
                
            return success
            
        except Exception as e:
            print(f"Failed to initialize metadata: {e}")
            return False
    
    def update_table_metadata(self, table_name: str, metadata: EnhancedTableMetadata) -> bool:
        """Aggiorna i metadati di una tabella in Qdrant"""
        try:
            point = self._create_vector_point(table_name, metadata)
            
            success = self.client.add_points(
                collection_name=self.client.collection_name,
                points=[point]
            )
            
            if success:
                # Aggiorniamo la cache
                self._metadata_cache[table_name] = point.payload
                
            return success
            
        except Exception as e:
            print(f"Failed to update table metadata: {e}")
            return False
    
    def get_table_metadata(self, table_name: str) -> Optional[TablePayload]:
        """Recupera i metadati di una tabella da Qdrant"""
        # Prima controlliamo la cache
        if table_name in self._metadata_cache:
            return self._metadata_cache[table_name]
        
        try:
            # Se non in cache, recuperiamo da Qdrant
            points = self.client.get_points(
                collection_name=self.client.collection_name,
                point_ids=[f"table_{table_name}"]
            )
            
            if points:
                # Aggiorniamo la cache e restituiamo
                metadata = points[0].payload
                self._metadata_cache[table_name] = metadata
                return metadata
                
            return None
            
        except Exception as e:
            print(f"Failed to get table metadata: {e}")
            return None