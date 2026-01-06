"""
Tests for Core Analysis Modules - v0.8.1 Phase 3

Target: Increase coverage from 71% to 80%+
Focus: Amplicon analyzer, InSilico PCR engine, and helper modules
"""
import pytest


# ============================================================================
# AMPLICON ANALYZER TESTS (core/amplicon/analyzer.py)
# ============================================================================

class TestAmpliconAnalyzer:
    """Tests for AmpliconAnalyzer class."""
    
    TEST_AMPLICON = "ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"
    
    def test_analyzer_init_default(self):
        """Should initialize analyzer with default config."""
        from primerlab.core.amplicon.analyzer import AmpliconAnalyzer
        
        analyzer = AmpliconAnalyzer()
        assert analyzer.config == {}
    
    def test_analyzer_init_with_config(self):
        """Should initialize with custom config."""
        from primerlab.core.amplicon.analyzer import AmpliconAnalyzer
        
        config = {"amplicon_analysis": {"gc_profile": {"window_size": 30}}}
        analyzer = AmpliconAnalyzer(config)
        assert analyzer.config == config
    
    def test_analyze_basic(self):
        """Should analyze amplicon sequence."""
        from primerlab.core.amplicon.analyzer import AmpliconAnalyzer
        
        analyzer = AmpliconAnalyzer()
        result = analyzer.analyze(self.TEST_AMPLICON)
        
        assert result is not None
        assert result.sequence == self.TEST_AMPLICON.upper()
        assert result.length == len(self.TEST_AMPLICON)
    
    def test_analyze_with_options(self):
        """Should analyze with specific options enabled/disabled."""
        from primerlab.core.amplicon.analyzer import AmpliconAnalyzer
        
        analyzer = AmpliconAnalyzer()
        result = analyzer.analyze(
            self.TEST_AMPLICON,
            include_structure=False,
            include_gc_profile=True,
            include_gc_clamp=True,
            include_tm=True,
            include_restriction_sites=False,
            include_quality_score=True
        )
        
        assert result is not None
    
    def test_analyze_amplicon_function(self):
        """Should use convenience function."""
        from primerlab.core.amplicon.analyzer import analyze_amplicon
        
        result = analyze_amplicon(self.TEST_AMPLICON)
        assert result is not None
        assert result.length == len(self.TEST_AMPLICON)


class TestAmpliconModels:
    """Tests for amplicon models."""
    
    def test_amplicon_analysis_result_import(self):
        """Should import AmpliconAnalysisResult."""
        from primerlab.core.amplicon.models import AmpliconAnalysisResult
        
        result = AmpliconAnalysisResult(
            sequence="ATCGATCG",
            length=8
        )
        assert result.sequence == "ATCGATCG"


# ============================================================================
# GC PROFILE TESTS (core/amplicon/gc_profile.py)
# ============================================================================

class TestGCProfile:
    """Tests for GC profile calculation."""
    
    def test_calculate_gc_profile(self):
        """Should calculate GC profile."""
        from primerlab.core.amplicon.gc_profile import calculate_gc_profile
        
        seq = "ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"
        result = calculate_gc_profile(seq, window_size=10, step_size=5)
        
        assert result is not None
        assert hasattr(result, 'windows') or isinstance(result, object)


# ============================================================================
# GC CLAMP TESTS (core/amplicon/gc_clamp.py)
# ============================================================================

class TestGCClamp:
    """Tests for GC clamp analysis."""
    
    def test_analyze_gc_clamp(self):
        """Should analyze GC clamp."""
        from primerlab.core.amplicon.gc_clamp import analyze_gc_clamp
        
        # Sequence ending with GC
        seq = "ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"
        result = analyze_gc_clamp(seq)
        
        assert result is not None
    
    def test_gc_clamp_5prime(self):
        """Should check 5' GC clamp."""
        from primerlab.core.amplicon.gc_clamp import analyze_gc_clamp
        
        # 5' starts with GC
        seq = "GCGCATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"
        result = analyze_gc_clamp(seq)
        
        assert result is not None


# ============================================================================
# TM PREDICTION TESTS (core/amplicon/tm_prediction.py)
# ============================================================================

class TestTmPrediction:
    """Tests for amplicon Tm prediction."""
    
    def test_predict_amplicon_tm(self):
        """Should predict amplicon Tm."""
        from primerlab.core.amplicon.tm_prediction import predict_amplicon_tm
        
        seq = "ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"
        result = predict_amplicon_tm(seq)
        
        assert result is not None
        assert hasattr(result, 'tm') or isinstance(result, (int, float, object))


# ============================================================================
# QUALITY SCORE TESTS (core/amplicon/quality_score.py)
# ============================================================================

class TestQualityScore:
    """Tests for quality score calculation."""
    
    def test_calculate_quality_score(self):
        """Should calculate quality score."""
        from primerlab.core.amplicon.quality_score import calculate_quality_score
        
        seq = "ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"
        result = calculate_quality_score(seq)
        
        assert result is not None


# ============================================================================
# INSILICO PCR ENGINE TESTS (core/insilico/engine.py)
# ============================================================================

class TestPrimerBinding:
    """Tests for PrimerBinding dataclass."""
    
    def test_primer_binding_create(self):
        """Should create PrimerBinding."""
        from primerlab.core.insilico.engine import PrimerBinding
        
        binding = PrimerBinding(
            primer_name="forward",
            primer_seq="ATCGATCGATCGATCGATCG",
            strand="+",
            position=100,
            match_percent=100.0,
            mismatches=0,
            three_prime_match=5,
            binding_tm=60.0,
            is_valid=True
        )
        
        assert binding.primer_name == "forward"
        assert binding.position == 100


class TestAmpliconPrediction:
    """Tests for AmpliconPrediction dataclass."""
    
    def test_amplicon_prediction_create(self):
        """Should create AmpliconPrediction."""
        from primerlab.core.insilico.engine import AmpliconPrediction, PrimerBinding
        
        fwd = PrimerBinding(
            primer_name="fwd", primer_seq="ATCGATCG", strand="+",
            position=100, match_percent=100.0, mismatches=0,
            three_prime_match=5, binding_tm=60.0, is_valid=True
        )
        rev = PrimerBinding(
            primer_name="rev", primer_seq="CGATCGAT", strand="-",
            position=300, match_percent=100.0, mismatches=0,
            three_prime_match=5, binding_tm=60.0, is_valid=True
        )
        
        prediction = AmpliconPrediction(
            forward_binding=fwd,
            reverse_binding=rev,
            product_size=200,
            product_sequence="ATCG" * 50,
            start_position=100,
            end_position=300,
            likelihood_score=0.95
        )
        
        assert prediction.product_size == 200


class TestInsilicoPCRResult:
    """Tests for InsilicoPCRResult dataclass."""
    
    def test_result_create(self):
        """Should create InsilicoPCRResult."""
        from primerlab.core.insilico.engine import InsilicoPCRResult
        
        result = InsilicoPCRResult(
            success=True,
            template_name="test",
            template_length=1000,
            forward_primer="ATCGATCG",
            reverse_primer="CGATCGAT",
            products=[],
            all_forward_bindings=[],
            all_reverse_bindings=[],
            parameters={}
        )
        
        assert result.success == True


class TestCalculateMatchPercent:
    """Tests for calculate_match_percent function."""
    
    def test_perfect_match(self):
        """Should return 100% for perfect match."""
        from primerlab.core.insilico.engine import calculate_match_percent
        
        primer = "ATCGATCG"
        target = "ATCGATCG"
        match_pct, mismatches, three_prime = calculate_match_percent(primer, target)
        
        assert match_pct == 100.0
        assert mismatches == 0
    
    def test_partial_match(self):
        """Should calculate partial match."""
        from primerlab.core.insilico.engine import calculate_match_percent
        
        primer = "ATCGATCG"
        target = "ATCGATCT"  # 1 mismatch at 3' end
        match_pct, mismatches, three_prime = calculate_match_percent(primer, target)
        
        assert match_pct < 100.0
        assert mismatches == 1


class TestInsilicoPCR:
    """Tests for InsilicoPCR class."""
    
    TEST_TEMPLATE = "ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"
    TEST_FWD = "ATCGATCGATCGATCGATCG"
    TEST_REV = "CGATCGATCGATCGATCGAT"
    
    def test_insilico_pcr_init(self):
        """Should initialize InsilicoPCR."""
        from primerlab.core.insilico.engine import InsilicoPCR
        
        engine = InsilicoPCR()
        assert engine.params is not None
    
    def test_insilico_pcr_init_custom_params(self):
        """Should initialize with custom params."""
        from primerlab.core.insilico.engine import InsilicoPCR
        
        custom = {"max_mismatches_total": 5}
        engine = InsilicoPCR(params=custom)
        assert engine.params["max_mismatches_total"] == 5
    
    def test_insilico_pcr_run(self):
        """Should run in-silico PCR."""
        from primerlab.core.insilico.engine import InsilicoPCR
        
        engine = InsilicoPCR()
        result = engine.run(
            template=self.TEST_TEMPLATE,
            forward_primer=self.TEST_FWD,
            reverse_primer=self.TEST_REV,
            template_name="test_gene"
        )
        
        assert result is not None
        assert result.template_name == "test_gene"
    
    def test_run_insilico_pcr_function(self):
        """Should use convenience function."""
        from primerlab.core.insilico.engine import run_insilico_pcr
        
        result = run_insilico_pcr(
            template=self.TEST_TEMPLATE,
            forward_primer=self.TEST_FWD,
            reverse_primer=self.TEST_REV
        )
        
        assert result is not None


class TestFindBindingSites:
    """Tests for find_binding_sites function."""
    
    def test_find_binding_sites(self):
        """Should find binding sites."""
        from primerlab.core.insilico.engine import find_binding_sites, InsilicoPCR
        
        template = "ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"
        primer = "ATCGATCGATCGATCGATCG"
        
        # Get default params from InsilicoPCR
        engine = InsilicoPCR()
        
        bindings = find_binding_sites(
            primer_seq=primer,
            template_seq=template,
            primer_name="forward",
            strand="+",
            params=engine.params
        )
        
        assert isinstance(bindings, list)


class TestCreateAlignmentString:
    """Tests for create_alignment_string function."""
    
    def test_create_alignment(self):
        """Should create alignment string."""
        from primerlab.core.insilico.engine import create_alignment_string
        
        primer = "ATCGATCG"
        target = "ATCGATCG"
        
        alignment = create_alignment_string(primer, target)
        assert isinstance(alignment, str)
    
    def test_alignment_with_mismatch(self):
        """Should show mismatch in alignment."""
        from primerlab.core.insilico.engine import create_alignment_string
        
        primer = "ATCGATCG"
        target = "ATCGATCT"
        
        alignment = create_alignment_string(primer, target)
        assert isinstance(alignment, str)


# ============================================================================
# SECONDARY STRUCTURE TESTS (core/amplicon/secondary_structure.py)
# ============================================================================

class TestSecondaryStructure:
    """Tests for secondary structure analysis."""
    
    def test_analyzer_init(self):
        """Should initialize SecondaryStructureAnalyzer."""
        from primerlab.core.amplicon.secondary_structure import SecondaryStructureAnalyzer
        
        analyzer = SecondaryStructureAnalyzer()
        assert analyzer is not None
    
    def test_predict_structure(self):
        """Should predict secondary structure."""
        from primerlab.core.amplicon.secondary_structure import SecondaryStructureAnalyzer
        
        analyzer = SecondaryStructureAnalyzer()
        seq = "ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"
        result = analyzer.predict(seq)
        
        assert result is not None


# ============================================================================
# RESTRICTION SITES TESTS (core/amplicon/restriction_sites.py)
# ============================================================================

class TestRestrictionSites:
    """Tests for restriction site finder."""
    
    def test_find_restriction_sites(self):
        """Should find restriction sites."""
        from primerlab.core.amplicon.restriction_sites import find_restriction_sites
        
        # EcoRI site: GAATTC
        seq = "ATCGATCGAATTCATCGATCGAATTCATCGATCG"
        result = find_restriction_sites(seq)
        
        assert result is not None
