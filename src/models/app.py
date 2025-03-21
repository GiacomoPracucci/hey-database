from typing import List
from dataclasses import field

from dataclasses import dataclass
from src.models.db import DatabaseConfig
from src.models.llm import LLMConfig
from src.models.prompt import PromptConfig
from src.models.vector_store import VectorStoreConfig
from src.models.cache import CacheConfig
from src.models.metadata import MetadataConfig

from src.connectors.connector import DatabaseConnector
from src.llm_handler.llm_handler import LLMHandler
from src.metadata.metadata_cache import MetadataCache
from src.store.vectorstore_client import VectorStore
from src.store.vectorstore_write import StoreWriter
from src.store.vectorstore_search import StoreSearch

from src.metadata.extractors.table.table_metadata_extractor import (
    TableMetadataExtractor,
)
from src.metadata.extractors.column.column_metadata_extractor import (
    ColumnMetadataExtractor,
)
from src.metadata.enhancers.table_metadata_enhancer import TableMetadataEnhancer
from src.metadata.enhancers.column_metadata_enhancer import ColumnMetadataEnhancer

from src.models.recipes import RecipeConfig, RecipesCollection

from src.models.base import BaseConfig


@dataclass
class AppConfig:
    database: DatabaseConfig
    sql_llm: LLMConfig
    prompt: PromptConfig
    cache: CacheConfig
    metadata: MetadataConfig
    vector_store: VectorStoreConfig
    base_config: BaseConfig
    recipes_configs: List[RecipeConfig] = field(default_factory=list)


@dataclass
class AppComponents:
    db: DatabaseConnector
    vector_store: VectorStore
    vector_store_writer: StoreWriter
    vector_store_searcher: StoreSearch
    sql_llm: LLMHandler
    cache: MetadataCache
    table_metadata_extractor: TableMetadataExtractor
    column_metadata_extractor: ColumnMetadataExtractor
    table_metadata_enhancer: TableMetadataEnhancer
    column_metadata_enhancer: ColumnMetadataEnhancer
    recipes_collection: RecipesCollection
