from src.models.cache import CacheConfig
from src.cache.metadata_cache import MetadataCache

import logging

logger = logging.getLogger("hey-database")


class CacheFactory:
    """Factory per la creazione del componente MetadataCache"""

    @staticmethod
    def create_cache(config: CacheConfig) -> MetadataCache:
        return MetadataCache(
            cache_dir=config.cache_dir,
            file_name=config.file_name,
            ttl_hours=config.ttl_hours,
        )
