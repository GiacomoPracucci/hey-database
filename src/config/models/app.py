from dataclasses import dataclass
from typing import Optional
from src.config.models.db import DatabaseConfig
from src.config.models.llm import LLMConfig
from src.config.models.prompt import PromptConfig
from src.config.models.vector_store import VectorStoreConfig
from src.config.models.cache import CacheConfig

@dataclass
class AppConfig:
    database: DatabaseConfig
    llm: LLMConfig
    prompt: PromptConfig
    cache: CacheConfig
    vector_store: Optional[VectorStoreConfig] = None
    debug: bool = False