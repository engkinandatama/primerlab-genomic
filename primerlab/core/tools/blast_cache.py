"""
BLAST Cache (v0.3.2)

Cache BLAST results to avoid redundant queries.
"""

import hashlib
import json
import time
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """A single cache entry."""
    query_hash: str
    database_hash: str
    result_json: str
    created_at: float
    expires_at: float


class BlastCache:
    """
    SQLite-based BLAST result cache.
    
    Caches results based on:
    - Query sequence hash
    - Database path/hash
    - BLAST parameters
    """

    DEFAULT_TTL = 86400 * 7  # 7 days

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        ttl: int = DEFAULT_TTL,
        enabled: bool = True
    ):
        """
        Initialize cache.
        
        Args:
            cache_dir: Directory for cache DB (default: ~/.primerlab/cache)
            ttl: Time-to-live in seconds
            enabled: Whether caching is enabled
        """
        self.enabled = enabled
        self.ttl = ttl

        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / ".primerlab" / "cache"

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.cache_dir / "blast_cache.db"

        self._init_db()

    def _init_db(self):
        """Initialize SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS blast_cache (
                    cache_key TEXT PRIMARY KEY,
                    query_hash TEXT,
                    database_hash TEXT,
                    result_json TEXT,
                    created_at REAL,
                    expires_at REAL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires 
                ON blast_cache(expires_at)
            """)
            conn.commit()

    def _make_key(
        self,
        query_seq: str,
        database: str,
        params: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate cache key from query and database."""
        key_parts = [
            query_seq.upper(),
            database,
            json.dumps(params or {}, sort_keys=True)
        ]
        key_str = "|".join(key_parts)
        return hashlib.sha256(key_str.encode()).hexdigest()[:32]

    def get(
        self,
        query_seq: str,
        database: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached result if available.
        
        Args:
            query_seq: Query sequence
            database: Database path
            params: BLAST parameters
            
        Returns:
            Cached result dict or None
        """
        if not self.enabled:
            return None

        cache_key = self._make_key(query_seq, database, params)
        now = time.time()

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """SELECT result_json FROM blast_cache 
                       WHERE cache_key = ? AND expires_at > ?""",
                    (cache_key, now)
                )
                row = cursor.fetchone()

                if row:
                    logger.debug(f"Cache hit for {cache_key[:8]}...")
                    return json.loads(row[0])

                logger.debug(f"Cache miss for {cache_key[:8]}...")
                return None

        except Exception as e:
            logger.warning(f"Cache read error: {e}")
            return None

    def set(
        self,
        query_seq: str,
        database: str,
        result: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None
    ):
        """
        Store result in cache.
        
        Args:
            query_seq: Query sequence
            database: Database path
            result: Result to cache
            params: BLAST parameters
        """
        if not self.enabled:
            return

        cache_key = self._make_key(query_seq, database, params)
        now = time.time()
        expires_at = now + self.ttl

        try:
            result_json = json.dumps(result)

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT OR REPLACE INTO blast_cache 
                       (cache_key, query_hash, database_hash, result_json, created_at, expires_at)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (cache_key, cache_key[:16], database, result_json, now, expires_at)
                )
                conn.commit()

            logger.debug(f"Cached result for {cache_key[:8]}...")

        except Exception as e:
            logger.warning(f"Cache write error: {e}")

    def clear(self):
        """Clear all cache entries."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM blast_cache")
                conn.commit()
            logger.info("Cache cleared")
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")

    def cleanup_expired(self):
        """Remove expired entries."""
        now = time.time()
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "DELETE FROM blast_cache WHERE expires_at < ?",
                    (now,)
                )
                count = cursor.rowcount
                conn.commit()

            if count > 0:
                logger.debug(f"Cleaned up {count} expired cache entries")

        except Exception as e:
            logger.warning(f"Cache cleanup error: {e}")

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM blast_cache")
                total = cursor.fetchone()[0]

                now = time.time()
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM blast_cache WHERE expires_at > ?",
                    (now,)
                )
                valid = cursor.fetchone()[0]

                return {
                    "total_entries": total,
                    "valid_entries": valid,
                    "expired_entries": total - valid,
                    "cache_path": str(self.db_path)
                }
        except Exception as e:
            return {"error": str(e)}


# Global cache instance
_cache: Optional[BlastCache] = None


def get_cache(enabled: bool = True) -> BlastCache:
    """Get or create global cache instance."""
    global _cache
    if _cache is None:
        _cache = BlastCache(enabled=enabled)
    return _cache


def clear_cache():
    """Clear the global cache."""
    cache = get_cache()
    cache.clear()
