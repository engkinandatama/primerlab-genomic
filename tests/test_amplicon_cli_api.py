"""
Tests for Amplicon CLI integration.

Tests the --amplicon-analysis flag in primerlab run command.
"""

import pytest
import subprocess
import tempfile
import json
from pathlib import Path


class TestAmpliconCLIFlag:
    """Tests for --amplicon-analysis CLI flag."""
    
    def test_run_help_shows_amplicon_flag(self):
        """Verify --amplicon-analysis appears in run help."""
        result = subprocess.run(
            ["python", "-m", "primerlab.cli.main", "run", "--help"],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert "--amplicon-analysis" in result.stdout
        assert "v0.4.1" in result.stdout
    
    def test_amplicon_flag_accepted(self):
        """Verify --amplicon-analysis flag is accepted without error."""
        # Create minimal config
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
workflow: pcr
input:
  sequence: "ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"
""")
            config_path = f.name
        
        try:
            # Just check flag is accepted (may fail for other reasons)
            result = subprocess.run(
                ["python", "-m", "primerlab.cli.main", "run", 
                 "--config", config_path, "--amplicon-analysis"],
                capture_output=True,
                text=True,
                timeout=60
            )
            # Flag should be accepted (no "unrecognized arguments" error)
            assert "unrecognized arguments: --amplicon-analysis" not in result.stderr
        finally:
            Path(config_path).unlink(missing_ok=True)


class TestAmpliconAPIFunction:
    """Tests for analyze_amplicon() API function."""
    
    def test_analyze_amplicon_import(self):
        """Verify analyze_amplicon can be imported from public API."""
        from primerlab.api.public import analyze_amplicon
        assert callable(analyze_amplicon)
    
    def test_analyze_amplicon_basic(self):
        """Test basic amplicon analysis via API."""
        from primerlab.api.public import analyze_amplicon
        
        sequence = "ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"
        result = analyze_amplicon(sequence)
        
        assert "length" in result
        assert "quality_score" in result
        assert "grade" in result
        assert result["length"] == len(sequence)
    
    def test_analyze_amplicon_quality_score_range(self):
        """Verify quality score is in valid range."""
        from primerlab.api.public import analyze_amplicon
        
        sequence = "ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"
        result = analyze_amplicon(sequence)
        
        assert 0 <= result["quality_score"] <= 100
        assert result["grade"] in ["A", "B", "C", "D", "F"]
    
    def test_analyze_amplicon_components(self):
        """Verify all analysis components are present."""
        from primerlab.api.public import analyze_amplicon
        
        sequence = "ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"
        result = analyze_amplicon(sequence)
        
        assert "secondary_structure" in result
        assert "gc_profile" in result
        assert "gc_clamp" in result
        assert "amplicon_tm" in result


class TestOverlapSimulationAPI:
    """Tests for run_overlap_simulation() API function."""
    
    def test_overlap_simulation_import(self):
        """Verify run_overlap_simulation can be imported."""
        from primerlab.api.public import run_overlap_simulation
        assert callable(run_overlap_simulation)
    
    def test_overlap_simulation_basic(self):
        """Test basic overlap simulation."""
        from primerlab.api.public import run_overlap_simulation
        
        template = "ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"
        
        primer_pairs = [
            {"name": "Pair1", "forward": "ATGCGATCGATCGATCGATCG", "reverse": "CGATCGATCGATCGATCGCAT"},
            {"name": "Pair2", "forward": "GATCGATCGATCGATCGATCG", "reverse": "CGATCGATCGATCGATCGATC"},
        ]
        
        result = run_overlap_simulation(template, primer_pairs)
        
        assert "template_length" in result
        assert "amplicons" in result
        assert "overlaps" in result
        assert "has_problems" in result
    
    def test_overlap_simulation_empty_pairs(self):
        """Test with empty primer pairs list."""
        from primerlab.api.public import run_overlap_simulation
        
        template = "ATGCGATCGATCGATCGATCG"
        result = run_overlap_simulation(template, [])
        
        assert result["amplicons"] == []
        assert result["overlaps"] == []
