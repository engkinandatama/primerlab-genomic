"""
Unit tests for Amplicon Coverage Map visualization.
"""

import pytest
from primerlab.core.visualization.coverage_map import (
    CoverageMapGenerator,
    PrimerRegion,
    AmpliconRegion,
    CoverageMapResult,
    create_coverage_map,
)


class TestPrimerRegion:
    """Tests for PrimerRegion model."""
    
    def test_creation(self):
        """Test PrimerRegion creation."""
        region = PrimerRegion(
            name="FWD1",
            start=0,
            end=20,
            direction="forward",
        )
        
        assert region.name == "FWD1"
        assert region.length == 20
        assert region.direction == "forward"


class TestAmpliconRegion:
    """Tests for AmpliconRegion model."""
    
    def test_creation(self):
        """Test AmpliconRegion creation."""
        region = AmpliconRegion(
            name="Amplicon1",
            start=0,
            end=250,
            forward_primer="FWD1",
            reverse_primer="REV1",
        )
        
        assert region.name == "Amplicon1"
        assert region.length == 250


class TestCoverageMapResult:
    """Tests for CoverageMapResult model."""
    
    def test_creation(self):
        """Test CoverageMapResult creation."""
        result = CoverageMapResult(
            sequence_length=1000,
            total_coverage=75.5,
        )
        
        assert result.sequence_length == 1000
        assert result.total_coverage == 75.5
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        result = CoverageMapResult(
            sequence_length=1000,
            total_coverage=75.5,
        )
        
        d = result.to_dict()
        assert d["sequence_length"] == 1000
        assert d["total_coverage"] == 75.5


class TestCoverageMapGenerator:
    """Tests for CoverageMapGenerator."""
    
    def test_generator_creation(self):
        """Test generator creation."""
        generator = CoverageMapGenerator()
        assert generator.config == {}
    
    def test_create_map_single_pair(self):
        """Test map creation with single primer pair."""
        generator = CoverageMapGenerator()
        
        primer_pairs = [{
            "name": "Pair1",
            "forward": {"start": 0, "end": 20},
            "reverse": {"start": 230, "end": 250},
        }]
        
        result = generator.create_map(1000, primer_pairs)
        
        assert isinstance(result, CoverageMapResult)
        assert len(result.primers) == 2
        assert len(result.amplicons) == 1
        assert result.amplicons[0].length == 250
    
    def test_create_map_multiple_pairs(self):
        """Test map creation with multiple primer pairs."""
        generator = CoverageMapGenerator()
        
        primer_pairs = [
            {
                "name": "Pair1",
                "forward": {"start": 0, "end": 20},
                "reverse": {"start": 230, "end": 250},
            },
            {
                "name": "Pair2",
                "forward": {"start": 500, "end": 520},
                "reverse": {"start": 730, "end": 750},
            },
        ]
        
        result = generator.create_map(1000, primer_pairs)
        
        assert len(result.primers) == 4
        assert len(result.amplicons) == 2
    
    def test_coverage_calculation(self):
        """Test coverage percentage calculation."""
        generator = CoverageMapGenerator()
        
        # One amplicon covering 250bp of 1000bp = 25%
        primer_pairs = [{
            "name": "Pair1",
            "forward": {"start": 0, "end": 20},
            "reverse": {"start": 230, "end": 250},
        }]
        
        result = generator.create_map(1000, primer_pairs)
        assert result.total_coverage == 25.0
    
    def test_generate_svg(self):
        """Test SVG generation."""
        generator = CoverageMapGenerator()
        
        primer_pairs = [{
            "name": "Test",
            "forward": {"start": 0, "end": 20},
            "reverse": {"start": 80, "end": 100},
        }]
        
        result = generator.create_map(200, primer_pairs)
        svg = generator.generate_svg(result)
        
        assert "<svg" in svg
        assert "</svg>" in svg
        assert "Coverage Map" in svg


class TestCreateCoverageMap:
    """Tests for create_coverage_map function."""
    
    def test_function_call(self):
        """Test function call."""
        primer_pairs = [{
            "name": "P1",
            "forward": {"start": 0, "end": 20},
            "reverse": {"start": 80, "end": 100},
        }]
        
        result = create_coverage_map(500, primer_pairs)
        
        assert isinstance(result, CoverageMapResult)
        assert result.sequence_length == 500
