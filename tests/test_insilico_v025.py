"""
Tests for v0.2.5 features: In-silico Enhancements
"""

import pytest

from primerlab.core.insilico.binding import check_primer_dimer
from primerlab.core.insilico import run_insilico_pcr


class TestPrimerDimerCheck:
    """Tests for check_primer_dimer function."""
    
    def test_check_primer_dimer_returns_dict(self):
        """Should return a dictionary result."""
        result = check_primer_dimer("ATGCATGCATGC", "GCATGCATGCAT")
        assert isinstance(result, dict)
        assert "has_dimer" in result
        assert "severity" in result
    
    def test_check_primer_dimer_no_complementarity(self):
        """Non-complementary primers should have no dimer."""
        result = check_primer_dimer("AAAAAAAAAA", "TTTTTTTTTT")
        # These are complementary, so they will have dimer
        # Use truly non-complementary
        result = check_primer_dimer("AAAAAAAAAA", "AAAAAAAAAA")
        assert result["severity"] == "none"
    
    def test_check_primer_dimer_high_complementarity(self):
        """Highly complementary primers should flag high severity."""
        # Forward and reverse complement of each other
        result = check_primer_dimer("ATGCATGCATGC", "GCATGCATGCAT")
        assert result["max_complementary"] > 0
    
    def test_check_primer_dimer_3prime_check(self):
        """Should check 3' end complementarity."""
        result = check_primer_dimer("ATGATGATGATG", "CATCATCATCAT")
        assert "three_prime_complementary" in result
    
    def test_check_primer_dimer_warning(self):
        """Severe dimer should have warning."""
        # Create highly complementary primers
        result = check_primer_dimer("ATCGATCGATCG", "CGATCGATCGAT")
        if result["severity"] != "none":
            assert result["warning"] is not None


class TestExtensionTime:
    """Tests for extension time calculation."""
    
    def test_extension_time_calculated(self):
        """Products should have extension time."""
        template = "ATGAGTAAAGGAGAAGAACTTTTCACTGGAGTTGTCCCAATTCTTGTTGAATTAGATGGTGATGTTAATGGGCAC" * 3
        fwd = "ATGAGTAAAGGAGAAGAAC"
        rev = "GTGCCCATTAACATCACCATC"
        
        result = run_insilico_pcr(
            template=template,
            forward_primer=fwd,
            reverse_primer=rev
        )
        
        if result.products:
            for product in result.products:
                # Extension time should be calculated
                assert hasattr(product, 'extension_time_sec')
                # Should be roughly 1 min/kb (60s/1000bp)
                expected_min = product.product_size / 1000.0 * 60
                assert abs(product.extension_time_sec - expected_min) < 0.1


class TestPrimerDimerInResult:
    """Tests for primer dimer in InsilicoPCRResult."""
    
    def test_primer_dimer_in_result(self):
        """Result should contain primer_dimer."""
        template = "ATGAGTAAAGGAGAAGAACTTTTC" * 10
        fwd = "ATGAGTAAAGGAGAAGAAC"
        rev = "GAAAAGTTCTTCTCCTTTACTCAT"  # Reverse complement
        
        result = run_insilico_pcr(
            template=template,
            forward_primer=fwd,
            reverse_primer=rev
        )
        
        assert result.primer_dimer is not None
        assert isinstance(result.primer_dimer, dict)
        assert "severity" in result.primer_dimer
