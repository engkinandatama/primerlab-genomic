"""
Unit tests for qPCR Efficiency module.
"""

import pytest
import math
from primerlab.core.qpcr.efficiency import (
    EfficiencyCalculator,
    StandardCurveResult,
    EfficiencyPrediction,
    calculate_efficiency,
    predict_primer_efficiency,
)


class TestStandardCurveResult:
    """Tests for StandardCurveResult."""
    
    def test_creation(self):
        """Test StandardCurveResult creation."""
        result = StandardCurveResult(
            concentrations=[1e6, 1e5, 1e4, 1e3],
            ct_values=[15.0, 18.0, 21.0, 24.0],
            slope=-3.32,
            intercept=35.0,
            r_squared=0.99,
            efficiency=100.0,
            dynamic_range=3.0,
        )
        
        assert result.slope == -3.32
        assert result.efficiency == 100.0
    
    def test_is_acceptable(self):
        """Test acceptable efficiency range."""
        good = StandardCurveResult(
            concentrations=[], ct_values=[],
            slope=-3.32, intercept=35.0, r_squared=0.99,
            efficiency=98.0, dynamic_range=3.0,
        )
        bad = StandardCurveResult(
            concentrations=[], ct_values=[],
            slope=-3.0, intercept=35.0, r_squared=0.95,
            efficiency=80.0, dynamic_range=3.0,
        )
        
        assert good.is_acceptable is True
        assert bad.is_acceptable is False
    
    def test_grade(self):
        """Test grading system."""
        # Grade A: R² >= 0.99, E = 95-105%
        grade_a = StandardCurveResult(
            concentrations=[], ct_values=[],
            slope=-3.32, intercept=35.0, r_squared=0.995,
            efficiency=100.0, dynamic_range=3.0,
        )
        
        assert grade_a.grade == "A"


class TestEfficiencyCalculator:
    """Tests for EfficiencyCalculator."""
    
    def test_calculator_creation(self):
        """Test calculator creation."""
        calc = EfficiencyCalculator()
        assert calc.config == {}
    
    def test_calculate_from_curve_ideal(self):
        """Test calculation with ideal data (100% efficiency)."""
        # Ideal efficiency: slope = -3.322 for 100% efficiency
        # Ct = -3.322 * log10(conc) + intercept
        calc = EfficiencyCalculator()
        
        concentrations = [1e6, 1e5, 1e4, 1e3, 1e2]
        ct_values = [15.0, 18.32, 21.64, 24.97, 28.29]  # ~100% efficiency
        
        result = calc.calculate_from_curve(concentrations, ct_values)
        
        assert isinstance(result, StandardCurveResult)
        assert result.r_squared > 0.99
        assert 95 <= result.efficiency <= 105
    
    def test_calculate_from_curve_minimum_points(self):
        """Test with minimum 3 data points."""
        calc = EfficiencyCalculator()
        
        concentrations = [1e4, 1e3, 1e2]
        ct_values = [20.0, 23.32, 26.64]
        
        result = calc.calculate_from_curve(concentrations, ct_values)
        assert len(result.concentrations) == 3
    
    def test_calculate_from_curve_too_few_points(self):
        """Test with too few data points."""
        calc = EfficiencyCalculator()
        
        with pytest.raises(ValueError, match="At least 3"):
            calc.calculate_from_curve([1e4, 1e3], [20.0, 23.0])
    
    def test_predict_efficiency_good_primers(self):
        """Test efficiency prediction with good primers."""
        calc = EfficiencyCalculator()
        
        result = calc.predict_efficiency(
            forward_seq="ATGCATGCATGCATGCATGC",
            reverse_seq="GCATGCATGCATGCATGCAT",
            tm_forward=60.0,
            tm_reverse=60.5,
            gc_forward=50.0,
            gc_reverse=50.0,
            amplicon_length=120,
        )
        
        assert isinstance(result, EfficiencyPrediction)
        assert result.predicted_efficiency >= 95
        assert result.confidence > 0.7
    
    def test_predict_efficiency_tm_mismatch(self):
        """Test prediction with Tm mismatch."""
        calc = EfficiencyCalculator()
        
        result = calc.predict_efficiency(
            forward_seq="ATGC" * 5,
            reverse_seq="GCAT" * 5,
            tm_forward=60.0,
            tm_reverse=55.0,  # 5°C difference
            gc_forward=50.0,
            gc_reverse=50.0,
            amplicon_length=120,
        )
        
        # Should have recommendations for Tm difference
        assert len(result.recommendations) > 0


class TestCalculateEfficiency:
    """Tests for calculate_efficiency function."""
    
    def test_function_call(self):
        """Test function call."""
        concentrations = [1e6, 1e5, 1e4, 1e3]
        ct_values = [15.0, 18.32, 21.64, 24.97]
        
        result = calculate_efficiency(concentrations, ct_values)
        
        assert isinstance(result, StandardCurveResult)


class TestPredictPrimerEfficiency:
    """Tests for predict_primer_efficiency function."""
    
    def test_function_call(self):
        """Test function call."""
        result = predict_primer_efficiency(
            forward_seq="ATGCATGCATGCATGCATGC",
            reverse_seq="GCATGCATGCATGCATGCAT",
        )
        
        assert isinstance(result, EfficiencyPrediction)
        assert 60 <= result.predicted_efficiency <= 120
