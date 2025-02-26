import json
import logging
import threading

from typing import Optional
from datetime import datetime, timedelta
from pathlib import Path
from src.models.metadata import Metadata

logger = logging.getLogger("hey-database")


class MetadataCache:
    """
    Thread-safe cache system for database metadata.

    Provides a persistent storage mechanism for metadata with automatic expiration.
    The cache is thread-safe and handles serialization/deserialization of metadata
    objects to/from JSON format.
    """

    def __init__(self, cache_dir: str, file_name: str, ttl_hours: int = 24):
        """
        Initialize the metadata cache.

        Args:
            cache_dir: Directory where to store cache files
            file_name: Base name for the cache file (without extension)
            ttl_hours: Cache validity period in hours
        """
        self.cache_dir = Path(cache_dir)
        self.ttl = timedelta(hours=ttl_hours)
        self.cache_file = self.cache_dir / f"{file_name}.json"
        self._lock = threading.Lock()
        self._ensure_cache_dir()

    def _ensure_cache_dir(self) -> None:
        """
        Ensure the cache directory exists, creating it if necessary.

        Raises:
            RuntimeError: If the directory cannot be created
        """
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create cache directory {self.cache_dir}: {e}")
            raise RuntimeError(f"Failed to create cache directory: {e}")

    def set(self, metadata: Metadata) -> bool:
        """
        Save metadata to cache.

        Serializes the metadata object to JSON and writes it to the cache file
        in a thread-safe manner.

        Args:
            metadata: Metadata state to cache

        Returns:
            bool: True if save successful, False otherwise
        """
        with self._lock:
            try:
                serializable_data = {"tables": {}, "columns": {}, "queries": {}}

                # Serialize tables
                for table_name, table_meta in metadata.tables.items():
                    serializable_data["tables"][table_name] = {
                        "name": table_meta.name,
                        "description": table_meta.description,
                        "primary_keys": table_meta.primary_keys,
                        "foreign_keys": table_meta.foreign_keys,
                        "keywords": table_meta.keywords,
                        "importance_score": table_meta.importance_score,
                        "row_count": table_meta.row_count,
                        "columns": table_meta.columns,
                        "type": table_meta.type,
                    }

                # Serialize columns
                for table_name, columns in metadata.columns.items():
                    serializable_data["columns"][table_name] = {}
                    for col_name, col_meta in columns.items():
                        serializable_data["columns"][table_name][col_name] = {
                            "name": col_meta.name,
                            "table": col_meta.table,
                            "data_type": col_meta.data_type,
                            "nullable": col_meta.nullable,
                            "is_primary_key": col_meta.is_primary_key,
                            "is_foreign_key": col_meta.is_foreign_key,
                            "distinct_values": col_meta.distinct_values,
                            "ai_name": col_meta.ai_name,
                            "description": col_meta.description,
                            "keywords": col_meta.keywords,
                            "type": col_meta.type,
                        }

                # Serialize queries
                if metadata.queries:
                    for question, query_meta in metadata.queries.items():
                        query_id = question  # Using question as key
                        serializable_data["queries"][query_id] = {
                            "question": query_meta.question,
                            "sql_query": query_meta.sql_query,
                            "explanation": query_meta.explanation,
                            "positive_votes": query_meta.positive_votes,
                            "timestamp": query_meta.timestamp.isoformat(),
                            "type": query_meta.type,
                        }

                # Write to final file
                with open(self.cache_file, "w", encoding="utf-8") as f:
                    json.dump(serializable_data, f, indent=2, ensure_ascii=False)

                logger.debug("Successfully cached metadata")
                return True

            except Exception as e:
                logger.error(f"Error writing metadata cache: {str(e)}")
                return False

    def get(self) -> Optional[Metadata]:
        """
        Get metadata from cache if valid.

        Checks if the cache is still valid based on TTL, and if so,
        deserializes the cached data into a Metadata object.

        Returns:
            Optional[Metadata]: Cached metadata or None if invalid/missing
        """
        if not self._is_cache_valid():
            return None

        with self._lock:
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)

                if not cached_data:
                    return None

                return Metadata.from_dict(cached_data)
            except Exception as e:
                logger.error(f"Error reading metadata cache: {str(e)}")
                return None

    def _is_cache_valid(self) -> bool:
        """
        Check if the cache file exists and is still valid.

        Checks both the existence of the cache file and whether
        it has expired based on the configured TTL.

        Returns:
            bool: True if cache exists and is within TTL
        """
        try:
            if not self.cache_file.exists():
                return False

            mtime = datetime.fromtimestamp(self.cache_file.stat().st_mtime)
            return datetime.now() - mtime <= self.ttl

        except Exception as e:
            logger.error(f"Error checking cache validity: {e}")
            return False

    def invalidate(self) -> None:
        """
        Invalidate the cache by deleting the cache file.

        This forces a fresh metadata extraction on the next request.
        """
        with self._lock:
            try:
                if self.cache_file.exists():
                    self.cache_file.unlink()
                    logger.debug("Cache invalidated")
            except Exception as e:
                logger.error(f"Error invalidating cache: {e}")
