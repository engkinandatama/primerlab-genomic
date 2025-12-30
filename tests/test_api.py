import pytest
from primerlab.api.public import design_pcr_primers, design_qpcr_assays

def test_api_pcr(gapdh_sequence):
    """Verifies design_pcr_primers API."""
    config = {
        "parameters": {
            "product_size_range": [[100, 200]]
        }
    }
    result = design_pcr_primers(gapdh_sequence, config)
    assert result.primers is not None
    assert "forward" in result.primers

def test_api_qpcr(gapdh_sequence):
    """Verifies design_qpcr_assays API."""
    config = {
        "parameters": {
            "product_size_range": [[70, 200]],
            "probe": {"tm": {"min": 60.0, "opt": 65.0, "max": 70.0}},
            "advanced": {"timeout": 60}
        }
    }
    result = design_qpcr_assays(gapdh_sequence, config)
    assert result.primers is not None
    assert "probe" in result.primers


# ===== v0.4.3 API Tests =====

def test_api_simulate_tm_gradient():
    """Verifies simulate_tm_gradient_api function (5D)."""
    from primerlab.api import simulate_tm_gradient_api
    
    primers = [
        {"name": "Gene1", "forward": "ATGCGATCGATCGATCGATCG", "reverse": "CGATCGATCGATCGATCGCAT"}
    ]
    
    result = simulate_tm_gradient_api(
        primers=primers,
        min_temp=50.0,
        max_temp=70.0,
        step_size=1.0
    )
    
    assert "optimal" in result
    assert "range_min" in result
    assert "range_max" in result
    assert "primers" in result
    assert len(result["primers"]) >= 1
    assert result["optimal"] > 0


def test_api_simulate_tm_gradient_custom_params():
    """Tests tm_gradient API with custom salt concentration."""
    from primerlab.api import simulate_tm_gradient_api
    
    primers = [{"name": "P1", "forward": "ATGCGATCGATCGATCGATCG"}]
    
    result = simulate_tm_gradient_api(
        primers=primers,
        min_temp=55.0,
        max_temp=68.0,
        na_concentration=100.0,
        primer_concentration=0.5
    )
    
    assert result["optimal"] >= 50
    assert result["range_min"] <= result["optimal"]
    assert result["range_max"] >= result["optimal"]


# ===== v0.5.0 API Tests =====

def test_api_predict_melt_curve():
    """Tests predict_melt_curve_api function."""
    from primerlab.api import predict_melt_curve_api
    
    amplicon = "ATGC" * 25  # 100bp
    
    result = predict_melt_curve_api(amplicon)
    
    assert "predicted_tm" in result
    assert "melt_curve" in result
    assert "is_single_peak" in result
    assert "grade" in result
    assert result["predicted_tm"] > 0


def test_api_validate_qpcr_amplicon():
    """Tests validate_qpcr_amplicon_api function."""
    from primerlab.api import validate_qpcr_amplicon_api
    
    amplicon = "ATGC" * 25  # 100bp, 50% GC
    
    result = validate_qpcr_amplicon_api(amplicon)
    
    assert "amplicon_length" in result
    assert "gc_content" in result
    assert "length_ok" in result
    assert "gc_ok" in result
    assert "quality_score" in result
    assert "grade" in result
    assert result["amplicon_length"] == 100


def test_api_validate_qpcr_amplicon_short():
    """Tests validation warnings for short amplicon."""
    from primerlab.api import validate_qpcr_amplicon_api
    
    short_amplicon = "ATGC" * 10  # 40bp
    
    result = validate_qpcr_amplicon_api(short_amplicon)
    
    assert result["length_ok"] == False
    assert any("short" in w.lower() for w in result["warnings"])
