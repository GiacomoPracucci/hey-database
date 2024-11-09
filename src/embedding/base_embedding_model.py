from abc import ABC, abstractmethod
from typing import List, Union

class EmbeddingModel(ABC):
    """Base class for embedding models that convert text to vector representations"""
    
    @abstractmethod
    def encode(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """Converts text or list of texts into embeddings
        
        Args:
            text: Single text string or list of text strings to encode
            
        Returns:
            Single embedding vector or list of embedding vectors
        """
        pass
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """Returns the dimension of the embedding vectors
        
        Returns:
            int: Dimension of embedding vectors
        """
        pass
    
    def encode_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Encodes a list of texts in batches
        
        Args:
            texts: List of texts to encode
            batch_size: Number of texts to process in each batch
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.encode(batch)
            embeddings.extend(batch_embeddings)
        return embeddings