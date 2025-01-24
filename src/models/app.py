from dataclasses import dataclass
from src.config.models.db import DatabaseConfig
from src.config.models.llm import LLMConfig
from src.config.models.prompt import PromptConfig
from src.config.models.vector_store import VectorStoreConfig
from src.config.models.cache import CacheConfig
from src.config.models.metadata import MetadataConfig

from src.connettori.db import DatabaseConnector
from src.llm_handler import LLMHandler
from src.cache.metadata_cache import MetadataCache
from src.vector_store.vector_store import VectorStore
from src.metadata.metadata_retriever import MetadataRetriever

from src.config.models.base import BaseConfig


@dataclass
class AppConfig:
    database: DatabaseConfig
    sql_llm: LLMConfig
    prompt: PromptConfig
    cache: CacheConfig
    metadata: MetadataConfig
    vector_store: VectorStoreConfig
    base_config: BaseConfig


@dataclass
class AppComponents:
    database: DatabaseConnector
    vector_store: VectorStore
    sql_llm: LLMHandler
    cache: MetadataCache
    metadata_extractor: MetadataRetriever
