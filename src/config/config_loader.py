from typing import Dict, Any
import yaml
import os

from src.config.languages import SupportedLanguage
from src.models.app import AppConfig
from src.models.db import DatabaseConfig
from src.models.llm import LLMConfig
from src.models.prompt import PromptConfig
from src.models.vector_store import VectorStoreConfig
from src.models.embedding import EmbeddingConfig
from src.models.cache import CacheConfig
from src.models.metadata import MetadataConfig
from src.models.base import BaseConfig

from dotenv import load_dotenv

import logging

logger = logging.getLogger("hey-database")

load_dotenv()


class ConfigResolver:
    """Utility class to resolve configuration values"""

    @staticmethod
    def resolve_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively resolves environment variables in configuration.

        Environment variables should be referenced as ${VAR_NAME}

        Args:
            config: Configuration dictionary

        Returns:
            Configuration with resolved environment variables
        """
        if isinstance(config, dict):
            return {k: ConfigResolver.resolve_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [ConfigResolver.resolve_env_vars(v) for v in config]
        elif (
            isinstance(config, str) and config.startswith("${") and config.endswith("}")
        ):
            var_name = config[2:-1]
            env_value = os.getenv(var_name)
            if env_value is None:
                logger.warning(f"Environment variable {var_name} not found")
                return ""
            return env_value
        return config


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
                f"Supported Languages: {', '.join(SupportedLanguage.supported_languages())}. "
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
        config_data = ConfigResolver.resolve_env_vars(config_data)
        return DatabaseConfig(
            type=config_data["type"],
            host=config_data["host"],
            port=config_data["port"],
            database=config_data["database"],
            user=config_data["user"],
            password=config_data["password"],
            schema=config_data["schema"],
            warehouse=config_data.get("warehouse"),
            account=config_data.get("account"),
            role=config_data.get("role"),
        )

    @classmethod
    def load_cache_config(cls, config_path: str) -> CacheConfig:
        """Load the cache configuration"""
        config_data = ConfigLoader._open_config(config_path)
        return CacheConfig(
            directory=config_data["directory"],
            file_name=config_data["file_name"],
            ttl_hours=config_data.get("ttl_hours", 24),
        )

    @classmethod
    def load_sql_llm_config(cls, config_path: str) -> LLMConfig:
        """
        Load the SQL LLM configuration
        """
        config_data = ConfigLoader._open_config(config_path)
        config_data = ConfigResolver.resolve_env_vars(config_data)
        return LLMConfig(
            type=config_data["type"],
            api_key=config_data["api_key"],
            model=config_data["model"],
            base_url=config_data["base_url"] if "base_url" in config_data else None,
        )

    @classmethod
    def load_prompt_config(cls, config_path: str) -> PromptConfig:
        """Load the prompt configuration"""
        config_data = ConfigLoader._open_config(config_path)
        return PromptConfig(
            include_sample_data=config_data.get("include_sample_data", True),
            max_sample_rows=config_data.get("max_sample_rows", 3),
        )

    @classmethod
    def load_metadata_config(cls, config_path: str) -> MetadataConfig:
        """Load the metadata configuration"""
        config_data = ConfigLoader._open_config(config_path)
        return MetadataConfig(
            retrieve_distinct_values=config_data.get("retrieve_distinct_values", False),
            max_distinct_values=config_data.get("max_distinct_values", 100),
        )

    @classmethod
    def load_vector_store_config(cls, config_path) -> VectorStoreConfig:
        """Carica la configurazione del vector store se presente"""
        config_data = ConfigLoader._open_config(config_path)
        config_data = ConfigResolver.resolve_env_vars(config_data)

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
            type=config_data["type"],
            collection_name=config_data.get("collection_name"),
            path=path if config_data.get("path") else None,
            url=config_data.get("url") if config_data.get("url") else None,
            embedding=embedding_config,
            api_key=config_data.get("api_key") if config_data.get("api_key") else None,
            batch_size=config_data.get("batch_size", 100),
        )
