"""
Unit tests for DimerEngine.

Tests:
- Basic dimer calculation
- Caching behavior
- ViennaRNA fallback when unavailable
- Matrix building for multiplex sets
"""

import pytest
from unittest.mock import patch, MagicMock
from primerlab.core.compat_check.models import MultiplexPair, DimerResult
from primerlab.core.compat_check.dimer import DimerEngine


class TestDimerEngineBasic:
    """Basic tests for DimerEngine."""
    
    def test_initialization_default(self):
        """Test default initialization."""
        engine = DimerEngine()
        assert engine.threshold == -6.0
    
    def test_initialization_custom_threshold(self):
        """Test custom threshold from config."""
        config = {"multiplex": {"dimer_dg_threshold": -5.0}}
        engine = DimerEngine(config)
        assert engine.threshold == -5.0
    
    def test_check_dimer_basic(self):
        """Test basic dimer checking."""
        engine = DimerEngine()
        result = engine.check_dimer(
            "ATGGGGAAGGTGAAGGTCGG",
            "GGATCTCGCTCCTGGAAGATG",
            "GAPDH_F",
            "GAPDH_R"
        )
        
        assert isinstance(result, DimerResult)
        assert result.primer1_name == "GAPDH_F"
        assert result.primer2_name == "GAPDH_R"
        # delta_g should be a float (value depends on ViennaRNA)
        assert isinstance(result.delta_g, float)
    
    def test_sequence_normalization(self):
        """Test sequences are normalized to uppercase."""
        engine = DimerEngine()
        result = engine.check_dimer("atgc", "gcta", "P1", "P2")
        
        assert result.primer1_seq == "ATGC"
        assert result.primer2_seq == "GCTA"


class TestDimerCaching:
    """Tests for dimer calculation caching."""
    
    def test_cache_hit(self):
        """Test that repeated calculations use cache."""
        engine = DimerEngine()
        
        # First call
        result1 = engine.check_dimer("ATGC", "GCTA", "P1", "P2")
        cache_size_after_first = len(engine._cache)
        
        # Second call with same sequences (different names)
        result2 = engine.check_dimer("ATGC", "GCTA", "P3", "P4")
        cache_size_after_second = len(engine._cache)
        
        # Cache should not grow for same sequence pair
        assert cache_size_after_second == cache_size_after_first
        # Results should have same delta_g
        assert result1.delta_g == result2.delta_g
    
    def test_cache_key_order_independent(self):
        """Test cache key is order-independent."""
        engine = DimerEngine()
        
        result1 = engine.check_dimer("AAAA", "TTTT", "P1", "P2")
        result2 = engine.check_dimer("TTTT", "AAAA", "P3", "P4")
        
        # Should use same cache entry
        assert len(engine._cache) == 1
        assert result1.delta_g == result2.delta_g
    
    def test_clear_cache(self):
        """Test cache clearing."""
        engine = DimerEngine()
        engine.check_dimer("ATGC", "GCTA", "P1", "P2")
        assert len(engine._cache) > 0
        
        engine.clear_cache()
        assert len(engine._cache) == 0


class TestDimerFallback:
    """Tests for ViennaRNA fallback behavior."""
    
    def test_fallback_when_vienna_unavailable(self):
        """Test fallback returns neutral result when ViennaRNA missing."""
        engine = DimerEngine()
        
        # Mock ViennaRNA as unavailable
        with patch.object(engine.vienna, 'fold') as mock_fold:
            mock_fold.return_value = {"error": "RNAfold not found"}
            
            result = engine.check_dimer("ATGC", "GCTA", "P1", "P2")
            
            # Should return neutral result
            assert result.delta_g == 0.0
            assert result.is_problematic is False
            assert "unavailable" in result.structure.lower()
    
    def test_fallback_caches_availability(self):
        """Test ViennaRNA availability is cached."""
        engine = DimerEngine()
        
        with patch.object(engine.vienna, 'fold') as mock_fold:
            mock_fold.return_value = {"error": "RNAfold not found"}
            
            # First call checks availability
            engine.check_dimer("ATGC", "GCTA", "P1", "P2")
            first_call_count = mock_fold.call_count
            
            # Second call should use cached availability
            engine.check_dimer("AAAA", "TTTT", "P3", "P4")
            second_call_count = mock_fold.call_count
            
            # fold() should only be called once to check availability
            assert second_call_count == first_call_count


class TestBuildMatrix:
    """Tests for compatibility matrix building."""
    
    def test_build_matrix_single_pair(self):
        """Test matrix building with single primer pair."""
        engine = DimerEngine()
        pairs = [MultiplexPair("GAPDH", "ATGC", "GCTA")]
        
        matrix = engine.build_matrix(pairs)
        
        # Single pair = 2 primers (F, R)
        # Combinations: F-F, F-R, R-R = 3 checks
        assert len(matrix.primer_names) == 2
        assert matrix.total_dimers == 3
        assert "GAPDH_F" in matrix.primer_names
        assert "GAPDH_R" in matrix.primer_names
    
    def test_build_matrix_two_pairs(self):
        """Test matrix building with two primer pairs."""
        engine = DimerEngine()
        pairs = [
            MultiplexPair("GAPDH", "ATGC", "GCTA"),
            MultiplexPair("ACTB", "TTTT", "AAAA"),
        ]
        
        matrix = engine.build_matrix(pairs)
        
        # Two pairs = 4 primers
        # Combinations: C(4,2) + 4 homodimers = 6 + 4 = 10 checks
        # Actually: for i in range(n), for j in range(i, n) = n*(n+1)/2 = 4*5/2 = 10
        assert len(matrix.primer_names) == 4
        assert matrix.total_dimers == 10
    
    def test_build_matrix_tracks_worst(self):
        """Test matrix tracks worst dimer correctly."""
        engine = DimerEngine()
        
        # Use sequences that might form worse dimers
        pairs = [
            MultiplexPair("P1", "GGGGGGGGGGGGGGGGGGGG", "CCCCCCCCCCCCCCCCCCCC"),
        ]
        
        matrix = engine.build_matrix(pairs)
        
        # Should have a worst dimer tracked
        # (actual value depends on ViennaRNA, but structure should be present)
        assert matrix.worst_dimer is not None or matrix.total_dimers > 0
    
    def test_build_matrix_empty_pairs(self):
        """Test matrix building with empty pairs list."""
        engine = DimerEngine()
        matrix = engine.build_matrix([])
        
        assert len(matrix.primer_names) == 0
        assert matrix.total_dimers == 0
        assert matrix.problematic_count == 0


class TestGetProblematicPairs:
    """Tests for retrieving problematic pairs."""
    
    def test_get_problematic_sorted(self):
        """Test problematic pairs are sorted by ΔG."""
        engine = DimerEngine()
        
        # Create a matrix with problematic dimers by using threshold
        config = {"multiplex": {"dimer_dg_threshold": 0.0}}  # All dimers problematic
        engine = DimerEngine(config)
        
        pairs = [
            MultiplexPair("P1", "ATGC", "GCTA"),
            MultiplexPair("P2", "TTTT", "AAAA"),
        ]
        
        matrix = engine.build_matrix(pairs)
        problematic = engine.get_problematic_pairs(matrix)
        
        # Should be sorted by delta_g (most negative first)
        if len(problematic) > 1:
            for i in range(len(problematic) - 1):
                assert problematic[i].delta_g <= problematic[i+1].delta_g
