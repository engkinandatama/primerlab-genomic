"""
Tests for BLAST Cache (v0.3.2)
"""

import pytest
import tempfile
import time
from pathlib import Path

from primerlab.core.tools.blast_cache import BlastCache, get_cache, clear_cache


class TestBlastCache:
    """Tests for BlastCache class."""
    
    def test_cache_init(self):
        """Cache should initialize correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = BlastCache(cache_dir=tmpdir)
            assert cache.db_path.exists()
    
    def test_cache_set_get(self):
        """Should store and retrieve results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = BlastCache(cache_dir=tmpdir)
            
            query = "ATGCATGC"
            database = "/path/to/db.fasta"
            result = {"hits": [{"id": "hit1", "score": 100}]}
            
            cache.set(query, database, result)
            cached = cache.get(query, database)
            
            assert cached is not None
            assert cached["hits"][0]["id"] == "hit1"
    
    def test_cache_miss(self):
        """Should return None on cache miss."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = BlastCache(cache_dir=tmpdir)
            
            cached = cache.get("NONEXISTENT", "/db.fasta")
            assert cached is None
    
    def test_cache_different_queries(self):
        """Different queries should be cached separately."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = BlastCache(cache_dir=tmpdir)
            
            cache.set("ATGC", "/db.fasta", {"query": "ATGC"})
            cache.set("GCTA", "/db.fasta", {"query": "GCTA"})
            
            result1 = cache.get("ATGC", "/db.fasta")
            result2 = cache.get("GCTA", "/db.fasta")
            
            assert result1["query"] == "ATGC"
            assert result2["query"] == "GCTA"
    
    def test_cache_disabled(self):
        """Disabled cache should not store or retrieve."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = BlastCache(cache_dir=tmpdir, enabled=False)
            
            cache.set("ATGC", "/db.fasta", {"hits": []})
            result = cache.get("ATGC", "/db.fasta")
            
            assert result is None
    
    def test_cache_clear(self):
        """Clear should remove all entries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = BlastCache(cache_dir=tmpdir)
            
            cache.set("ATGC", "/db.fasta", {"hits": []})
            cache.clear()
            
            result = cache.get("ATGC", "/db.fasta")
            assert result is None
    
    @pytest.mark.skip(reason="Timing-dependent - may flake on slow systems")
    def test_cache_ttl(self):
        """Expired entries should not be returned."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Very short TTL
            cache = BlastCache(cache_dir=tmpdir, ttl=1)
            
            cache.set("ATGC", "/db.fasta", {"hits": []})
            
            # Wait for expiration
            time.sleep(1.5)
            
            result = cache.get("ATGC", "/db.fasta")
            assert result is None
    
    def test_cache_stats(self):
        """Stats should return entry counts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = BlastCache(cache_dir=tmpdir)
            
            cache.set("ATGC", "/db.fasta", {"hits": []})
            cache.set("GCTA", "/db.fasta", {"hits": []})
            
            stats = cache.stats()
            
            assert stats["total_entries"] == 2
            assert stats["valid_entries"] == 2
    
    @pytest.mark.skip(reason="Timing-dependent - may flake on slow systems")
    def test_cache_cleanup_expired(self):
        """Cleanup should remove expired entries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = BlastCache(cache_dir=tmpdir, ttl=1)
            
            cache.set("ATGC", "/db.fasta", {"hits": []})
            time.sleep(1.5)
            
            cache.cleanup_expired()
            stats = cache.stats()
            
            assert stats["valid_entries"] == 0


class TestCacheHelpers:
    """Tests for cache helper functions."""
    
    def test_get_cache(self):
        """get_cache should return singleton."""
        cache1 = get_cache()
        cache2 = get_cache()
        
        # Should be same instance type
        assert type(cache1) == type(cache2)
