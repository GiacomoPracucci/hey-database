import logging
from dataclasses import dataclass

from src.models.vector_store import VectorStoreConfig
from src.models.embedding import EmbeddingConfig
from src.embedding.huggingface_embedding import HuggingFaceEmbedding
from src.embedding.openai_embedding import OpenAIEmbedding
from src.store.qdrant.qdrant_client import QdrantStore
from src.store.qdrant.qdrant_writer import QdrantWriter
from src.store.qdrant.qdrant_search import QdrantSearch

logger = logging.getLogger("hey-database")


@dataclass
class VectorStoreComponents:
    """
    Container for all vector store related components.
    Ensures all components are coherently implemented for the same store type.
    """

    store: QdrantStore
    writer: QdrantWriter
    search: QdrantSearch


class VectorStoreFactory:
    """
    Factory class responsible for creating vector store components.
    Handles the creation of the main store, embedding models, and related
    components (writer, search) ensuring they are all compatible.

    The factory supports different vector store implementations and their
    corresponding embedding models. Currently supported:
    - Stores: Qdrant
    - Embeddings: HuggingFace, OpenAI
    """

    @staticmethod
    def create_embedding_model(config: EmbeddingConfig):
        """
        Create an appropriate embedding model based on configuration.

        Supports multiple embedding model implementations with their
        specific initialization requirements.

        Args:
            config: Configuration for the embedding model

        Returns:
            Initialized embedding model instance

        Raises:
            ValueError: If embedding type is not supported or required
                      configuration is missing
        """
        if config.type == "huggingface":
            return HuggingFaceEmbedding(model_name=config.model_name)
        elif config.type == "openai":
            if not config.api_key:
                raise ValueError("OpenAI API key is required for OpenAI embeddings")
            return OpenAIEmbedding(api_key=config.api_key, model=config.model_name)
        else:
            raise ValueError(f"Embedding type {config.type} not supported")

    @staticmethod
    def create(config: VectorStoreConfig) -> VectorStoreComponents:
        """
        Create a complete vector store setup including main store, writer, and search components.

        This method serves as the main factory method, creating and connecting all
        necessary components for a functional vector store system.

        Args:
            config: Complete vector store configuration including store type,
                   connection details, and embedding configuration

        Returns:
            VectorStoreComponents containing initialized store, writer, and search components

        Raises:
            ValueError: If store type is not supported or configuration is invalid
        """
        if not config.type == "qdrant":
            raise ValueError(f"Vector store type {config.type} not supported")

        # Create embedding model first as it's needed by multiple components
        embedding_model = VectorStoreFactory.create_embedding_model(config.embedding)

        # Validate Qdrant-specific configuration
        if config.path and config.url:
            raise ValueError(
                "Both path and url specified for Qdrant, only one is allowed"
            )
        if not config.path and not config.url:
            raise ValueError(
                "Neither path nor url specified for Qdrant, please specify one"
            )

        # Create main store
        store = QdrantStore(
            path=config.path if config.path else None,
            url=config.url if config.url else None,
            collection_name=config.collection_name,
            api_key=config.api_key,
            embedding_model=embedding_model,
        )

        # Create additional components
        writer = QdrantWriter(store)
        search = QdrantSearch(store)

        return VectorStoreComponents(store=store, writer=writer, search=search)
