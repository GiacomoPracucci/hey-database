import logging

from src.models.vector_store import VectorStoreConfig
from src.models.embedding import EmbeddingConfig

from src.embedding.huggingface_embedding import HuggingFaceEmbedding
from src.embedding.openai_embedding import OpenAIEmbedding

from src.store.qdrant_vectorstore import QdrantStore

logger = logging.getLogger("hey-database")


class VectorStoreFactory:
    """Factory per la creazione dei componenti vector store"""

    @staticmethod
    def create_embedding_model(config: EmbeddingConfig):
        """Crea il modello di embedding appropriato"""
        if config.type == "huggingface":
            return HuggingFaceEmbedding(model_name=config.model_name)
        elif config.type == "openai":
            if not config.api_key:
                raise ValueError("OpenAI API key is required for OpenAI embeddings")
            return OpenAIEmbedding(api_key=config.api_key, model=config.model_name)
        else:
            raise ValueError(f"Embedding type {config.type} not supported")

    @staticmethod
    def create(config: VectorStoreConfig):
        """Crea il vector store appropriato"""
        if not config or not config.enabled:
            return None

        if config.type == "qdrant":
            embedding_model = VectorStoreFactory.create_embedding_model(
                config.embedding
            )

            if config.path and config.url:
                raise ValueError(
                    "Both path and url specified for Qdrant, only one is allowed"
                )
            if not config.path and not config.url:
                raise ValueError(
                    "Neither path nor url specified for Qdrant, please specify one"
                )

            if config.path:
                return QdrantStore(
                    path=config.path,
                    collection_name=config.collection_name,
                    embedding_model=embedding_model,
                )
            elif config.url:
                return QdrantStore(
                    url=config.url,
                    collection_name=config.collection_name,
                    api_key=config.api_key,
                    embedding_model=embedding_model,
                )
            else:
                raise ValueError("Neither path nor url specified for Qdrant")
        else:
            raise ValueError(f"Vector store type {config.type} not supported")
