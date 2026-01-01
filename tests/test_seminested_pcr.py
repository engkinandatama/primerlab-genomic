"""
Unit tests for Semi-Nested PCR module.
"""

import pytest
from primerlab.core.variants.seminested import (
    SemiNestedPCREngine,
    design_seminested_primers,
)
from primerlab.core.variants.models import NestedPCRResult


# Test sequence (~800bp)
TEST_SEQUENCE = (
    "ATGAGTAAAGGAGAAGAACTTTTCACTGGAGTTGTCCCAATTCTTGTTGAATTAGATGGTGATGTTAATGGGCACAAATTTTCTGTC"
    "AGTGGAGAGGGTGAAGGTGATGCAACATACGGAAAACTTACCCTTAAATTTATTTGCACTACTGGAAAACTACCTGTTCCATGGCCA"
    "ACACTTGTCACTACTTTCTCTTATGGTGTTCAATGCTTTTCAAGATACCCAGATCATATGAAACGGCATGACTTTTTCAAGAGTGCC"
    "ATGCCCGAAGGTTATGTACAGGAAAGAACTATATTTTTCAAAGATGACGGGAACTACAAGACACGTGCTGAAGTCAAGTTTGAAGGT"
    "GATACCCTTGTTAATAGAATCGAGTTAAAAGGTATTGATTTTAAAGAAGATGGAAACATTCTTGGACACAAATTGGAATACAACTAT"
    "AACTCACACAATGTATACATCATGGCAGACAAACAAAAGAATGGAATCAAAGTTAACTTCAAAATTAGACACAACATTGAAGATGGA"
    "AGCGTTCAACTAGCAGACCATTATCAACAAAATACTCCAATTGGCGATGGCCCTGTCCTTTTACCAGACAACCATTACCTGTCCACA"
    "CAATCTGCCCTTTCGAAAGATCCCAACGAAAAGAGAGACCACATGGTCCTTCTTGAGTTTGTAACAGCTGCTGGGATTACACATGGC"
    "ATGGATGAACTATACAAATAA"
)


class TestSemiNestedPCREngine:
    """Tests for SemiNestedPCREngine."""
    
    def test_engine_creation(self):
        """Test engine creation with default config."""
        engine = SemiNestedPCREngine()
        assert engine.outer_size_min == 400
        assert engine.outer_size_max == 600
        assert engine.inner_size_min == 150
        assert engine.inner_size_max == 300
        assert engine.shared_position == "forward"
    
    def test_engine_custom_config(self):
        """Test engine with custom config."""
        config = {
            "outer_size_min": 300,
            "outer_size_max": 500,
            "inner_size_min": 100,
            "inner_size_max": 200,
            "shared_position": "reverse",
        }
        engine = SemiNestedPCREngine(config)
        assert engine.outer_size_min == 300
        assert engine.shared_position == "reverse"
    
    def test_design_short_sequence(self):
        """Test design with too short sequence."""
        engine = SemiNestedPCREngine()
        result = engine.design("ATGC" * 50)  # 200bp
        
        assert result.success is False
        assert len(result.warnings) > 0
        assert "too short" in result.warnings[0].lower()
    
    def test_design_valid_sequence(self):
        """Test design with valid sequence."""
        engine = SemiNestedPCREngine({
            "outer_size_min": 200,
            "outer_size_max": 400,
            "inner_size_min": 100,
            "inner_size_max": 200,
        })
        result = engine.design(TEST_SEQUENCE)
        
        assert isinstance(result, NestedPCRResult)
        assert result.sequence_length == len(TEST_SEQUENCE)


class TestDesignSeminestedPrimers:
    """Tests for design_seminested_primers function."""
    
    def test_function_call(self):
        """Test function call with defaults."""
        result = design_seminested_primers(
            sequence=TEST_SEQUENCE,
            outer_size_range=(200, 400),
            inner_size_range=(100, 200),
        )
        
        assert isinstance(result, NestedPCRResult)
        assert result.outer_size_range == (200, 400)
        assert result.inner_size_range == (100, 200)
    
    def test_shared_forward(self):
        """Test with shared forward primer."""
        result = design_seminested_primers(
            sequence=TEST_SEQUENCE,
            outer_size_range=(200, 400),
            inner_size_range=(100, 200),
            shared_position="forward",
        )
        
        assert isinstance(result, NestedPCRResult)
        # If successful, inner forward should equal outer forward
        if result.success and result.primer_set:
            assert result.primer_set.outer_forward == result.primer_set.inner_forward
    
    def test_shared_reverse(self):
        """Test with shared reverse primer."""
        result = design_seminested_primers(
            sequence=TEST_SEQUENCE,
            outer_size_range=(200, 400),
            inner_size_range=(100, 200),
            shared_position="reverse",
        )
        
        assert isinstance(result, NestedPCRResult)
        # If successful, inner reverse should equal outer reverse
        if result.success and result.primer_set:
            assert result.primer_set.outer_reverse == result.primer_set.inner_reverse
