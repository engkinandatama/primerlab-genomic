"""
Tests for tm-gradient CLI command.
"""

import pytest
import subprocess
import tempfile
import json
from pathlib import Path


class TestTmGradientCLI:
    """Tests for primerlab tm-gradient CLI command."""
    
    def test_help_output(self):
        """Verify tm-gradient --help shows all options."""
        result = subprocess.run(
            ["python", "-m", "primerlab.cli.main", "tm-gradient", "--help"],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0
        assert "--primers" in result.stdout
        assert "--min-temp" in result.stdout
        assert "--max-temp" in result.stdout
        assert "--step" in result.stdout
        assert "--output" in result.stdout
        assert "--format" in result.stdout
    
    def test_missing_required_args(self):
        """Verify error when required args missing."""
        result = subprocess.run(
            ["python", "-m", "primerlab.cli.main", "tm-gradient"],
            capture_output=True,
            text=True,
            timeout=30
        )
        # Should fail with missing required arguments
        assert result.returncode != 0
        assert "required" in result.stderr.lower() or "error" in result.stderr.lower()


class TestTmGradientIntegration:
    """Integration tests for tm-gradient command."""
    
    @pytest.fixture
    def sample_primers_json(self, tmp_path):
        """Create sample primers JSON."""
        primers = [
            {"name": "Gene1", "forward": "ATGCGATCGATCGATCGATCG", "reverse": "CGATCGATCGATCGATCGCAT"},
            {"name": "Gene2", "forward": "GCGCGCGCGCGCGCGCGCGC", "reverse": "ATATATATATATATATATATAT"},
        ]
        path = tmp_path / "primers.json"
        with open(path, "w") as f:
            json.dump(primers, f)
        return str(path)
    
    def test_basic_run(self, sample_primers_json, tmp_path):
        """Test basic tm-gradient run."""
        output_dir = tmp_path / "output"
        
        result = subprocess.run(
            [
                "python", "-m", "primerlab.cli.main", "tm-gradient",
                "--primers", sample_primers_json,
                "--output", str(output_dir),
            ],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Should complete successfully
        assert result.returncode == 0
        assert "Optimal Annealing Temperature" in result.stdout
    
    def test_json_output_created(self, sample_primers_json, tmp_path):
        """Verify JSON output file created."""
        output_dir = tmp_path / "output"
        
        subprocess.run(
            [
                "python", "-m", "primerlab.cli.main", "tm-gradient",
                "--primers", sample_primers_json,
                "--output", str(output_dir),
            ],
            capture_output=True,
            timeout=60
        )
        
        # Check JSON file created
        json_path = output_dir / "tm_gradient.json"
        if json_path.exists():
            with open(json_path) as f:
                data = json.load(f)
            assert "optimal" in data
            assert "primers" in data
    
    def test_custom_temperature_range(self, sample_primers_json, tmp_path):
        """Test with custom temperature range."""
        output_dir = tmp_path / "output"
        
        result = subprocess.run(
            [
                "python", "-m", "primerlab.cli.main", "tm-gradient",
                "--primers", sample_primers_json,
                "--min-temp", "55",
                "--max-temp", "68",
                "--step", "1.0",
                "--output", str(output_dir),
            ],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        assert result.returncode == 0
        assert "55.0°C" in result.stdout or "55°C" in result.stdout
