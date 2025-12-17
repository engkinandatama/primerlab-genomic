"""
Tests for Primer Comparison Tool (v0.1.5)
"""

import pytest
from primerlab.core.comparison import (
    compare_primers,
    format_comparison_for_cli,
    _extract_metrics,
    _analyze_pros_cons,
    _calculate_comparison_score
)


# Sample result data for testing
SAMPLE_RESULT_A = {
    "workflow": "pcr",
    "primers": {
        "forward": {
            "id": "gene_F1",
            "sequence": "ATGCGTACGATCGATCG",
            "tm": 60.5,
            "gc": 52.0,
            "hairpin_dg": -2.5,
            "homodimer_dg": -5.0
        },
        "reverse": {
            "id": "gene_R1",
            "sequence": "TCGATCGATCGTAGCAT",
            "tm": 59.8,
            "gc": 48.0,
            "hairpin_dg": -1.8,
            "homodimer_dg": -4.5
        }
    },
    "amplicons": [{"length": 200}],
    "qc": {"quality_score": 85}
}

SAMPLE_RESULT_B = {
    "workflow": "pcr",
    "primers": {
        "forward": {
            "id": "gene_F2",
            "sequence": "GCTAGCTAGCTAGCTA",
            "tm": 58.0,
            "gc": 55.0,
            "hairpin_dg": -4.0,
            "homodimer_dg": -7.0
        },
        "reverse": {
            "id": "gene_R2",
            "sequence": "TAGCTAGCTAGCTAGC",
            "tm": 62.5,
            "gc": 50.0,
            "hairpin_dg": -3.5,
            "homodimer_dg": -6.0
        }
    },
    "amplicons": [{"length": 180}],
    "qc": {"quality_score": 72}
}


class TestExtractMetrics:
    """Tests for metric extraction."""
    
    def test_extracts_quality_score(self):
        """Should extract quality score from QC."""
        metrics = _extract_metrics(SAMPLE_RESULT_A)
        assert metrics["quality_score"] == 85
    
    def test_extracts_primer_metrics(self):
        """Should extract primer Tm and GC."""
        metrics = _extract_metrics(SAMPLE_RESULT_A)
        assert metrics["fwd_tm"] == 60.5
        assert metrics["rev_tm"] == 59.8
        assert metrics["fwd_gc"] == 52.0
        assert metrics["rev_gc"] == 48.0
    
    def test_calculates_tm_balance(self):
        """Should calculate Tm balance."""
        metrics = _extract_metrics(SAMPLE_RESULT_A)
        assert metrics["tm_balance"] == pytest.approx(0.7, abs=0.1)
    
    def test_extracts_product_size(self):
        """Should extract product size from amplicons."""
        metrics = _extract_metrics(SAMPLE_RESULT_A)
        assert metrics["product_size"] == 200
    
    def test_handles_missing_data(self):
        """Should handle missing data gracefully."""
        empty_result = {"primers": {}, "amplicons": [], "qc": {}}
        metrics = _extract_metrics(empty_result)
        assert metrics["quality_score"] is None
        assert metrics["fwd_tm"] is None


class TestAnalyzeProsAndCons:
    """Tests for pros/cons analysis."""
    
    def test_identifies_excellent_quality(self):
        """Should identify excellent quality score as pro."""
        metrics = {"quality_score": 90, "tm_balance": 0.5}
        result = _analyze_pros_cons(metrics)
        assert any("Excellent" in p for p in result["pros"])
    
    def test_identifies_poor_quality(self):
        """Should identify poor quality score as con."""
        metrics = {"quality_score": 40}
        result = _analyze_pros_cons(metrics)
        assert any("Poor" in c for c in result["cons"])
    
    def test_identifies_good_tm_balance(self):
        """Should identify good Tm balance as pro."""
        metrics = {"tm_balance": 0.5}
        result = _analyze_pros_cons(metrics)
        assert any("Tm balance" in p for p in result["pros"])
    
    def test_identifies_strong_hairpin(self):
        """Should identify strong hairpin as con."""
        metrics = {"fwd_hairpin_dg": -8.0}
        result = _analyze_pros_cons(metrics)
        assert any("hairpin" in c for c in result["cons"])


class TestCompareComparison:
    """Tests for the main comparison function."""
    
    def test_returns_winner(self):
        """Should determine winner based on scores."""
        result = compare_primers(SAMPLE_RESULT_A, SAMPLE_RESULT_B)
        assert result["winner"] in ["A", "B", "tie"]
    
    def test_returns_scores(self):
        """Should return scores for both primers."""
        result = compare_primers(SAMPLE_RESULT_A, SAMPLE_RESULT_B)
        assert "A" in result["scores"]
        assert "B" in result["scores"]
    
    def test_returns_comparison_table(self):
        """Should return comparison table."""
        result = compare_primers(SAMPLE_RESULT_A, SAMPLE_RESULT_B)
        assert len(result["comparison_table"]) > 0
    
    def test_returns_pros_cons(self):
        """Should return pros/cons for both."""
        result = compare_primers(SAMPLE_RESULT_A, SAMPLE_RESULT_B)
        assert "A" in result["pros_cons"]
        assert "B" in result["pros_cons"]
    
    def test_custom_labels(self):
        """Should support custom labels."""
        result = compare_primers(
            SAMPLE_RESULT_A, 
            SAMPLE_RESULT_B,
            labels=("Design1", "Design2")
        )
        assert "Design1" in result["scores"]
        assert "Design2" in result["scores"]
    
    def test_a_wins_with_higher_quality(self):
        """Result A should win with higher quality score."""
        result = compare_primers(SAMPLE_RESULT_A, SAMPLE_RESULT_B)
        # A has quality_score=85, B has quality_score=72
        # A should likely win
        assert result["winner"] == "A" or result["winner"] == "tie"


class TestCalculateComparisonScore:
    """Tests for scoring calculation."""
    
    def test_quality_score_affects_result(self):
        """Higher quality score should lead to higher comparison score."""
        high_qs = {"quality_score": 90, "tm_balance": 1.0}
        low_qs = {"quality_score": 50, "tm_balance": 1.0}
        
        high_score = _calculate_comparison_score(high_qs)
        low_score = _calculate_comparison_score(low_qs)
        
        assert high_score > low_score
    
    def test_tm_balance_affects_result(self):
        """Better Tm balance should lead to higher score."""
        good_balance = {"tm_balance": 0.5}
        bad_balance = {"tm_balance": 5.0}
        
        good_score = _calculate_comparison_score(good_balance)
        bad_score = _calculate_comparison_score(bad_balance)
        
        assert good_score > bad_score


class TestFormatForCLI:
    """Tests for CLI formatting."""
    
    def test_formats_without_error(self):
        """Should format comparison for CLI display."""
        result = compare_primers(SAMPLE_RESULT_A, SAMPLE_RESULT_B)
        cli_output = format_comparison_for_cli(result)
        
        assert "PRIMER COMPARISON" in cli_output
        assert isinstance(cli_output, str)
    
    def test_includes_winner(self):
        """Should include winner in output."""
        result = compare_primers(SAMPLE_RESULT_A, SAMPLE_RESULT_B)
        cli_output = format_comparison_for_cli(result)
        
        assert "Winner" in cli_output or "TIE" in cli_output
