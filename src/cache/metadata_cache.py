import json
import logging
import threading

from typing import Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path
from src.config.models.metadata import TableMetadata, EnhancedTableMetadata

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

    def _is_cache_valid(self) -> bool:
        """Check if the cache file exists and is still valid
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

    def get(self) -> Optional[Dict[str, EnhancedTableMetadata]]:
        """Get metadata from cache if valid
        Returns:
            Dict[str, TableMetadata] or None if cache invalid/missing
        """
        with self._lock:
            try:
                # check di validità by ttl
                if not self._is_cache_valid():
                    logger.debug("Cache invalid or expired")
                    return None

                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Deserialize to TableMetadata objects
                metadata = {}
                for table_name, table_data in data.items():
                    try:
                        base_metadata = TableMetadata(
                            name=table_data["name"],
                            columns=table_data["columns"],
                            primary_keys=table_data["primary_keys"],
                            foreign_keys=table_data["foreign_keys"],
                            row_count=table_data["row_count"],
                        )

                        metadata[table_name] = EnhancedTableMetadata(
                            base_metadata=base_metadata,
                            description=table_data.get("description", ""),
                            keywords=table_data.get("keywords", []),
                            importance_score=table_data.get("importance_score", 0.0),
                        )

                    except KeyError as e:
                        logger.error(
                            f"Missing required field in cached data for table {table_name}: {e}"
                        )
                        continue

                return metadata if metadata else None

            except json.JSONDecodeError as e:
                logger.error(f"Error decoding cache file: {e}")
                self.invalidate()
                return None
            except Exception as e:
                logger.error(f"Error reading metadata cache: {e}")
                return None

    def set(self, metadata: Dict[str, TableMetadata]) -> bool:
        """Save metadata to cache
        Args:
            metadata: Dictionary of table metadata to cache

        Returns:
            bool: True if save successful
        """
        with self._lock:
            try:
                # convert TableMetadata objects to serializable dictionaries
                serializable_data = {
                    table_name: {
                        "name": table_meta.base_metadata.name,
                        "description": table_meta.description,
                        "primary_keys": table_meta.base_metadata.primary_keys,
                        "foreign_keys": table_meta.base_metadata.foreign_keys,
                        "keywords": table_meta.keywords,
                        "importance_score": table_meta.importance_score,
                        "row_count": table_meta.base_metadata.row_count,
                        "columns": table_meta.base_metadata.columns,
                    }
                    for table_name, table_meta in metadata.items()
                }

                # write to final file
                with open(self.cache_file, "w", encoding="utf-8") as f:
                    json.dump(serializable_data, f, indent=2, ensure_ascii=False)

                logger.debug(
                    f"Successfully cached metadata for schema {self.schema_name}"
                )
                return True

            except Exception as e:
                logger.error(f"Error writing metadata cache: {str(e)}")
                return False

    def invalidate(self) -> None:
        """Invalidate the cache by deleting the cache file"""
        with self._lock:
            try:
                if self.cache_file.exists():
                    self.cache_file.unlink()
                    logger.debug(f"Cache invalidated for schema {self.schema_name}")
            except Exception as e:
                logger.error(f"Error invalidating cache: {e}")

    def __enter__(self):
        """Context manager support"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup on context manager exit"""
        pass  # Nothing to cleanup
