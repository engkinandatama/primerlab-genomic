"""
Test Model Serialization (v0.8.2).

Tests that all dataclass models can be serialized to dict for JSON export.
"""

import pytest
from typing import Dict, Any


class TestOfftargetModelSerialization:
    """Test offtarget/finder.py dataclass serialization."""

    def test_offtarget_hit_to_dict(self):
        """Test OfftargetHit.to_dict() method."""
        from primerlab.core.offtarget.finder import OfftargetHit
        
        hit = OfftargetHit(
            sequence_id="seq_001",
            sequence_title="Test Sequence",
            position=100,
            strand="+",
            identity=95.0,
            mismatches=1,
            gaps=0,
            evalue=1e-10,
            is_significant=True,
            risk_level="high"
        )
        
        result = hit.to_dict()
        
        assert isinstance(result, dict)
        assert result["sequence_id"] == "seq_001"
        assert result["identity"] == 95.0
        assert result["is_significant"] is True
        assert result["risk_level"] == "high"

    def test_offtarget_result_to_dict(self):
        """Test OfftargetResult.to_dict() method."""
        from primerlab.core.offtarget.finder import OfftargetResult, OfftargetHit
        
        hit = OfftargetHit(
            sequence_id="seq_001",
            sequence_title="Test",
            position=100,
            strand="+",
            identity=90.0,
            mismatches=2,
            gaps=0,
            evalue=1e-5,
        )
        
        result_obj = OfftargetResult(
            primer_id="primer_fwd",
            primer_seq="ATGCATGCATGCATGC",
            target_id="target_gene",
            on_target_found=True,
            offtarget_count=1,
            significant_offtargets=1,
            offtargets=[hit],
            specificity_score=85.0,
            warnings=["One off-target found"]
        )
        
        result = result_obj.to_dict()
        
        assert isinstance(result, dict)
        assert result["primer_id"] == "primer_fwd"
        assert result["specificity_score"] == 85.0
        assert len(result["offtargets"]) == 1
        assert result["offtargets"][0]["sequence_id"] == "seq_001"


class TestInsilicoModelSerialization:
    """Test insilico/binding.py and engine.py dataclass serialization."""

    def test_binding_site_to_dict(self):
        """Test BindingSite.to_dict() method."""
        from primerlab.core.insilico.binding import BindingSite
        
        site = BindingSite(
            position=50,
            strand="+",
            primer_seq="ATGCATGCATGCATGC",
            target_seq="ATGCATGCATGCATGC",
            match_count=16,
            mismatch_count=0,
            match_percent=100.0,
            three_prime_match=5,
            three_prime_dg=-8.5,
            five_prime_mismatch=0,
            binding_tm=62.5,
            binding_dg=-15.0,
            is_valid=True,
            validation_notes=["All requirements met"],
            alignment_str="||||||||||||||||"
        )
        
        result = site.to_dict()
        
        assert isinstance(result, dict)
        assert result["position"] == 50
        assert result["match_percent"] == 100.0
        assert result["is_valid"] is True

    def test_primer_binding_to_dict(self):
        """Test PrimerBinding.to_dict() method."""
        from primerlab.core.insilico.engine import PrimerBinding
        
        binding = PrimerBinding(
            primer_name="Forward",
            primer_seq="ATGCATGCATGCATGC",
            strand="+",
            position=0,
            match_percent=100.0,
            mismatches=0,
            three_prime_match=5,
            binding_tm=60.0,
            is_valid=True,
            alignment="||||||||||||||||"
        )
        
        result = binding.to_dict()
        
        assert isinstance(result, dict)
        assert result["primer_name"] == "Forward"
        assert result["is_valid"] is True

    def test_insilico_pcr_result_to_dict(self):
        """Test InsilicoPCRResult.to_dict() method."""
        from primerlab.core.insilico.engine import InsilicoPCRResult
        
        result_obj = InsilicoPCRResult(
            success=True,
            template_name="test_template",
            template_length=1000,
            forward_primer="ATGCATGCATGC",
            reverse_primer="GCATGCATGCAT",
            products=[],
            all_forward_bindings=[],
            all_reverse_bindings=[],
            parameters={"min_3prime_match": 3},
            warnings=[],
            errors=[]
        )
        
        result = result_obj.to_dict()
        
        assert isinstance(result, dict)
        assert result["success"] is True
        assert result["template_name"] == "test_template"


class TestConfigValidatorSerialization:
    """Test config_validator.py dataclass serialization."""

    def test_validation_error_to_dict(self):
        """Test ValidationError.to_dict() method."""
        from primerlab.core.config_validator import ValidationError
        
        error = ValidationError(
            path="offtarget.database",
            message="Database not found",
            suggestion="Check the path"
        )
        
        result = error.to_dict()
        
        assert isinstance(result, dict)
        assert result["path"] == "offtarget.database"
        assert result["message"] == "Database not found"
        assert result["suggestion"] == "Check the path"

    def test_validation_result_to_dict(self):
        """Test ValidationResult.to_dict() method."""
        from primerlab.core.config_validator import ValidationResult, ValidationError
        
        error = ValidationError(path="test", message="error", suggestion=None)
        warning = ValidationError(path="warn", message="warning", suggestion=None)
        
        result_obj = ValidationResult(
            valid=False,
            errors=[error],
            warnings=[warning]
        )
        
        result = result_obj.to_dict()
        
        assert isinstance(result, dict)
        assert result["valid"] is False
        assert len(result["errors"]) == 1
        assert len(result["warnings"]) == 1


class TestRerankingSerialization:
    """Test reranking.py dataclass serialization."""

    def test_candidate_score_to_dict(self):
        """Test CandidateScore.to_dict() method."""
        from primerlab.core.reranking import CandidateScore
        
        score = CandidateScore(
            index=0,
            primer3_penalty=0.5,
            hairpin_dg=-3.0,
            homodimer_dg=-4.0,
            passes_qc=True,
            rejection_reason=None
        )
        
        result = score.to_dict()
        
        assert isinstance(result, dict)
        assert result["index"] == 0
        assert result["primer3_penalty"] == 0.5
        assert result["passes_qc"] is True
        assert result["rejection_reason"] is None


class TestExistingModelsSerialization:
    """Test that existing models still have to_dict() working."""

    def test_multiplex_pair_to_dict(self):
        """Test MultiplexPair.to_dict() method."""
        from primerlab.core.compat_check.models import MultiplexPair
        
        pair = MultiplexPair(
            name="GAPDH",
            forward="ATGCATGCATGCATGC",
            reverse="GCATGCATGCATGCAT",
            tm_forward=60.0,
            tm_reverse=59.5,
        )
        
        result = pair.to_dict()
        
        assert isinstance(result, dict)
        assert result["name"] == "GAPDH"
        assert "avg_tm" in result

    def test_amplicon_analysis_result_to_dict(self):
        """Test AmpliconAnalysisResult.to_dict() method."""
        from primerlab.core.amplicon.models import AmpliconAnalysisResult
        
        result_obj = AmpliconAnalysisResult(
            sequence="ATGCATGCATGC",
            length=12,
        )
        
        result = result_obj.to_dict()
        
        assert isinstance(result, dict)
        assert result["sequence"] == "ATGCATGCATGC"
        assert result["length"] == 12
