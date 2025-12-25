"""
Unit tests for multiplex API.
"""
import pytest
from unittest.mock import patch, MagicMock
from primerlab.api.public import check_multiplex_compatibility

@pytest.fixture
def mock_primers():
    return [
        {"name": "P1", "fwd": "ATGCATGC", "rev": "GCTAGCTA", "tm_fwd": 60.0, "tm_rev": 60.0},
        {"name": "P2", "fwd": "TTTTAAAA", "rev": "AAAATTTT", "tm_fwd": 62.0, "tm_rev": 62.0}
    ]

def test_check_multiplex_compatibility_structure(mock_primers):
    """Test that API returns correct dictionary structure."""
    
    # Mock core components to avoid full logic execution
    with patch("primerlab.core.multiplex.dimer.DimerEngine.build_matrix") as mock_build, \
         patch("primerlab.core.multiplex.scoring.MultiplexScorer.calculate_score") as mock_score, \
         patch("primerlab.core.multiplex.validator.MultiplexValidator.get_validation_summary") as mock_validate:
        
        # Setup mocks
        mock_build.return_value = MagicMock()
        
        mock_score_res = MagicMock()
        mock_score_res.score = 90.0
        mock_score_res.grade = "A"
        mock_score_res.warnings = []
        mock_score_res.recommendations = []
        mock_score_res.component_scores = {}
        mock_score.return_value = mock_score_res
        
        mock_validate.return_value = {
            "is_valid": True,
            "warnings": [],
            "errors": []
        }
        
        result = check_multiplex_compatibility(mock_primers)
        
        assert isinstance(result, dict)
        assert result["is_valid"] is True
        assert result["score"] == 90.0
        assert result["grade"] == "A"
        assert result["pair_count"] == 2
        assert "warnings" in result
        assert "recommendations" in result

def test_check_multiplex_compatibility_real_run():
    """Test actual API run with simple inputs."""
    primers = [
        {"name": "P1", "fwd": "AGCTAGCTAGCTAGCT", "rev": "TCGATCGATCGATCGA"}, # Very simple
        {"name": "P2", "fwd": "CGATCGATCGATCGAT", "rev": "ATCGATCGATCGATCG"}
    ]
    
    # We might need to mock DimerEngine if ViennaRNA is not available, 
    # but our DimerEngine has fallback built-in.
    result = check_multiplex_compatibility(primers)
    
    assert isinstance(result["score"], float)
    assert isinstance(result["grade"], str)
