"""
Unit tests for Multiplex Data Models.

Tests:
- MultiplexPair creation and properties
- DimerResult creation and to_dict()
- CompatibilityMatrix operations
- MultiplexResult grading and export
"""

import pytest
from primerlab.core.multiplex.models import (
    MultiplexPair,
    DimerResult,
    CompatibilityMatrix,
    MultiplexResult,
    score_to_grade,
    grade_to_emoji,
)


class TestMultiplexPair:
    """Tests for MultiplexPair dataclass."""
    
    def test_basic_creation(self):
        """Test basic MultiplexPair creation."""
        pair = MultiplexPair(
            name="GAPDH",
            forward="ATGGGGAAGGTGAAGGTCGG",
            reverse="GGATCTCGCTCCTGGAAGATG",
        )
        assert pair.name == "GAPDH"
        assert pair.forward == "ATGGGGAAGGTGAAGGTCGG"
        assert pair.reverse == "GGATCTCGCTCCTGGAAGATG"
    
    def test_sequence_normalization(self):
        """Test sequences are normalized to uppercase."""
        pair = MultiplexPair(
            name="Test",
            forward="atgc",
            reverse="gcta",
        )
        assert pair.forward == "ATGC"
        assert pair.reverse == "GCTA"
    
    def test_avg_tm(self):
        """Test average Tm calculation."""
        pair = MultiplexPair(
            name="Test",
            forward="ATGC",
            reverse="GCTA",
            tm_forward=60.0,
            tm_reverse=62.0,
        )
        assert pair.avg_tm == 61.0
    
    def test_avg_gc(self):
        """Test average GC calculation."""
        pair = MultiplexPair(
            name="Test",
            forward="ATGC",
            reverse="GCTA",
            gc_forward=50.0,
            gc_reverse=60.0,
        )
        assert pair.avg_gc == 55.0
    
    def test_to_dict(self):
        """Test to_dict() export."""
        pair = MultiplexPair(
            name="GAPDH",
            forward="ATGC",
            reverse="GCTA",
            tm_forward=60.0,
            tm_reverse=62.0,
            target_region="exon1",
        )
        d = pair.to_dict()
        assert d["name"] == "GAPDH"
        assert d["forward"] == "ATGC"
        assert d["target_region"] == "exon1"
        assert "avg_tm" in d


class TestDimerResult:
    """Tests for DimerResult dataclass."""
    
    def test_basic_creation(self):
        """Test basic DimerResult creation."""
        result = DimerResult(
            primer1_name="GAPDH_F",
            primer2_name="ACTB_F",
            primer1_seq="ATGC",
            primer2_seq="GCTA",
            delta_g=-5.5,
        )
        assert result.delta_g == -5.5
        assert result.is_problematic is False
    
    def test_homodimer_detection(self):
        """Test homodimer detection."""
        homo = DimerResult(
            primer1_name="GAPDH_F",
            primer2_name="GAPDH_F",
            primer1_seq="ATGC",
            primer2_seq="ATGC",
            delta_g=-3.0,
        )
        assert homo.is_homodimer is True
        
        hetero = DimerResult(
            primer1_name="GAPDH_F",
            primer2_name="ACTB_F",
            primer1_seq="ATGC",
            primer2_seq="GCTA",
            delta_g=-3.0,
        )
        assert hetero.is_homodimer is False
    
    def test_to_dict(self):
        """Test to_dict() export."""
        result = DimerResult(
            primer1_name="P1",
            primer2_name="P2",
            primer1_seq="ATGC",
            primer2_seq="GCTA",
            delta_g=-7.5,
            structure="...(())",
            is_problematic=True,
        )
        d = result.to_dict()
        assert d["delta_g"] == -7.5
        assert d["is_problematic"] is True
        assert "is_homodimer" in d


class TestCompatibilityMatrix:
    """Tests for CompatibilityMatrix dataclass."""
    
    def test_empty_matrix(self):
        """Test empty matrix creation."""
        matrix = CompatibilityMatrix()
        assert len(matrix.primer_names) == 0
        assert len(matrix.matrix) == 0
        assert matrix.worst_dimer is None
    
    def test_get_dimer(self):
        """Test dimer retrieval by name."""
        dimer = DimerResult(
            primer1_name="P1",
            primer2_name="P2",
            primer1_seq="ATGC",
            primer2_seq="GCTA",
            delta_g=-5.0,
        )
        matrix = CompatibilityMatrix(
            primer_names=["P1", "P2"],
            matrix={("P1", "P2"): dimer},
        )
        
        # Forward lookup
        assert matrix.get_dimer("P1", "P2") is not None
        # Reverse lookup
        assert matrix.get_dimer("P2", "P1") is not None
        # Non-existent
        assert matrix.get_dimer("P1", "P3") is None
    
    def test_get_problematic_dimers(self):
        """Test retrieving problematic dimers."""
        good = DimerResult("P1", "P2", "ATGC", "GCTA", -2.0, is_problematic=False)
        bad = DimerResult("P1", "P3", "ATGC", "TTTT", -8.0, is_problematic=True)
        
        matrix = CompatibilityMatrix(
            primer_names=["P1", "P2", "P3"],
            matrix={("P1", "P2"): good, ("P1", "P3"): bad},
            problematic_count=1,
        )
        
        problematic = matrix.get_problematic_dimers()
        assert len(problematic) == 1
        assert problematic[0].delta_g == -8.0
    
    def test_to_dict(self):
        """Test to_dict() export."""
        matrix = CompatibilityMatrix(
            primer_names=["P1", "P2"],
            total_dimers=1,
            problematic_count=0,
        )
        d = matrix.to_dict()
        assert d["primer_names"] == ["P1", "P2"]
        assert d["total_dimers"] == 1


class TestMultiplexResult:
    """Tests for MultiplexResult dataclass."""
    
    def test_empty_result(self):
        """Test empty result creation."""
        result = MultiplexResult()
        assert result.score == 0.0
        assert result.grade == "F"
        assert result.is_compatible is False
    
    def test_is_compatible(self):
        """Test compatibility check by grade."""
        for grade, expected in [("A", True), ("B", True), ("C", True), ("D", False), ("F", False)]:
            result = MultiplexResult(grade=grade)
            assert result.is_compatible is expected
    
    def test_pair_count(self):
        """Test pair count property."""
        pairs = [
            MultiplexPair("P1", "ATGC", "GCTA"),
            MultiplexPair("P2", "TTTT", "AAAA"),
        ]
        result = MultiplexResult(pairs=pairs)
        assert result.pair_count == 2
    
    def test_to_dict(self):
        """Test to_dict() export."""
        result = MultiplexResult(
            score=85.0,
            grade="A",
            warnings=["Warning 1"],
            recommendations=["Rec 1"],
        )
        d = result.to_dict()
        assert d["score"] == 85.0
        assert d["grade"] == "A"
        assert d["is_compatible"] is True
    
    def test_phase3_fields(self):
        """Test Phase 3 additional fields."""
        result = MultiplexResult(
            score=80.0,
            grade="B",
            is_valid=False,
            errors=["Error 1"],
            component_scores={"dimer": 90.0, "tm": 80.0}
        )
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.component_scores["dimer"] == 90.0


class TestScoreGrading:
    """Tests for score grading functions."""
    
    def test_score_to_grade(self):
        """Test score to grade conversion."""
        assert score_to_grade(100) == "A"
        assert score_to_grade(85) == "A"
        assert score_to_grade(84) == "B"
        assert score_to_grade(70) == "B"
        assert score_to_grade(69) == "C"
        assert score_to_grade(55) == "C"
        assert score_to_grade(54) == "D"
        assert score_to_grade(40) == "D"
        assert score_to_grade(39) == "F"
        assert score_to_grade(0) == "F"
    
    def test_grade_to_emoji(self):
        """Test grade to emoji conversion."""
        assert grade_to_emoji("A") == "✅"
        assert grade_to_emoji("B") == "✅"
        assert grade_to_emoji("C") == "⚠️"
        assert grade_to_emoji("D") == "⚠️"
        assert grade_to_emoji("F") == "❌"
        assert grade_to_emoji("X") == "❓"  # Unknown grade
