"""
Unit tests for Advanced qPCR Features.
"""

import pytest
from primerlab.core.qpcr.advanced import (
    AdvancedQPCRTools,
    HRMOptimizationResult,
    InternalControlResult,
    QuencherRecommendation,
    DPCRCompatibilityResult,
    optimize_hrm,
    get_quencher_recommendation,
    check_dpcr,
    REPORTER_QUENCHER_MATRIX,
)


# Test amplicon (~100bp)
TEST_AMPLICON = "ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"


class TestHRMOptimizationResult:
    """Tests for HRMOptimizationResult."""
    
    def test_creation(self):
        """Test HRMOptimizationResult creation."""
        result = HRMOptimizationResult(
            amplicon_length=100,
            gc_content=50.0,
            predicted_tm=85.0,
            melt_range=(80.0, 90.0),
            resolution_score=85,
            snp_discrimination=True,
        )
        
        assert result.amplicon_length == 100
        assert result.resolution_score == 85
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        result = HRMOptimizationResult(
            amplicon_length=100,
            gc_content=50.0,
            predicted_tm=85.0,
            melt_range=(80.0, 90.0),
            resolution_score=85,
            snp_discrimination=True,
        )
        
        d = result.to_dict()
        assert d["amplicon_length"] == 100
        assert d["resolution_score"] == 85


class TestQuencherRecommendation:
    """Tests for QuencherRecommendation."""
    
    def test_creation(self):
        """Test QuencherRecommendation creation."""
        result = QuencherRecommendation(
            reporter="FAM",
            recommended_quencher="BHQ-1",
            alternative_quenchers=["TAMRA"],
            excitation=495,
            emission=520,
        )
        
        assert result.reporter == "FAM"
        assert result.recommended_quencher == "BHQ-1"


class TestDPCRCompatibilityResult:
    """Tests for DPCRCompatibilityResult."""
    
    def test_creation(self):
        """Test DPCRCompatibilityResult creation."""
        result = DPCRCompatibilityResult(
            amplicon_length=100,
            gc_content=50.0,
            is_compatible=True,
            partition_efficiency=95.0,
            concentration_range=(10, 100000),
        )
        
        assert result.is_compatible is True
        assert result.partition_efficiency == 95.0


class TestAdvancedQPCRTools:
    """Tests for AdvancedQPCRTools."""
    
    def test_tools_creation(self):
        """Test tools creation."""
        tools = AdvancedQPCRTools()
        assert tools.config == {}
    
    def test_optimize_for_hrm(self):
        """Test HRM optimization."""
        tools = AdvancedQPCRTools()
        result = tools.optimize_for_hrm(TEST_AMPLICON)
        
        assert isinstance(result, HRMOptimizationResult)
        assert result.amplicon_length == len(TEST_AMPLICON)
        assert 0 <= result.resolution_score <= 100
    
    def test_hrm_short_amplicon(self):
        """Test HRM with too short amplicon."""
        tools = AdvancedQPCRTools()
        result = tools.optimize_for_hrm("ATGC" * 5)  # 20bp
        
        assert len(result.recommendations) > 0
        assert "too short" in result.recommendations[0].lower()
    
    def test_recommend_internal_control_human(self):
        """Test internal control recommendation for human."""
        tools = AdvancedQPCRTools()
        results = tools.recommend_internal_control("human")
        
        assert len(results) >= 3
        gene_names = [r.gene_name for r in results]
        assert "GAPDH" in gene_names
    
    def test_recommend_quencher_fam(self):
        """Test quencher recommendation for FAM."""
        tools = AdvancedQPCRTools()
        result = tools.recommend_quencher("FAM")
        
        assert result.reporter == "FAM"
        assert result.recommended_quencher == "BHQ-1"
        assert len(result.alternative_quenchers) > 0
    
    def test_recommend_quencher_unknown(self):
        """Test quencher recommendation for unknown reporter."""
        tools = AdvancedQPCRTools()
        result = tools.recommend_quencher("UNKNOWN")
        
        assert result.recommended_quencher == "BHQ-1"  # Default
        assert len(result.notes) > 0
    
    def test_check_dpcr_compatibility(self):
        """Test dPCR compatibility check."""
        tools = AdvancedQPCRTools()
        result = tools.check_dpcr_compatibility(TEST_AMPLICON)
        
        assert isinstance(result, DPCRCompatibilityResult)
        assert result.is_compatible is True


class TestHelperFunctions:
    """Tests for helper functions."""
    
    def test_optimize_hrm(self):
        """Test optimize_hrm function."""
        result = optimize_hrm(TEST_AMPLICON)
        assert isinstance(result, HRMOptimizationResult)
    
    def test_get_quencher_recommendation(self):
        """Test get_quencher_recommendation function."""
        result = get_quencher_recommendation("VIC")
        assert result.reporter == "VIC"
        assert result.recommended_quencher == "MGB"
    
    def test_check_dpcr(self):
        """Test check_dpcr function."""
        result = check_dpcr(TEST_AMPLICON)
        assert isinstance(result, DPCRCompatibilityResult)


class TestReporterQuencherMatrix:
    """Tests for reporter-quencher matrix."""
    
    def test_matrix_has_common_reporters(self):
        """Test matrix contains common reporters."""
        assert "FAM" in REPORTER_QUENCHER_MATRIX
        assert "VIC" in REPORTER_QUENCHER_MATRIX
        assert "HEX" in REPORTER_QUENCHER_MATRIX
    
    def test_matrix_structure(self):
        """Test matrix entry structure."""
        fam = REPORTER_QUENCHER_MATRIX["FAM"]
        assert "compatible" in fam
        assert "optimal" in fam
        assert "wavelength" in fam
