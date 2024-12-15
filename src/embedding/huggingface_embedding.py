from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
from src.embedding.base_embedding_model import EmbeddingModel

class HuggingFaceEmbedding(EmbeddingModel):
    """Embedding model implementation using HuggingFace's sentence-transformers"""

    def __init__(self, model_name: str = "sentence-transformers/multi-qa-MiniLM-L6-cos-v1"):
        """Initialize the HuggingFace embedding model
        
        Args:
            model_name: Name of the pre-trained model to use
        """
        self.model = SentenceTransformer(model_name)
        
    def encode(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """Convert text to embedding using sentence-transformers
        
        Args:
            text: Text or list of texts to encode
            
        Returns:
            Embedding vector(s)
        """
        embeddings = self.model.encode(text)
        if isinstance(text, str):
            return embeddings.tolist()
        return [embedding.tolist() for embedding in embeddings]
    
    def get_embedding_dimension(self) -> int:
        """Get the embedding dimension from the model
        
        Returns:
            int: Dimension of embedding vectors
        """
        return self.model.get_sentence_embedding_dimension()