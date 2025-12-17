"""
Tests for Auto Parameter Suggestion Engine (v0.1.5)
"""

import pytest
from primerlab.core.suggestion import (
    analyze_failure,
    suggest_relaxed_parameters,
    format_suggestions_for_cli,
    RELAXATION_RULES
)


class TestAnalyzeFailure:
    """Tests for failure analysis."""
    
    def test_tm_failure_detection(self):
        """Should detect Tm constraint issues."""
        error_details = {
            "left_explain": "considered 50, too few ok",
            "right_explain": "tm constraint, too many",
            "pair_explain": "no pairs"
        }
        areas = analyze_failure(error_details)
        assert "tm" in areas
    
    def test_gc_failure_detection(self):
        """Should detect GC content issues."""
        error_details = {
            "left_explain": "gc content too low",
            "right_explain": "ok",
            "pair_explain": "no pairs"
        }
        areas = analyze_failure(error_details)
        assert "gc" in areas
    
    def test_product_size_failure_detection(self):
        """Should detect product size issues."""
        error_details = {
            "left_explain": "ok",
            "right_explain": "ok",
            "pair_explain": "product size too short"
        }
        areas = analyze_failure(error_details)
        assert "product_size" in areas
    
    def test_default_areas_when_unknown(self):
        """Should return default areas when no specific issue found."""
        error_details = {
            "left_explain": "unknown issue",
            "right_explain": "unknown",
            "pair_explain": "something else"
        }
        areas = analyze_failure(error_details)
        # Should suggest common relaxations
        assert len(areas) >= 1


class TestSuggestRelaxedParameters:
    """Tests for parameter suggestion generation."""
    
    def test_tm_relaxation(self):
        """Should suggest widened Tm range."""
        config = {
            "workflow": "pcr",
            "parameters": {
                "tm": {"min": 57.0, "max": 63.0}
            }
        }
        result = suggest_relaxed_parameters(config)
        
        assert "suggestions" in result
        assert "relaxed_config" in result
        
        # Check Tm was relaxed
        relaxed_tm = result["relaxed_config"]["parameters"]["tm"]
        assert relaxed_tm["min"] < 57.0
        assert relaxed_tm["max"] > 63.0
    
    def test_gc_relaxation(self):
        """Should suggest widened GC range within limits."""
        config = {
            "workflow": "pcr",
            "parameters": {
                "gc": {"min": 40.0, "max": 60.0}
            }
        }
        result = suggest_relaxed_parameters(config)
        
        relaxed_gc = result["relaxed_config"]["parameters"]["gc"]
        # Should be relaxed but within bounds
        assert relaxed_gc["min"] >= 20.0
        assert relaxed_gc["max"] <= 80.0
    
    def test_product_size_relaxation(self):
        """Should suggest widened product size range."""
        config = {
            "workflow": "pcr",
            "parameters": {
                "product_size_range": [[100, 200]]
            }
        }
        result = suggest_relaxed_parameters(config)
        
        relaxed_range = result["relaxed_config"]["parameters"]["product_size_range"]
        assert relaxed_range[0][0] < 100  # min lowered
        assert relaxed_range[0][1] > 200  # max raised
    
    def test_probe_tm_relaxation_qpcr(self):
        """Should suggest probe Tm relaxation for qPCR."""
        config = {
            "workflow": "qpcr",
            "parameters": {
                "probe": {
                    "tm": {"min": 68.0, "max": 72.0}
                }
            }
        }
        error_details = {
            "left_explain": "ok",
            "right_explain": "ok",
            "pair_explain": "internal oligo constraint"
        }
        result = suggest_relaxed_parameters(config, error_details)
        
        # Should have probe suggestion
        probe_suggestion = next(
            (s for s in result["suggestions"] if "probe" in s["parameter"]),
            None
        )
        assert probe_suggestion is not None
    
    def test_explanation_generation(self):
        """Should generate human-readable explanation."""
        config = {
            "workflow": "pcr",
            "parameters": {}
        }
        result = suggest_relaxed_parameters(config)
        
        assert "explanation" in result
        assert len(result["explanation"]) > 0


class TestFormatForCLI:
    """Tests for CLI formatting."""
    
    def test_formats_without_error(self):
        """Should format suggestions for CLI display."""
        config = {
            "workflow": "pcr",
            "parameters": {"tm": {"min": 57.0, "max": 63.0}}
        }
        result = suggest_relaxed_parameters(config)
        cli_output = format_suggestions_for_cli(result)
        
        assert "AUTO PARAMETER SUGGESTION" in cli_output
        assert isinstance(cli_output, str)
