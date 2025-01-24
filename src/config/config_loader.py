from typing import Dict, Any
import yaml
from dotenv import load_dotenv

load_dotenv()
from src.config.languages import SupportedLanguage
from src.config.models.app import AppConfig
from src.config.models.db import DatabaseConfig
from src.config.models.llm import LLMConfig
from src.config.models.prompt import PromptConfig
from src.config.models.vector_store import VectorStoreConfig
from src.config.models.embedding import EmbeddingConfig
from src.config.models.cache import CacheConfig
from src.config.models.metadata import MetadataConfig
from src.config.models.base import BaseConfig

import logging

logger = logging.getLogger("hey-database")


class ConfigLoader:
    """Load the configuration from a YAML file"""

    @classmethod
    def load_config(
        cls,
        db_config_path: str,
        cache_config_path: str,
        sql_llm_config_path: str,
        prompt_config_path: str,
        metadata_config_path: str,
        vector_store_config_path: str,
        base_config_path: str,
    ) -> AppConfig:
        """Load the configuration"""
        db_config = cls.load_db_config(db_config_path)
        cache_config = cls.load_cache_config(cache_config_path)
        sql_llm_config = cls.load_sql_llm_config(sql_llm_config_path)
        prompt_config = cls.load_prompt_config(prompt_config_path)
        metadata_config = cls.load_metadata_config(metadata_config_path)
        vector_store_config = cls.load_vector_store_config(vector_store_config_path)
        base_config = cls.load_base_config(base_config_path)

        return AppConfig(
            database=db_config,
            cache=cache_config,
            sql_llm=sql_llm_config,
            prompt=prompt_config,
            metadata=metadata_config,
            vector_store=vector_store_config,
            base_config=base_config,
        )

    @staticmethod
    def _open_config(config_path: str) -> Dict[str, Any]:
        """Load a configuration file"""
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)
        return config_data

    @classmethod
    def load_base_config(cls, config_path: str) -> BaseConfig:
        config_data = ConfigLoader._open_config(config_path)
        language_str = config_data.get(
            "language", SupportedLanguage.get_default().value
        )
        if not SupportedLanguage.is_supported(language_str):
            logger.warning(
                f"Language '{language_str}' not supported"
                f"Supported Languages: {', '.join(SupportedLanguage.get_supported_languages())}. "
                f"Default language will be used: ({SupportedLanguage.get_default().value})"
            )
        return BaseConfig(
            language=config_data.get("language", SupportedLanguage.get_default().value),
            debug=config_data.get("debug", False),
        )

    @classmethod
    def load_db_config(cls, config_path: str) -> DatabaseConfig:
        """Load the database configuration"""
        config_data = ConfigLoader._open_config(config_path)
        return DatabaseConfig(
            type=config_data["database"]["type"],
            host=config_data["database"]["host"],
            port=config_data["database"]["port"],
            database=config_data["database"]["database"],
            user=config_data["database"]["user"],
            password=config_data["database"]["password"],
            schema=config_data["database"]["schema"],
            warehouse=config_data["database"].get("warehouse"),
            account=config_data["database"].get("account"),
            role=config_data["database"].get("role"),
        )

    @classmethod
    def load_cache_config(cls, config_path: str) -> CacheConfig:
        """Load the cache configuration"""
        config_data = ConfigLoader._open_config(config_path)
        return CacheConfig(
            directory=config_data.get("cache", {}).get("directory"),
            file_name=config_data.get("cache", {}).get("file_name"),
            ttl_hours=config_data.get("cache", {}).get("ttl_hours", 24),
        )

    @classmethod
    def load_sql_llm_config(cls, config_path: str) -> LLMConfig:
        """
        Load the SQL LLM configuration
        """
        config_data = ConfigLoader._open_config(config_path)
        return LLMConfig(
            type=config_data["llm"]["type"],
            api_key=config_data["llm"].get("api_key"),
            model=config_data["llm"].get("model"),
            base_url=config_data["llm"].get("base_url"),
        )

    @classmethod
    def load_prompt_config(cls, config_path: str) -> PromptConfig:
        """Load the prompt configuration"""
        config_data = ConfigLoader._open_config(config_path)
        return PromptConfig(
            include_sample_data=config_data.get("prompt", {}).get(
                "include_sample_data", True
            ),
            max_sample_rows=config_data.get("prompt", {}).get("max_sample_rows", 3),
        )

    @classmethod
    def load_metadata_config(cls, config_path: str) -> MetadataConfig:
        """Load the metadata configuration"""
        config_data = ConfigLoader._open_config(config_path)
        return MetadataConfig(
            retrieve_distinct_values=config_data.get("metadata", {}).get(
                "retrieve_distinct_values", False
            ),
            max_distinct_values=config_data.get("metadata", {}).get(
                "max_distinct_values", 100
            ),
        )

    @classmethod
    def load_vector_store_config(cls, config_path) -> VectorStoreConfig:
        """Carica la configurazione del vector store se presente"""
        config_data = ConfigLoader._open_config(config_path)

        path = config_data.get("path")

        if "embedding" not in config_data:
            raise ValueError("Missing embedding configuration in vector_store config")

        embedding_data = config_data["embedding"]
        embedding_config = EmbeddingConfig(
            type=embedding_data["type"],
            model_name=embedding_data["model_name"],
            api_key=embedding_data.get("api_key"),
        )

        return VectorStoreConfig(
            enabled=config_data.get("enabled", False),
            type=config_data["type"],
            collection_name=config_data.get("collection_name"),
            path=path if config_data.get("path") else None,
            url=config_data.get("url") if config_data.get("url") else None,
            embedding=embedding_config,
            api_key=config_data.get("api_key") if config_data.get("api_key") else None,
            batch_size=config_data.get("batch_size", 100),
        )
