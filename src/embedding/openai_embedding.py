from typing import List, Union
import numpy as np
from openai import OpenAI
from src.embedding.base_embedding_model import EmbeddingModel

class OpenAIEmbedding(EmbeddingModel):
    """Embedding model implementation using OpenAI's API"""
    
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        """Initialize the OpenAI embedding model
        
        Args:
            api_key: OpenAI API key
            model: Name of the OpenAI embedding model to use
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self._embedding_dimension = self._get_model_dimension()
        
    def encode(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """Convert text to embedding using OpenAI's API
        
        Args:
            text: Text or list of texts to encode
            
        Returns:
            Embedding vector(s)
        """
        if isinstance(text, str):
            text = [text]
            
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        embeddings = [data.embedding for data in response.data]
        return embeddings[0] if len(embeddings) == 1 else embeddings

    def get_embedding_dimension(self) -> int:
        """Get the embedding dimension for the current model
        
        Returns:
            int: Dimension of embedding vectors
        """
        return self._embedding_dimension
    
    def _get_model_dimension(self) -> int:
        """Determine the embedding dimension for the chosen model
        
        Returns:
            int: Embedding dimension
        """
        # dimensioni note dei modelli di embedding OpenAI
        dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536
        }
        return dimensions.get(self.model, 1536) 