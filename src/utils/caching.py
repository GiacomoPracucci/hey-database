from functools import wraps
from typing import Optional, Any, Dict
import time
from datetime import datetime, timedelta

class SchemaCache:
    """Gestore della cache per i metadati dello schema"""
    
    def __init__(self, ttl_seconds: int = 3600):
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, datetime] = {}
        self._ttl = timedelta(seconds=ttl_seconds)

    def get(self, key: str) -> Optional[Any]:
        """Recupera un valore dalla cache se non è scaduto"""
        if key not in self._cache:
            return None
            
        timestamp = self._timestamps.get(key)
        if timestamp and datetime.now() - timestamp > self._ttl:
            # Cache scaduta
            del self._cache[key]
            del self._timestamps[key]
            return None
            
        return self._cache[key]

    def set(self, key: str, value: Any):
        """Salva un valore in cache con timestamp"""
        self._cache[key] = value
        self._timestamps[key] = datetime.now()

    def clear(self):
        """Pulisce la cache"""
        self._cache.clear()
        self._timestamps.clear()


schema_cache = SchemaCache()

def cache_schema(ttl_seconds: int = 3600):
    """Decorator per cachare i risultati delle funzioni che recuperano i metadati"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # crea una chiave unica per la cache basata sulla funzione e i parametri
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # prova a recuperare dalla cache
            cached_result = schema_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # se non in cache, esegui la funzione
            result = func(*args, **kwargs)
            
            # salva in cache
            schema_cache.set(cache_key, result)
            
            return result
        return wrapper
    return decorator