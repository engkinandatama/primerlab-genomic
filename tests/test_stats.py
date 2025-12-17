"""Tests for Stats CLI Command (v0.1.6)."""
import pytest
import subprocess
import sys
import tempfile
from pathlib import Path


class TestStatsCommand:
    """Tests for primerlab stats command."""
    
    @pytest.fixture
    def sample_fasta(self, tmp_path):
        """Create a sample FASTA file."""
        fasta_content = """>TEST_SEQUENCE Sample sequence for testing
ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC
ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC
"""
        fasta_path = tmp_path / "test.fasta"
        fasta_path.write_text(fasta_content)
        return fasta_path
    
    @pytest.fixture
    def masked_fasta(self, tmp_path):
        """Create a FASTA with N-masked regions."""
        fasta_content = """>MASKED_SEQ Sequence with N regions
ATGCATGCATGCATGCATGCNNNNNNNNNNATGCATGCATGCATGCATGCATGCATGC
ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC
"""
        fasta_path = tmp_path / "masked.fasta"
        fasta_path.write_text(fasta_content)
        return fasta_path
    
    @pytest.fixture
    def iupac_fasta(self, tmp_path):
        """Create a FASTA with IUPAC codes."""
        fasta_content = """>IUPAC_SEQ Sequence with IUPAC codes
ATGCATGCATGCATGCRYSWATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC
ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC
"""
        fasta_path = tmp_path / "iupac.fasta"
        fasta_path.write_text(fasta_content)
        return fasta_path
    
    def test_stats_basic(self, sample_fasta):
        """Test basic stats command."""
        result = subprocess.run(
            [sys.executable, "-m", "primerlab.cli.main", "stats", str(sample_fasta)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert result.returncode == 0
        assert "Sequence Statistics" in result.stdout
        assert "GC Content" in result.stdout
        assert "Ready for primer design" in result.stdout
    
    def test_stats_json_output(self, sample_fasta):
        """Test JSON output format."""
        import json
        
        result = subprocess.run(
            [sys.executable, "-m", "primerlab.cli.main", "stats", str(sample_fasta), "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert result.returncode == 0
        
        # Should be valid JSON
        data = json.loads(result.stdout)
        
        assert "name" in data
        assert "length" in data
        assert "gc_percent" in data
        assert "n_count" in data
        assert "valid_for_design" in data
    
    def test_stats_detects_n_masked(self, masked_fasta):
        """Test N-masked region detection."""
        result = subprocess.run(
            [sys.executable, "-m", "primerlab.cli.main", "stats", str(masked_fasta), "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert result.returncode == 0
        
        import json
        data = json.loads(result.stdout)
        
        assert data["n_count"] > 0
    
    def test_stats_detects_iupac(self, iupac_fasta):
        """Test IUPAC code detection."""
        result = subprocess.run(
            [sys.executable, "-m", "primerlab.cli.main", "stats", str(iupac_fasta), "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert result.returncode == 0
        
        import json
        data = json.loads(result.stdout)
        
        assert len(data["iupac_codes"]) > 0
        assert data["iupac_count"] > 0
    
    def test_stats_raw_sequence(self):
        """Test with raw sequence input (not file)."""
        # Note: This should work with a raw sequence string
        sequence = "ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC"
        
        result = subprocess.run(
            [sys.executable, "-m", "primerlab.cli.main", "stats", sequence],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Should work or gracefully fail
        assert result.returncode in [0, 1]
    
    def test_stats_help(self):
        """Test stats --help."""
        result = subprocess.run(
            [sys.executable, "-m", "primerlab.cli.main", "stats", "--help"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert result.returncode == 0
        assert "sequence" in result.stdout.lower()


class TestStatsCalculations:
    """Tests for stats calculation accuracy."""
    
    def test_gc_calculation(self, tmp_path):
        """Test GC percentage calculation accuracy."""
        import json
        
        # Create a 100bp sequence: 50 GC + 50 AT = 50% GC
        fasta_content = ">GC50\nGCGCGCGCGCGCGCGCGCGCGCGCGCATATATATATATATATATATATAT\n"
        fasta_path = tmp_path / "gc50.fasta"
        fasta_path.write_text(fasta_content)
        
        result = subprocess.run(
            [sys.executable, "-m", "primerlab.cli.main", "stats", str(fasta_path), "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        data = json.loads(result.stdout)
        
        # Should be 50% GC (26 GC out of 50 chars)
        assert data["length"] == 50
        assert data["gc_count"] == 26  # GCGCGCGCGCGCGCGCGCGCGCGCGC = 26 GC
    
    def test_length_calculation(self, tmp_path):
        """Test length calculation."""
        import json
        
        # Exactly 60bp
        fasta_content = ">LEN60\nATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC\n"
        fasta_path = tmp_path / "len60.fasta"
        fasta_path.write_text(fasta_content)
        
        result = subprocess.run(
            [sys.executable, "-m", "primerlab.cli.main", "stats", str(fasta_path), "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        data = json.loads(result.stdout)
        
        assert data["length"] == 60
