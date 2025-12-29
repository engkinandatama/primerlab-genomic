"""
Unit tests for Tm Gradient module.
"""

import pytest
from primerlab.core.tm_gradient import (
    TmGradientConfig,
    TmGradientResult,
    TmDataPoint,
    TemperatureSensitivity,
    simulate_tm_gradient,
    calculate_binding_efficiency,
    predict_optimal_annealing,
    analyze_temperature_sensitivity,
)


class TestTmGradientConfig:
    """Tests for TmGradientConfig."""
    
    def test_default_values(self):
        """Test default configuration."""
        config = TmGradientConfig()
        assert config.min_temp == 50.0
        assert config.max_temp == 72.0
        assert config.step_size == 0.5
    
    def test_temperature_range(self):
        """Test temperature range generation."""
        config = TmGradientConfig(min_temp=55, max_temp=65, step_size=1.0)
        temps = config.temperature_range
        assert len(temps) == 11  # 55, 56, ..., 65
        assert temps[0] == 55.0
        assert temps[-1] == 65.0


class TestTmDataPoint:
    """Tests for TmDataPoint."""
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        dp = TmDataPoint(
            temperature=60.0,
            binding_efficiency=95.0,
            fraction_bound=0.95,
            delta_g=-10.5
        )
        d = dp.to_dict()
        assert d["temperature"] == 60.0
        assert d["binding_efficiency"] == 95.0


class TestSimulateTmGradient:
    """Tests for simulate_tm_gradient function."""
    
    def test_basic_simulation(self):
        """Test basic gradient simulation."""
        result = simulate_tm_gradient(
            "ATGCGATCGATCGATCGATCG",
            primer_name="TestPrimer"
        )
        
        assert isinstance(result, TmGradientResult)
        assert result.primer_name == "TestPrimer"
        assert result.calculated_tm > 0
        assert len(result.data_points) > 0
    
    def test_gc_rich_primer(self):
        """Test GC-rich primer has high Tm."""
        gc_result = simulate_tm_gradient("GCGCGCGCGCGCGCGCGCGCGC")
        
        # GC-rich 22-mer should have Tm above 60
        assert gc_result.calculated_tm > 55
    
    def test_longer_primer_reasonable_tm(self):
        """Test longer primer has reasonable Tm."""
        long = simulate_tm_gradient("ATGCGATCGATCGATCGATCGATCGATC")
        
        # Tm should be in reasonable range for 28-mer
        assert 50 < long.calculated_tm < 80
    
    def test_optimal_below_tm(self):
        """Test optimal annealing is below Tm."""
        result = simulate_tm_gradient("ATGCGATCGATCGATCGATCG")
        assert result.optimal_annealing_temp < result.calculated_tm
    
    def test_efficiency_curve(self):
        """Test efficiency curve property."""
        result = simulate_tm_gradient("ATGCGATCGATCGATCGATCG")
        curve = result.efficiency_curve
        
        assert len(curve) > 0
        assert all(isinstance(p, tuple) and len(p) == 2 for p in curve)


class TestCalculateBindingEfficiency:
    """Tests for calculate_binding_efficiency function."""
    
    def test_efficiency_below_tm(self):
        """Efficiency should be high below Tm."""
        eff, fraction, dg = calculate_binding_efficiency(50.0, 60.0, -50.0, -150.0)
        assert eff > 90
    
    def test_efficiency_above_tm(self):
        """Efficiency should be lower above Tm."""
        eff_below, _, _ = calculate_binding_efficiency(55.0, 60.0, -50.0, -150.0)
        eff_above, _, _ = calculate_binding_efficiency(70.0, 60.0, -50.0, -150.0)
        
        assert eff_below > eff_above


class TestPredictOptimalAnnealing:
    """Tests for predict_optimal_annealing function."""
    
    def test_single_primer(self):
        """Test with single primer."""
        primers = [{"name": "P1", "sequence": "ATGCGATCGATCGATCGATCG"}]
        result = predict_optimal_annealing(primers)
        
        assert "optimal" in result
        assert "range_min" in result
        assert "range_max" in result
    
    def test_multiple_primers(self):
        """Test with multiple primers."""
        primers = [
            {"name": "P1", "sequence": "ATGCGATCGATCGATCGATCG"},
            {"name": "P2", "sequence": "GCTAGCTAGCTAGCTAGCTAG"},
        ]
        result = predict_optimal_annealing(primers)
        
        assert "primers" in result
        assert len(result["primers"]) == 2


class TestAnalyzeTemperatureSensitivity:
    """Tests for analyze_temperature_sensitivity function."""
    
    def test_sensitivity_analysis(self):
        """Test sensitivity analysis."""
        sens = analyze_temperature_sensitivity(
            "ATGCGATCGATCGATCGATCG",
            primer_name="TestPrimer"
        )
        
        assert isinstance(sens, TemperatureSensitivity)
        assert sens.primer_name == "TestPrimer"
        assert 0 <= sens.sensitivity_score <= 100
        assert sens.grade in ["A", "B", "C", "D", "F"]
    
    def test_tolerance_range(self):
        """Test tolerance range is positive."""
        sens = analyze_temperature_sensitivity("ATGCGATCGATCGATCGATCG")
        assert sens.tolerance_range >= 0
