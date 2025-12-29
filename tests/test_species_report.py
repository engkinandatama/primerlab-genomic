"""
Unit tests for species report module.
"""

import pytest
import tempfile
import json
from pathlib import Path

from primerlab.core.species import (
    SpeciesTemplate,
    SpecificityMatrix,
    SpeciesCheckResult,
)
from primerlab.core.species.report import (
    generate_species_json_report,
    generate_species_markdown_report,
    generate_species_html_report,
)


@pytest.fixture
def sample_result():
    """Create sample SpeciesCheckResult."""
    matrix = SpecificityMatrix(
        primer_names=["P1_fwd", "P1_rev"],
        species_names=["Human", "Mouse"],
        target_species="Human",
        bindings={}
    )
    
    return SpeciesCheckResult(
        target_species="Human",
        primers_checked=1,
        species_checked=2,
        specificity_matrix=matrix,
        overall_score=85.0,
        grade="B",
        is_specific=True,
        warnings=["Test warning"],
        recommendations=["Test recommendation"]
    )


class TestJSONReport:
    """Tests for JSON report generation."""
    
    def test_json_report_created(self, sample_result):
        """Test JSON report file creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = generate_species_json_report(sample_result, tmpdir)
            
            assert Path(path).exists()
            assert path.endswith(".json")
    
    def test_json_report_content(self, sample_result):
        """Test JSON report content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = generate_species_json_report(sample_result, tmpdir)
            
            with open(path) as f:
                data = json.load(f)
            
            assert data["target_species"] == "Human"
            assert data["overall_score"] == 85.0
            assert data["grade"] == "B"


class TestMarkdownReport:
    """Tests for Markdown report generation."""
    
    def test_markdown_report_created(self, sample_result):
        """Test Markdown report file creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = generate_species_markdown_report(sample_result, tmpdir)
            
            assert Path(path).exists()
            assert path.endswith(".md")
    
    def test_markdown_report_content(self, sample_result):
        """Test Markdown report content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = generate_species_markdown_report(sample_result, tmpdir)
            
            content = Path(path).read_text()
            
            assert "Species Specificity Report" in content
            assert "85.0/100" in content
            assert "Human" in content
            assert "Test warning" in content


class TestHTMLReport:
    """Tests for HTML report generation."""
    
    def test_html_report_created(self, sample_result):
        """Test HTML report file creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = generate_species_html_report(sample_result, tmpdir)
            
            assert Path(path).exists()
            assert path.endswith(".html")
    
    def test_html_report_content(self, sample_result):
        """Test HTML report contains key elements."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = generate_species_html_report(sample_result, tmpdir)
            
            content = Path(path).read_text()
            
            assert "<!DOCTYPE html>" in content
            assert "Species Specificity Report" in content
            assert "Human" in content
            assert "85" in content  # Score
            assert "class=\"card\"" in content  # Has styling
