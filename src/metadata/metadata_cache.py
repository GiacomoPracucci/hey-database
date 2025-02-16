import json
import logging
import threading

from typing import Optional
from datetime import datetime, timedelta
from pathlib import Path
from src.models.metadata import Metadata

logger = logging.getLogger("hey-database")


class MetadataCache:
    """Thread-safe cache system for database metadata"""

    def __init__(self, cache_dir: str, file_name: str, ttl_hours: int = 24):
        """Initialize the metadata cache

        Args:
            cache_dir: Directory where to store cache files
            schema_name: Database schema name (used in cache file name)
            ttl_hours: Cache validity period in hours
        """
        self.cache_dir = Path(cache_dir)
        self.ttl = timedelta(hours=ttl_hours)
        self.cache_file = self.cache_dir / f"{file_name}.json"
        self._lock = threading.Lock()
        self._ensure_cache_dir()

    def _ensure_cache_dir(self) -> None:
        """Ensure the cache directory exists"""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create cache directory {self.cache_dir}: {e}")
            raise RuntimeError(f"Failed to create cache directory: {e}")

    def set(self, metadata: Metadata) -> bool:
        """
        Save metadata to cache

        Args:
            metadata: Metadata state to cache

        Returns:
            bool: True if save successful
        """
        with self._lock:
            try:
                serializable_data = {"tables": {}, "columns": {}}

                # Serialize tables
                for table_name, table_meta in metadata.tables.items():
                    serializable_data["tables"][table_name] = {
                        "name": table_meta.base_metadata.name,
                        "description": table_meta.description,
                        "primary_keys": table_meta.base_metadata.primary_keys,
                        "foreign_keys": table_meta.base_metadata.foreign_keys,
                        "keywords": table_meta.keywords,
                        "importance_score": table_meta.importance_score,
                        "row_count": table_meta.base_metadata.row_count,
                        "columns": table_meta.base_metadata.columns,
                    }

                # Serialize columns
                for table_name, columns in metadata.columns.items():
                    serializable_data["columns"][table_name] = {}
                    for col_name, col_meta in columns.items():
                        serializable_data["columns"][table_name][col_name] = {
                            "name": col_meta.base_metadata.name,
                            "table": col_meta.base_metadata.table,
                            "data_type": col_meta.base_metadata.data_type,
                            "nullable": col_meta.base_metadata.nullable,
                            "is_primary_key": col_meta.base_metadata.is_primary_key,
                            "is_foreign_key": col_meta.base_metadata.is_foreign_key,
                            "distinct_values": col_meta.base_metadata.distinct_values,
                            "ai_name": col_meta.ai_name,
                            "description": col_meta.description,
                            "keywords": col_meta.keywords,
                        }

                # write to final file
                with open(self.cache_file, "w", encoding="utf-8") as f:
                    json.dump(serializable_data, f, indent=2, ensure_ascii=False)

                logger.debug("Successfully cached metadata")
                return True

            except Exception as e:
                logger.error(f"Error writing metadata cache: {str(e)}")
                return False

    def get(self) -> Optional[Metadata]:
        """
        Get metadata from cache if valid

        Returns:
            Optional[Dict]: Cached metadata or None if invalid/missing
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
        Check if the cache file exists and is still valid

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
        """Invalidate the cache by deleting the cache file"""
        with self._lock:
            try:
                if self.cache_file.exists():
                    self.cache_file.unlink()
                    logger.debug("Cache invalidated")
            except Exception as e:
                logger.error(f"Error invalidating cache: {e}")
