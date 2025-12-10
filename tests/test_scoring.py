"""Tests for Primer Quality Scoring (v0.1.4)."""
import pytest
from primerlab.core.scoring import (
    calculate_quality_score,
    get_category,
    PENALTY_CONFIG,
    ScoringResult
)


class TestScoringBasics:
    """Test basic scoring functionality."""
    
    def test_perfect_primer_score(self):
        """Perfect primer should score 100."""
        result = calculate_quality_score(
            primer3_penalty=0.0,
            qc_mode="standard"
        )
        assert result.score == 100
        assert result.category == "Excellent"
    
    def test_primer3_penalty_deduction(self):
        """Primer3 penalty should reduce score."""
        result = calculate_quality_score(
            primer3_penalty=2.0,  # Should deduct 20 points
            qc_mode="standard"
        )
        assert result.score == 80
        assert result.category == "Good"
    
    def test_high_penalty_low_score(self):
        """High penalty should result in low score."""
        result = calculate_quality_score(
            primer3_penalty=5.0,  # Should deduct 50 points (capped)
            qc_mode="standard"
        )
        assert result.score == 50
        assert result.category == "Fair"


class TestScoringModes:
    """Test mode-specific penalties."""
    
    def test_strict_mode_higher_penalty(self):
        """Strict mode should apply higher penalties."""
        # Same hairpin in strict vs standard
        strict = calculate_quality_score(
            primer3_penalty=0.0,
            hairpin_dg_fwd=-5.0,  # Below strict threshold (-2)
            qc_mode="strict"
        )
        standard = calculate_quality_score(
            primer3_penalty=0.0,
            hairpin_dg_fwd=-5.0,  # Below standard threshold (-3)
            qc_mode="standard"
        )
        
        # Both should penalize, but strict should penalize more
        assert strict.score < standard.score
    
    def test_relaxed_mode_lenient(self):
        """Relaxed mode should be more lenient."""
        relaxed = calculate_quality_score(
            primer3_penalty=0.0,
            hairpin_dg_fwd=-8.0,  # Below standard (-3) but above relaxed (-6 for 3end)
            qc_mode="relaxed"
        )
        standard = calculate_quality_score(
            primer3_penalty=0.0,
            hairpin_dg_fwd=-8.0,  # Below standard threshold (-3)
            qc_mode="standard"
        )
        
        # Relaxed should penalize less than standard
        assert relaxed.score >= standard.score


class TestScoringCategories:
    """Test category assignment."""
    
    def test_excellent_category(self):
        """Score 85-100 should be Excellent."""
        category, emoji = get_category(85)
        assert category == "Excellent"
        assert emoji == "✅"
        
        category, emoji = get_category(100)
        assert category == "Excellent"
    
    def test_good_category(self):
        """Score 70-84 should be Good."""
        category, emoji = get_category(70)
        assert category == "Good"
        
        category, emoji = get_category(84)
        assert category == "Good"
    
    def test_fair_category(self):
        """Score 50-69 should be Fair."""
        category, emoji = get_category(50)
        assert category == "Fair"
        assert emoji == "⚠️"
    
    def test_poor_category(self):
        """Score 0-49 should be Poor."""
        category, emoji = get_category(0)
        assert category == "Poor"
        assert emoji == "❌"
        
        category, emoji = get_category(49)
        assert category == "Poor"


class TestScoringResult:
    """Test ScoringResult dataclass."""
    
    def test_to_dict(self):
        """ScoringResult should serialize to dict."""
        result = calculate_quality_score(primer3_penalty=1.0)
        d = result.to_dict()
        
        assert "score" in d
        assert "category" in d
        assert "penalties" in d
        assert isinstance(d["penalties"], dict)


class TestPenaltyConfig:
    """Test penalty configuration."""
    
    def test_all_modes_exist(self):
        """All three modes should be configured."""
        assert "strict" in PENALTY_CONFIG
        assert "standard" in PENALTY_CONFIG
        assert "relaxed" in PENALTY_CONFIG
    
    def test_strict_thresholds_tighter(self):
        """Strict thresholds should be tighter than standard."""
        strict = PENALTY_CONFIG["strict"]
        standard = PENALTY_CONFIG["standard"]
        
        # Strict threshold is more positive (less negative)
        assert strict["hairpin_3end_threshold"] > standard["hairpin_3end_threshold"]
