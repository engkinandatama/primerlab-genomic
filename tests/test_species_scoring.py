"""
Unit tests for species scoring module.
"""

import pytest
from primerlab.core.species import (
    SpeciesTemplate,
    BindingSite,
    SpeciesBinding,
    SpecificityMatrix,
    SpeciesCheckResult,
)
from primerlab.core.species.scoring import (
    CrossReactivityScore,
    calculate_cross_reactivity_score,
    generate_specificity_matrix_table,
    detect_offtarget_species,
)


class TestCrossReactivityScore:
    """Tests for CrossReactivityScore dataclass."""
    
    def test_creation(self):
        """Test score creation."""
        score = CrossReactivityScore(
            primer_name="Test",
            target_binding=100.0,
            max_offtarget_binding=0.0,
            specificity_score=100.0,
            grade="A"
        )
        assert score.primer_name == "Test"
        assert score.grade == "A"
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        score = CrossReactivityScore(
            primer_name="P1",
            target_binding=95.0,
            max_offtarget_binding=50.0,
            specificity_score=85.0,
            offtarget_species=["Mouse"],
            grade="B"
        )
        d = score.to_dict()
        assert d["primer_name"] == "P1"
        assert d["specificity_score"] == 85.0
        assert "Mouse" in d["offtarget_species"]


class TestCalculateCrossReactivityScore:
    """Tests for calculate_cross_reactivity_score function."""
    
    def test_perfect_specificity(self):
        """Test perfect score with no off-target."""
        # Create matrix with only target binding
        bindings = {
            "Primer1": {
                "Target": SpeciesBinding("Target", "Primer1", "ATGC", 
                                         [BindingSite(0, "+", 100.0, 0)],
                                         best_match_percent=100.0),
            }
        }
        matrix = SpecificityMatrix(
            primer_names=["Primer1"],
            species_names=["Target"],
            target_species="Target",
            bindings=bindings
        )
        
        score = calculate_cross_reactivity_score(matrix, "Primer1")
        assert score.target_binding == 100.0
        assert score.max_offtarget_binding == 0.0
        assert score.is_specific is True
    
    def test_with_offtarget(self):
        """Test score with off-target binding."""
        bindings = {
            "Primer1": {
                "Target": SpeciesBinding("Target", "Primer1", "ATGC",
                                         [BindingSite(0, "+", 100.0, 0)],
                                         best_match_percent=100.0),
                "Mouse": SpeciesBinding("Mouse", "Primer1", "ATGC",
                                        [BindingSite(0, "+", 85.0, 2)],
                                        best_match_percent=85.0),
            }
        }
        matrix = SpecificityMatrix(
            primer_names=["Primer1"],
            species_names=["Target", "Mouse"],
            target_species="Target",
            bindings=bindings
        )
        
        score = calculate_cross_reactivity_score(matrix, "Primer1", offtarget_threshold=70.0)
        assert "Mouse" in score.offtarget_species
        assert score.is_specific is False


class TestGenerateSpecificityMatrixTable:
    """Tests for generate_specificity_matrix_table function."""
    
    def test_basic_table(self):
        """Test basic table generation."""
        matrix = SpecificityMatrix(
            primer_names=["P1", "P2"],
            species_names=["Target", "Mouse"],
            target_species="Target",
            bindings={}
        )
        
        table = generate_specificity_matrix_table(matrix)
        assert "Primer" in table
        assert "Target*" in table or "Target" in table
    
    def test_empty_matrix(self):
        """Test with empty matrix."""
        matrix = SpecificityMatrix(
            primer_names=[],
            species_names=[],
            target_species="",
            bindings={}
        )
        
        table = generate_specificity_matrix_table(matrix)
        assert "Empty matrix" in table


class TestDetectOfftargetSpecies:
    """Tests for detect_offtarget_species function."""
    
    def test_no_offtargets(self):
        """Test with no off-target binding."""
        matrix = SpecificityMatrix(
            primer_names=["P1"],
            species_names=["Target"],
            target_species="Target",
            bindings={}
        )
        result = SpeciesCheckResult(
            target_species="Target",
            primers_checked=1,
            species_checked=1,
            specificity_matrix=matrix,
            overall_score=100.0,
            grade="A",
            is_specific=True
        )
        
        detections = detect_offtarget_species(result)
        assert len(detections) == 0
