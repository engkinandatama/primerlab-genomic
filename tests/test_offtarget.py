"""
Tests for Off-target Detection Engine (v0.3.0)
"""

import pytest
from pathlib import Path

from primerlab.core.offtarget.finder import (
    OfftargetFinder,
    OfftargetHit,
    OfftargetResult,
    PrimerPairOfftargetResult,
    find_offtargets
)
from primerlab.core.offtarget.scorer import (
    SpecificityScorer,
    SpecificityScore,
    calculate_specificity
)
from primerlab.core.models.blast import BlastHit
from primerlab.core.tools.primer_aligner import check_alignment_availability


# Path to test database
TEST_DB_PATH = Path(__file__).parent.parent / "examples" / "blast" / "test_db.fasta"

# Check if any alignment method is available
BLAST_AVAILABLE, BIOPYTHON_AVAILABLE, _ = check_alignment_availability()
ALIGNER_AVAILABLE = BLAST_AVAILABLE or BIOPYTHON_AVAILABLE


class TestOfftargetHit:
    """Tests for OfftargetHit class."""
    
    def test_from_blast_hit_high_risk(self):
        """High identity hit should be high risk."""
        blast_hit = BlastHit(
            subject_id="seq1",
            subject_title="Test sequence",
            query_start=1, query_end=20,
            subject_start=100, subject_end=120,
            identity_percent=98.0,
            alignment_length=20,
            mismatches=0,
            gaps=0,
            evalue=1e-10,
            bit_score=50.0
        )
        
        ot = OfftargetHit.from_blast_hit(blast_hit)
        
        assert ot.risk_level == "high"
        assert ot.identity == 98.0
    
    def test_from_blast_hit_medium_risk(self):
        """Medium identity hit should be medium risk."""
        blast_hit = BlastHit(
            subject_id="seq1",
            subject_title="",
            query_start=1, query_end=20,
            subject_start=100, subject_end=120,
            identity_percent=88.0,
            alignment_length=20,
            mismatches=2,
            gaps=0,
            evalue=1e-5,
            bit_score=35.0
        )
        
        ot = OfftargetHit.from_blast_hit(blast_hit)
        
        assert ot.risk_level == "medium"
    
    def test_from_blast_hit_low_risk(self):
        """Low identity hit should be low risk."""
        blast_hit = BlastHit(
            subject_id="seq1",
            subject_title="",
            query_start=1, query_end=20,
            subject_start=100, subject_end=120,
            identity_percent=75.0,
            alignment_length=20,
            mismatches=5,
            gaps=0,
            evalue=1e-2,
            bit_score=20.0
        )
        
        ot = OfftargetHit.from_blast_hit(blast_hit)
        
        assert ot.risk_level == "low"


class TestOfftargetFinder:
    """Tests for OfftargetFinder."""
    
    @pytest.mark.skipif(not TEST_DB_PATH.exists(), reason="Test DB not found")
    @pytest.mark.skipif(not ALIGNER_AVAILABLE, reason="No aligner available")
    def test_finder_initialization(self):
        """Finder should initialize with database."""
        finder = OfftargetFinder(database=str(TEST_DB_PATH))
        assert finder.database == str(TEST_DB_PATH)
    
    @pytest.mark.skipif(not TEST_DB_PATH.exists(), reason="Test DB not found")
    @pytest.mark.skipif(not ALIGNER_AVAILABLE, reason="No aligner available")
    def test_find_offtargets(self):
        """Should find off-targets in database."""
        finder = OfftargetFinder(
            database=str(TEST_DB_PATH),
            target_id="NC_000913.3_partial"  # Our target
        )
        
        # Use a primer that might match multiple sequences
        result = finder.find_offtargets(
            primer_seq="ATGACCATGATTACGGATTC",  # Generic primer
            primer_id="test_primer"
        )
        
        assert isinstance(result, OfftargetResult)
        assert result.primer_id == "test_primer"
        assert 0 <= result.specificity_score <= 100
    
    @pytest.mark.skipif(not TEST_DB_PATH.exists(), reason="Test DB not found")
    @pytest.mark.skipif(not ALIGNER_AVAILABLE, reason="No aligner available")
    def test_find_primer_pair_offtargets(self):
        """Should analyze primer pair."""
        finder = OfftargetFinder(database=str(TEST_DB_PATH))
        
        result = finder.find_primer_pair_offtargets(
            forward_primer="ATGACCATGATTACGGATTC",
            reverse_primer="GCAACTGTTGGGAAGGGCGA"
        )
        
        assert isinstance(result, PrimerPairOfftargetResult)
        assert 0 <= result.combined_score <= 100


class TestSpecificityScorer:
    """Tests for SpecificityScorer."""
    
    def test_score_no_offtargets(self):
        """No off-targets should give perfect score."""
        result = OfftargetResult(
            primer_id="test",
            primer_seq="ATGC",
            offtargets=[]
        )
        
        scorer = SpecificityScorer()
        score = scorer.score_primer(result)
        
        assert score.overall_score == 100.0
        assert score.grade == "A"
        assert score.is_acceptable
    
    def test_score_with_high_risk_offtargets(self):
        """High risk off-targets should lower score."""
        offtargets = [
            OfftargetHit(
                sequence_id="seq1",
                sequence_title="",
                position=100,
                strand="+",
                identity=98.0,
                mismatches=0,
                gaps=0,
                evalue=1e-10,
                is_significant=True,
                risk_level="high"
            )
        ]
        
        result = OfftargetResult(
            primer_id="test",
            primer_seq="ATGC",
            offtargets=offtargets,
            offtarget_count=1,
            significant_offtargets=1
        )
        
        scorer = SpecificityScorer()
        score = scorer.score_primer(result)
        
        assert score.overall_score < 100.0
        assert score.details["high_risk_count"] == 1
    
    def test_calculate_specificity_function(self):
        """Convenience function should work."""
        result = OfftargetResult(
            primer_id="test",
            primer_seq="ATGC"
        )
        
        score = calculate_specificity(result)
        
        assert isinstance(score, SpecificityScore)


class TestFindOfftargetsFunction:
    """Tests for convenience function."""
    
    @pytest.mark.skipif(not TEST_DB_PATH.exists(), reason="Test DB not found")
    @pytest.mark.skipif(not ALIGNER_AVAILABLE, reason="No aligner available")
    def test_find_offtargets_function(self):
        """Convenience function should work."""
        result = find_offtargets(
            primer_seq="ATGACCATGATTACG",
            database=str(TEST_DB_PATH)
        )
        
        assert isinstance(result, OfftargetResult)
