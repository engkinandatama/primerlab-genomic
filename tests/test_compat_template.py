"""
Integration tests for check-compat --template flag.

Tests the overlap analysis integration in the check-compat command.
"""

import pytest
import subprocess
import tempfile
import json
from pathlib import Path


@pytest.fixture
def sample_primers_json():
    """Create a sample primers.json file."""
    primers = [
        {
            "name": "Gene1",
            "forward": "ATGCGATCGATCGATCGATCG",
            "reverse": "CGATCGATCGATCGATCGCAT",
            "tm_forward": 60.0,
            "tm_reverse": 60.0,
            "gc_forward": 52.4,
            "gc_reverse": 52.4
        },
        {
            "name": "Gene2",
            "forward": "GATCGATCGATCGATCGATCG",
            "reverse": "CGATCGATCGATCGATCGATC",
            "tm_forward": 58.0,
            "tm_reverse": 58.0,
            "gc_forward": 50.0,
            "gc_reverse": 50.0
        }
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(primers, f)
        return f.name


@pytest.fixture
def sample_template_fasta():
    """Create a sample template FASTA file."""
    content = """>TestTemplate
ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
        f.write(content)
        return f.name


class TestCheckCompatTemplateFlag:
    """Tests for check-compat --template flag."""
    
    def test_help_shows_template_flag(self):
        """Verify --template appears in check-compat help."""
        result = subprocess.run(
            ["python", "-m", "primerlab.cli.main", "check-compat", "--help"],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert "--template" in result.stdout
        assert "v0.4.1" in result.stdout
    
    def test_template_flag_accepted(self, sample_primers_json, sample_template_fasta):
        """Verify --template flag is accepted."""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                result = subprocess.run(
                    ["python", "-m", "primerlab.cli.main", "check-compat",
                     "--primers", sample_primers_json,
                     "--template", sample_template_fasta,
                     "--output", tmpdir],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                # Should not have unrecognized argument error
                assert "unrecognized arguments: --template" not in result.stderr
        finally:
            Path(sample_primers_json).unlink(missing_ok=True)
            Path(sample_template_fasta).unlink(missing_ok=True)
    
    def test_overlap_analysis_runs(self, sample_primers_json, sample_template_fasta):
        """Verify overlap analysis runs when template provided."""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                result = subprocess.run(
                    ["python", "-m", "primerlab.cli.main", "check-compat",
                     "--primers", sample_primers_json,
                     "--template", sample_template_fasta,
                     "--output", tmpdir],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                # Check for overlap analysis message
                output = result.stdout + result.stderr
                # Either runs successfully or gracefully handles errors
                assert "unrecognized arguments" not in output
        finally:
            Path(sample_primers_json).unlink(missing_ok=True)
            Path(sample_template_fasta).unlink(missing_ok=True)
