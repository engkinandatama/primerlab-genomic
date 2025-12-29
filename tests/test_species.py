"""
Tests for Species-Specific Analysis Module.
"""

import pytest
import tempfile
from pathlib import Path

from primerlab.core.species import (
    SpeciesTemplate,
    BindingSite,
    SpeciesBinding,
    SpecificityMatrix,
    parse_fasta,
    load_species_template,
    load_multi_fasta,
    find_binding_sites,
    calculate_match_percent,
    reverse_complement,
    analyze_primer_binding,
    check_species_specificity,
)


class TestModels:
    """Tests for species data models."""
    
    def test_species_template_creation(self):
        """Test SpeciesTemplate dataclass."""
        template = SpeciesTemplate(
            species_name="E.coli",
            sequence="ATGCGATCG",
            description="Test template"
        )
        assert template.species_name == "E.coli"
        assert template.length == 9
    
    def test_binding_site_strong_binding(self):
        """Test BindingSite strong binding threshold."""
        strong = BindingSite(position=100, strand='+', match_percent=85.0, mismatches=2)
        weak = BindingSite(position=200, strand='-', match_percent=70.0, mismatches=5)
        
        assert strong.is_strong_binding is True
        assert weak.is_strong_binding is False


class TestFastaLoader:
    """Tests for FASTA loading functions."""
    
    def test_parse_fasta_single(self):
        """Test parsing single sequence FASTA."""
        content = ">seq1 Test sequence\nATGCGATCGATCG\nATCGATCGATCG"
        result = parse_fasta(content)
        
        assert len(result) == 1
        assert result[0][0] == "seq1"
        assert result[0][1] == "ATGCGATCGATCGATCGATCGATCG"
    
    def test_parse_fasta_multi(self):
        """Test parsing multi-sequence FASTA."""
        content = ">species1\nATGCGATC\n>species2\nGATCGATC"
        result = parse_fasta(content)
        
        assert len(result) == 2
        assert result[0][0] == "species1"
        assert result[1][0] == "species2"
    
    def test_load_species_template(self):
        """Test loading template from file."""
        content = ">TestSpecies Description here\nATGCGATCGATCGATCGATCG"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            f.write(content)
            path = f.name
        
        try:
            template = load_species_template(path, "CustomName")
            assert template.species_name == "CustomName"
            assert template.length == 21
        finally:
            Path(path).unlink(missing_ok=True)


class TestAlignment:
    """Tests for alignment functions."""
    
    def test_reverse_complement(self):
        """Test reverse complement calculation."""
        assert reverse_complement("ATGC") == "GCAT"
        assert reverse_complement("AAAA") == "TTTT"
    
    def test_calculate_match_percent_perfect(self):
        """Test 100% match."""
        pct, mm, pos = calculate_match_percent("ATGC", "ATGC")
        assert pct == 100.0
        assert mm == 0
    
    def test_calculate_match_percent_partial(self):
        """Test partial match."""
        pct, mm, pos = calculate_match_percent("ATGC", "ATGG")
        assert pct == 75.0
        assert mm == 1
        assert 3 in pos
    
    def test_find_binding_sites(self):
        """Test finding binding sites on template."""
        template = "ATGCGATCGATCGATCGATCGATCGATCGATCGATCG"
        primer = "ATCGATCG"
        
        sites = find_binding_sites(primer, template, min_match_percent=80.0)
        assert len(sites) > 0
        # Perfect match should have 100%
        assert any(s[2] == 100.0 for s in sites)


class TestBinding:
    """Tests for binding analysis."""
    
    def test_analyze_primer_binding(self):
        """Test primer binding analysis on template."""
        template = SpeciesTemplate(
            species_name="TestSpecies",
            sequence="ATGCGATCGATCGATCGATCGATCGATCG"
        )
        
        binding = analyze_primer_binding(
            "TestPrimer",
            "ATCGATCG",
            template,
            min_match_percent=80.0
        )
        
        assert binding.species_name == "TestSpecies"
        assert binding.has_binding is True
    
    def test_check_species_specificity(self):
        """Test full specificity check."""
        target = SpeciesTemplate("Target", "ATGCGATCGATCGATCGATCGATCGATCG")
        offtarget = {"Other": SpeciesTemplate("Other", "NNNNNNNNNNNNNNNNNNNNNNNN")}
        
        primers = [{"name": "Primer1", "forward": "ATCGATCG", "reverse": "CGATCGAT"}]
        
        result = check_species_specificity(primers, target, offtarget)
        
        assert result.target_species == "Target"
        assert result.primers_checked == 1
        assert result.grade in ["A", "B", "C", "D", "F"]
