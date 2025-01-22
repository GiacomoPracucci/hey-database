from dataclasses import dataclass
from typing import Optional

@dataclass
class CacheConfig:
    """Configurazione per il sistema di caching"""
    enabled: bool = False
    directory: Optional[str] = None  # Directory dove salvare i file di cache
    ttl_hours: int = 336            # Durata della validità della cache in ore