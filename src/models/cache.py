from dataclasses import dataclass
from typing import Optional


@dataclass
class CacheConfig:
    """Configurazione per il sistema di caching"""

    directory: str = "./data/cache/default"
    file_name: str = "metadata_cache_default"
    ttl_hours: int = 336
